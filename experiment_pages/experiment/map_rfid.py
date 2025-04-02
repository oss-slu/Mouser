'''Map RFID module.'''
import time
from tkinter import Menu
from tkinter.ttk import Style, Treeview
import tkinter.font as tkfont
import random
import threading
import webbrowser
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from playsound import playsound
from serial import serialutil
from shared.tk_models import *
from shared.serial_port_controller import SerialPortController
from shared.serial_handler import SerialDataHandler

from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager

import shared.file_utils as file_utils

def get_random_rfid():
    '''Returns a simulated rfid number'''
    return random.randint(1000000000, 9999999999)

def play_sound_async(filename):
    '''Plays the given filename.'''
    threading.Thread(target=playsound, args=(filename,), daemon=True).start()

class MapRFIDPage(MouserPage):# pylint: disable= undefined-variable
    '''Map RFID user interface and window.'''
    def __init__(self, database, parent: CTk, previous_page: CTkFrame = None, file_path = ""):

        super().__init__(parent, "Map RFID", previous_page)

        self.rfid_reader = None
        self.rfid_stop_event = threading.Event()  # Event to stop RFID listener
        self.rfid_thread = None # Store running thread

        # Store the parent reference
        self.parent = parent

        file = database
        self.db = ExperimentDatabase(file)

        self.animal_rfid_list = []
        self.animals = []
        self.animal_id = 1

        self.animal_id_entry_text = StringVar(value="1")

        # Simulate All RFID Button
        simulate_all_rfid_button = CTkButton(self, text="Simulate ALL RFID", compound=TOP,
                                      width=250, height=75, font=("Georgia", 65), command=self.simulate_all_rfid)
        simulate_all_rfid_button.place(relx=0.80, rely=0.15, anchor=CENTER)



        self.start_rfid = CTkButton(self, text="Start Scanning", compound=TOP,
                                         width=250, height=75, font=("Georgia", 65), command=self.rfid_listen)
        self.start_rfid.place(relx=0.45, rely=0.15, anchor=CENTER)
        if self.db.experiment_uses_rfid == 0:
            self.start_rfid.configure(state="disabled")

        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.15, rely=0.30, relheight=0.40, relwidth=0.80)
        self.table_frame.grid_columnconfigure(0, weight= 1)
        self.table_frame.grid_rowconfigure(0, weight= 1)

        self.file_path = file_path

        heading_style = Style()
        heading_style.configure("Treeview.Heading", font=('Arial', 10))

        columns = ('animal_id', 'rfid')
        self.table = Treeview(
            self.table_frame, columns=columns, show='headings', height=10, style='column.Treeview')

        self.table.heading('animal_id', text='Animal ID')
        self.table.heading('rfid', text='RFID')

        self.table.grid(row=0, column=0, sticky='nsew')
        self.table.grid_columnconfigure(0, weight = 1)
        self.table.grid_rowconfigure(0, weight = 1)


        scrollbar = CTkScrollbar(self.table_frame, orientation=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        self.right_click = Menu(self, tearoff=0)
        self.right_click.add_command(
            label="Remove Selection(s)", command=self.remove_selected_items)
        self.table.bind("<Button-3>", self.right_click_menu)

        self.delete_button = CTkButton(self, text="Remove Selection(s)", compound=TOP,
                                       width=250, height=75, font=("Georgia", 65), command=self.remove_selected_items,
                                       state="normal")  # Initialize button as disabled
        self.delete_button.place(relx=0.45, rely=0.80, anchor=CENTER)

        # Add Sacrifice button with normal state
        self.sacrifice_button = CTkButton(self, text="Sacrifice Selected", compound=TOP,
                                      width=250, height=75, font=("Georgia", 65), command=self.sacrifice_selected_items,
                                      state="normal")  # Initialize as enabled
        self.sacrifice_button.place(relx=0.80, rely=0.80, anchor=CENTER)

        self.item_selected(None)

        animals_setup = self.db.get_all_animal_ids()
        for animal in animals_setup:
            rfid = self.db.get_animal_rfid(animal)
            value = (int(animal), rfid)
            self.table.tag_configure('text_font', font=('Arial', 25))
            self.table.insert('', END, values=value, tags='text_font')
            self.animals.append(value)
            self.animal_id_entry_text.set(animal)

        ##setting previous button behavior
        self.menu_button = None
        self.set_menu_button(previous_page)
        self.menu_page = previous_page

        self.menu_button.configure(command = self.press_back_to_menu_button)
        self.scroll_to_latest_entry()

    def rfid_listen(self):
        """Starts RFID listener, ensuring the previous session is fully closed before restarting."""

        # Ensure old listener is properly stopped before starting a new one
        if self.rfid_thread and self.rfid_thread.is_alive():
            print("⚠️ Stopping stale RFID listener before restarting...")
            self.stop_listening()
            time.sleep(0.5)  # Allow OS to release the port

        print("📡 Starting a fresh RFID listener...")
        print("RFIDs already scanned: ", self.animal_rfid_list)
        self.rfid_stop_event.clear()  # Reset the stop flag

        def listen():
            try:
                local_db = ExperimentDatabase(self.db.db_file)
                self.rfid_reader = SerialDataHandler("reader")  # Store reference to close later
                self.rfid_reader.start()
                print("🔄 RFID Reader Started!")

                last_rfid = None  # Track last scanned RFID to avoid duplicate reads

                while not self.rfid_stop_event.is_set():
                    received_rfid = self.rfid_reader.get_stored_data()

                    if not received_rfid or received_rfid == last_rfid:
                        time.sleep(0.5)
                        continue

                    last_rfid = received_rfid
                    print(f"📡 RFID Scanned: {received_rfid}")

                    clean_rfid = received_rfid.strip().replace("\x02", "").replace("\x03", "")

                    if not clean_rfid:
                        print("⚠️ Empty or invalid RFID detected, skipping...")
                        continue  # 🚫 Avoid calling add_value()

                    if clean_rfid in self.animal_rfid_list:
                        print(f"⚠️ RFID {clean_rfid} is already in use! Skipping...")
                        play_sound_async("shared/sounds/error.wav")
                        continue  # 🚫 Avoid calling add_value()

                    # If it's a new RFID, process it
                    self.after(0, lambda: self.add_value(clean_rfid))
                    self.animal_rfid_list.append(clean_rfid)
                    play_sound_async("shared/sounds/rfid_success.wav")

            except Exception as e:
                print(f"❌ Error in RFID listener: {e}")

            finally:
                print("🛑 RFID listener has stopped.")
                if self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader = None  # Ensure cleanup

        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    def stop_listening(self):
        """Stops the RFID listener thread and ensures the serial port is released."""
        if self.rfid_stop_event.is_set():
            return  # If already stopped, do nothing

        print("⛔ Stopping RFID scanning...")
        self.rfid_stop_event.set()  # Stop the listener loop

        if self.rfid_thread and self.rfid_thread.is_alive():
            self.rfid_thread.join(timeout=1)  # Ensure the thread fully stops

        if self.rfid_reader:  # Make sure the serial reader is released
            try:
                print("🔌 Closing serial connection...")
                self.rfid_reader.stop()
                self.rfid_reader = None  # Reset the reader instance
            except Exception as e:
                print(f"⚠️ Error closing serial port: {e}")

        time.sleep(0.5)  # Allow OS to release the port

    def simulate_all_rfid(self):
        '''Simulates RFID for all remaining unmapped animals.'''
        total_needed = self.db.get_total_number_animals()
        current_count = len(self.db.get_animals())

        print(f"Simulating RFIDs: {current_count} mapped, {total_needed} total needed")

        if current_count >= total_needed:
            self.raise_warning()
            return

        while current_count < total_needed:
            self.add_random_rfid()
            current_count = len(self.db.get_animals())
            # Force UI update
            self.update()
            self.scroll_to_latest_entry()


    def scroll_to_latest_entry(self):
        '''Scrolls to the latest entry in the rfid table.'''
        self.table.yview_moveto(1)

    def right_click_menu(self, event):
        '''Opens right-click menu.'''
        if len(self.table.selection()) != 0:
            try:
                self.right_click.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click.grab_release()

    def add_random_rfid(self):
        '''Adds a random rfid value to the next animal.'''
        active_animals = len(self.db.get_animals())
        if active_animals >= self.db.get_total_number_animals():
            self.raise_warning()
            return

        # Generate a unique RFID
        rfid = get_random_rfid()
        while str(rfid) in [str(animal[1]) for animal in self.animals]:  # Ensure unique RFID
            rfid = get_random_rfid()

        # Get the next animal ID
        animal_id = self.get_next_animal()

        # Find next available group
        group_id = self.db.find_next_available_group()

        # Add to database
        self.db.add_animal(animal_id, rfid, group_id, '')
        self.db._conn.commit()

        # Add to UI table
        self.table.insert('', END, values=(animal_id, rfid), tags='text_font')
        self.animals.append((animal_id, rfid))

        # Update entry text
        self.change_entry_text()


    def add_value(self, rfid):
        """Adds RFID to the table, stops listening, checks the count, then restarts or stops."""

        if rfid is None or rfid == "":
            print("🚫 Skipping None/Empty RFID value... No entry will be added.")
            return  # ✅ Prevents adding a blank entry

        item_id = self.animal_id

        # Find appropriate group with available space
        current_group = 1
        while True:
            # Get cage capacity for current group
            cage_capacity = self.db.get_cage_capacity(current_group)

            # Get current number of animals in group
            group_count = self.db.get_group_animal_count(current_group)

            # If current group has space, use it
            if group_count < cage_capacity:
                break

            # Otherwise, try next group
            current_group += 1

        # Add to table
        self.table.insert('', item_id-1, values=(item_id, rfid), tags='text_font')
        self.animals.insert(item_id-1, (item_id, rfid))
        self.change_entry_text()

        # Add to database with determined group
        self.db.add_animal(item_id, rfid, current_group, '')
        self.db._conn.commit()

        AudioManager.play("shared/sounds/rfid_success.wav")

        # Stop listening before checking conditions
        self.stop_listening()

        total_scanned = len(self.db.get_animals())  # Get count of scanned RFIDs
        total_expected = db.get_number_animals()  # Expected count from DB

        print(f"✅ Scanned: {total_scanned} / Expected: {total_expected}")

        # Restart scanning if more animals need to be scanned
        if total_scanned < total_expected:
            print("🔄 Restarting RFID listening...")
            self.rfid_listen()
        else:
            print("🎉 All animals have been mapped to RFIDs! RFID scanning completed.")
            print("RFIDs scanned: ", self.db.get_all_animals_rfid())
            self.stop_listening()



    def change_selected_value(self, rfid):
        '''Changes the selected rfid value.'''
        item = self.table.item(self.changing_value)
        self.table.item(self.changing_value, values=(
            item['values'][0], rfid))
        self.change_rfid_button["state"] = "normal"


        AudioManager.play("shared/sounds/rfid_success.wav")

    def item_selected(self, _):
        selected = self.table.selection()
        print("Selection ", selected, " changed.")

        # Check if any selected item starts with 'I00'
        enable_button = any(self.table.item(item_id, 'values')[0].startswith('I00') for item_id in selected)

        if enable_button:
            self.delete_button["state"] = "normal"
        else:
            self.delete_button["state"] = "disabled"

    def remove_selected_items(self):
        '''Removes the selected item from a table, warning if none selected.'''
        selected_items = self.table.selection()

        # Check if any items are selected
        if not selected_items:  # If no items are selected
            self.raise_warning("No item selected. Please select an item to remove.")
            return

        for item in selected_items:
            item_id = int(self.table.item(item, 'values')[0])
            self.table.selection_remove(item)
            self.table.delete(item)
            self.db.remove_animal(item_id)
            print("Total number of animal rows in the table:", len(self.table.get_children()))

        self.change_entry_text()

    def change_entry_text(self):
        '''Changes entry text for the table.'''
        # Update entry text after removal
        if self.animals:
            next_animal = self.get_next_animal()
            self.animal_id_entry_text.set(str(next_animal))
            self.animal_id = next_animal
        else:
            self.animal_id_entry_text.set("1")
            self.animal_id = 1

    def get_next_animal(self):
        '''returns the next animal in our experiment.'''
        total_animals = self.db.get_total_number_animals()
        # Get list of existing ACTIVE animal IDs from the database
        existing_animal_ids = set(self.db.get_all_animals())

        # Find the first gap in the sequence
        for animal_id in range(1, total_animals + 1):
            if animal_id not in existing_animal_ids:
                return animal_id

        return total_animals + 1

    def open_serial_port_selection(self):
        '''Opens serial port selection.'''
        #self.serial_port_button["state"] = "disabled"
        self.serial_port_panel.open()

    def raise_warning(self, warning_message = 'Maximum number of animals reached'):
        '''Raises an error window.'''

        message = CTk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(False, False)

        label = CTkLabel(message, text= warning_message)
        label.grid(row=0, column=0, padx=10, pady=10)


        ok_button = CTkButton(message, text="OK", width=10,
                        command= lambda: [message.destroy()])
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        AudioManager.play("shared/sounds/error.wav")

        message.mainloop()

    def update(self):
        """Updates the table view to match the database state."""
        # Clear existing table entries
        for item in self.table.get_children():
            self.table.delete(item)

        # Clear existing animals list
        self.animals.clear()

        # Fetch all active animals from database
        animals_setup = self.db.get_all_animal_ids()

        # Rebuild table with fresh data
        for animal in animals_setup:
            rfid = self.db.get_animal_rfid(animal)
            value = (int(animal), rfid)
            self.table.tag_configure('text_font', font=('Arial', 25))
            self.table.insert('', END, values=value, tags='text_font')
            self.animals.append(value)

        # Update the animal ID entry text
        if animals_setup:
            self.animal_id_entry_text.set(str(self.get_next_animal()))
        else:
            self.animal_id_entry_text.set("1")

        # Scroll to show the latest entry
        self.scroll_to_latest_entry()

    def press_back_to_menu_button(self):
        '''Handles back to menu button press.'''
        print("Animals mapped: ", len(self.db.get_all_animals_rfid()), "\n")
        print("Animals needed: ", self.db.get_total_number_animals())
        if len(self.db.get_all_animals_rfid()) != self.db.get_total_number_animals():
            self.raise_warning('Not all animals have been mapped to RFIDs')
        else:
            try:
                # Save the current state before cleaning up
                current_file = self.db.db_file
                
                # Ensure all changes are committed
                self.db._conn.commit()
                print("Changes committed")
                
                # Save back to original file location
                print(f"Saving {current_file} to {self.file_path}")
                file_utils.save_temp_to_file(current_file, self.file_path)
                print("Save successful!")

                # Close the database connection
                self.db.close()  # This will now handle the singleton cleanup

                self.stop_listening()

                # Local import to avoid circular dependency
                from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI

                # Create new ExperimentMenuUI instance with the same file
                new_page = ExperimentMenuUI(self.parent, self.file_path, self.menu_page)
                new_page.raise_frame()
                
            except Exception as e:
                print(f"Error during save and cleanup: {e}")
                import traceback
                print(f"Full traceback: {traceback.format_exc()}")


    def close_connection(self):
        '''Closes database file.'''
        self.db.close()

    def sacrifice_selected_items(self):
        '''Decreases the maximum number of animals in the experiment by 1'''
        selected_items = self.table.selection()

        if not selected_items:
            self.raise_warning("No items selected. Please select animals to sacrifice.")
            return

        # First mark the selected animals as inactive
        for item in selected_items:
            animal_id = int(self.table.item(item, 'values')[0])
            self.table.selection_remove(item)
            self.table.delete(item)
            self.db.set_animal_active_status(animal_id, 0)  # Mark as inactive
            self.animals = [(index, rfid) for (index, rfid) in self.animals if index != animal_id]

            # Then update the UI table
            self.change_entry_text()

            # Then decrease the maximum number of animals
            current_max = self.db.get_total_number_animals()
            current_max = current_max - 1
            if current_max <= 0:
                self.raise_warning("Cannot reduce animal count below 0")
                return
            else:
                # Decrease the maximum number of animals by 1
                self.db.set_number_animals(current_max)

class SerialPortSelection():
    '''Serial port selection user interface.'''
    def __init__(self, parent: CTk, controller: SerialPortController, map_rfid: MapRFIDPage):

        self.parent = parent
        self.map_rfid = map_rfid
        self.id = None

        self.port_controller = controller

        self.serial_simulator = SerialSimulator(self.parent)

    def open(self):
        '''Opens Serial Port Selection Dialog.'''
        self.root = CTkToplevel(self.parent)
        self.root.title("Serial Port Selection")
        self.root.geometry('400x400')
        columns = ('port', 'description')
        self.table = Treeview(self.root, columns=columns, show='headings')

        #headings
        self.table.heading('port', text='Port')
        self.table.column('port', width = 100)
        self.table.heading('description', text='Description')
        self.table.column('description', width = 400)

        #grid for the serial ports
        self.table.grid(row=0, column=0, sticky=NSEW)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        #scrollbar
        scrollbar = CTkScrollbar(self.root, orientation=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.update_ports()


        self.select_port = CTkButton(self.root,
                                     text = "Select Port",
                                     compound=TOP,
                                     width=15,
                                     command=self.conform_selection)
        self.select_port.place(relx=0.50, rely=0.85, anchor=CENTER)

        self.run_simulate = CTkButton(self.root,
                                      text = "Run Simulation",
                                      compound=TOP,
                                      width=15,
                                      command=self.open_simulator)

        self.run_simulate.place(relx=0.75, rely=0.85, anchor=CENTER)

    def update_ports(self):
        '''Updates the displayed ports to reflect available ports.'''
        ports = self.port_controller.get_available_ports()
        self.table.tag_configure('TkTextFont', font=tkfont.nametofont('TkTextFont'))
        style = Style()
        style.configure('TkTextFont', font = (NONE,30))
        for line in ports:
            self.table.insert('', END, values = line, tags='TkTextFont')

    def conform_selection(self):
        '''Confirms the selected value.'''
        if self.id is not None:
            item_details = self.table.item(self.id)      #port_info = ['port name', 'description']
            port_info = item_details.get("values")
            virtual_ports = self.port_controller.get_virtual_port()

            if self.port_controller.set_reader_port is not None:
                self.port_controller.close_reader_port()
                self.port_controller.close_writer_port()

            self.port_controller.set_reader_port(port_info[0])
            description = port_info[1].split(" ")

            if "com0com" in description:
                virtual_ports.remove(port_info[0])
                self.port_controller.set_writer_port(virtual_ports[0])

            self.root.destroy()
            # todo: allow user to choose a virtual port as reader_port and the other
            # virtual port as writer port, when user selects any other ports that's not
            # virtual, raise warning

    def open_simulator(self):
        '''Opens serial simuplator dialog.'''
        self.serial_simulator.open()

class SerialSimulator():
    '''Serial Simulator dialog.'''
    def __init__(self, parent: CTk):
        self.parent = parent
        self.serial_controller = SerialPortController()
        self.written_port = None

    def open(self):

        '''Opens the serial simulator dialog.'''
        if len(self.serial_controller.get_virtual_port()) == 0:
            warning = CTkMessagebox(title="Warning",
                                    message="Virtual ports missing, would you like to download the virtual ports?",
                                    icon="warning",
                                    option_1="Cancel",
                                    option_2="Download")
            if warning.get() == "Download":
                self.download_link()

        else:
            self.root = CTkToplevel(self.parent)
            self.root.title("Serial Port Selection")
            self.root.geometry('400x400')

            self.read_message = CTkTextbox(self.root, height=15, width = 40)
            self.read_message.place(relx=0.10, rely = 0.00)

            self.drop_down_ports = CTkComboBox(self.root, values=self.serial_controller.get_virtual_port())
            self.drop_down_ports.place(relx=0.30, rely = 0.88)

            self.comfirm_port = CTkButton(self.root, text="confirm port", width=15,
                                        command=self.set_written_port)
            self.comfirm_port.place(relx=0.80, rely=0.900, anchor=CENTER)

            self.input_entry = CTkEntry(self.root, width=140)
            self.input_entry.place(relx=0.50, rely=0.80, anchor=CENTER)

            self.sent_button = CTkButton(self.root, text = "sent", width = 15, command=self.sent)
            self.sent_button.place(relx=0.80, rely = 0.80, anchor=CENTER)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def sent(self):
        '''Writes to the appropriate port.'''
        if self.written_port is not None:
            print(self.written_port)
            message = self.input_entry.get()
            self.serial_controller.write_to(message)
            self.read_and_display()
        else:
            self.raise_warning()

    def setup_ports(self):
        '''Sets up virtual ports.'''
        self.serial_controller.set_writer_port(self.written_port)

        available_port = self.serial_controller.get_virtual_port()
        available_port.remove(self.written_port)

        self.serial_controller.set_reader_port(available_port[0])

    def read_and_display(self):
        '''Reads from available port.'''
        available_port = self.serial_controller.get_virtual_port()
        available_port.remove(self.written_port)

        if len(available_port)==0:
            CTkMessagebox(
                message="There seems to be problem with the virtual port, please submit bug report.",
                title="Warning",
                icon="cancel"
            )

        else:
            message = self.serial_controller.read_info()
            self.read_message.insert(END,message)

    def check_written_port(self):
        '''Returns if writting port is available.'''
        if self.written_port is None:
            return False
        else:
            return True

    def set_written_port(self):
        '''Sets the writting port or raises an error if
        it doesn't work.'''
        self.written_port = self.drop_down_ports.get()
        try:
            self.setup_ports()
        except serialutil.SerialException:
            self.raise_warning()

    def download_link(self):
        '''Opens download lint in webbrowser.'''
        webbrowser.open("https://softradar.com/com0com/")

    def on_closing(self):
        '''Closes all ports and closes the window.'''
        self.serial_controller.close_all_port()
        self.written_port = None
        self.root.destroy()

    def raise_warning(self, warning_message='Maximum number of animals reached'):
        '''Raises an error window that can be dismissed with any key or mouse press.'''

        def dismiss_warning(event=None):
            '''Destroy the warning window when triggered.'''
            print(f"Event triggered: {event}")  # Debugging to confirm key press is detected
            message.destroy()

        message = CTk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(False, False)
        root = CTk()
        root.bind("<KeyPress>", dismiss_warning)


        label = CTkLabel(message, text=warning_message)
        label.grid(row=0, column=0, padx=10, pady=10)

        # Ensure the pop-up window grabs focus
        message.focus_force()

        # Bind key and mouse events to dismiss the window
        message.bind("<KeyPress>", dismiss_warning)  # Captures any key press
        message.bind("<Button>", dismiss_warning)   # Captures any mouse click

        # Add an OK button for manual dismissal
        ok_button = CTkButton(message, text="OK", width=10, command=dismiss_warning)
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        AudioManager.play("shared/sounds/error.wav")

        message.mainloop()
