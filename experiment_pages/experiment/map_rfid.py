'''Map RFID module.'''
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
from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager
from tkinter import messagebox

def get_random_rfid():
    '''Returns a simulated rfid number.'''
    return random.randint(1000000, 9999999)

def play_sound_async(filename):
    '''Plays the given filename asynchronously.'''
    threading.Thread(target=playsound, args=(filename,), daemon=True).start()

class MapRFIDPage(MouserPage):  # pylint: disable=undefined-variable
    def __init__(self, database, parent: CTk, previous_page: CTkFrame = None):
        super().__init__(parent, "Map RFID", previous_page)

        self.db = ExperimentDatabase(database)
        self.serial_port_controller = SerialPortController(
            "settings/serial ports/serial_port_preference.csv"
        )

        self.animals = []  # Initialize animals list
        self.animal_id = 1  # Initialize animal ID counter
        self.animal_id_entry_text = StringVar(value="1")  # Initialize entry text properly


        # Set up the table frame
        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.15, rely=0.40, relheight=0.50, relwidth=0.80)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        # Configure the table
        heading_style = Style()
        heading_style.configure("Treeview.Heading", font=('Arial', 10))
        columns = ('animal_id', 'rfid')

        self.table = Treeview(
            self.table_frame, columns=columns, show='headings', height=10, style='column.Treeview'
        )
        self.table.heading('animal_id', text='Animal ID')
        self.table.heading('rfid', text='RFID')
        self.table.grid(row=0, column=0, sticky='nsew')

        # Add scrollbar to the table
        scrollbar = CTkScrollbar(self.table_frame, orientation=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.table.grid(row=0, column=0, sticky='nsew')
        self.table.configure(yscroll=scrollbar.set)


        self.serial_port_button = CTkButton(self, text="Select Serial Port", compound=TOP,
                                            width=15, command=self.open_serial_port_selection)
        self.serial_port_button.place(relx=0.10, rely=0.95, anchor=CENTER)

        self.change_rfid_button = CTkButton(self, text="Change RFID", compound=TOP,
                                            width=15, command=self.open_change_rfid)
        self.change_rfid_button.place(relx=0.40, rely=0.95, anchor=CENTER)

        self.delete_button = CTkButton(self, text="Remove Selection(s)", compound=TOP,
                                    width=20, command=self.remove_selected_items,
                                    state="normal")
        self.delete_button.place(relx=0.70, rely=0.95, anchor=CENTER)

        # Initialize right-click menu
        self.right_click = Menu(self, tearoff=0)
        self.right_click.add_command(label="Remove Selection(s)", command=self.remove_selected_items)

        # Bind the right-click menu to the table
        self.table.bind("<Button-3>", self.right_click_menu)


        # Simulate RFID Button
        simulate_rfid_button = CTkButton(
            self, text="Simulate RFID", compound=TOP, width=15, 
            command=self.add_random_rfid
        )
        simulate_rfid_button.place(relx=0.80, rely=0.17, anchor=CENTER)

        # Simulate All RFID Button
        simulate_all_rfid_button = CTkButton(
            self, text="Simulate All RFID", compound=TOP, width=15, 
            command=self.simulate_all_rfid
        )
        simulate_all_rfid_button.place(relx=0.80, rely=0.27, anchor=CENTER)

    def add_value(self, rfid):
        '''Adds an RFID entry to the table and updates animals list.'''
        try:
            item_id = len(self.animals) + 1  # Increment animal ID
            self.animals.append({'id': item_id, 'rfid': rfid})  # Update animals list

            print(f"Inserting into table: Animal {item_id}, RFID {rfid}")
            self.table.insert('', 'end', values=(item_id, rfid))  # Insert into table

            self.change_entry_text()  # Update the animal ID entry text
            print("Table insertion and entry text update successful.")

        except Exception as e:
            print(f"Error in add_value: {e}")


    def change_entry_text(self):
        '''Updates the animal ID entry text to the next unmapped animal.'''
        next_animal = len(self.animals) + 1  # Calculate the next animal ID
        self.animal_id_entry_text.set(str(next_animal))  # Update the entry text


    def add_random_rfid(self, play_sound=True):
        '''Adds a random RFID value to the next animal.'''
        try:
            print(f"Attempting to add RFID. Current animal count: {len(self.animals)}")

            if len(self.animals) >= self.db.get_number_animals():
                self.raise_warning("All animals are already mapped.")
                return

            rfid = get_random_rfid()
            print(f"Generated RFID: {rfid}")

            # Schedule the addition using after() to avoid race conditions
            self.master.after(0, lambda: self.add_value(rfid))
            print(f"RFID {rfid} added successfully for animal {len(self.animals)}")

            # Play audio if enabled, with a small delay to avoid threading issues
            if play_sound:
                self.master.after(100, lambda: AudioManager.play("shared/sounds/rfid_success.wav"))

        except Exception as e:
            print(f"Error in add_random_rfid: {e}")





    def simulate_all_rfid(self):
        '''Simulates RFID values for all unmapped animals with increased delay.'''
        try:
            unmapped_count = self.db.get_number_animals() - len(self.animals)

            if unmapped_count <= 0:
                self.raise_warning("All animals are already mapped.")
                return

            # Use a larger delay between each operation to prevent overload
            for i in range(unmapped_count):
                self.master.after(i * 100, self.add_random_rfid, False)  # 100ms delay per animal

            print(f"Simulated {unmapped_count} animals.")

            # Show success message after all RFIDs are added
            self.master.after(unmapped_count * 100, lambda: messagebox.showinfo(
                "RFID Simulation Complete",
                f"{unmapped_count} animals have been successfully mapped with RFID."
            ))

        except Exception as e:
            print(f"Error in simulate_all_rfid: {e}")



    def show_feedback_message(self, unmapped_count):
        '''Displays a feedback message after RFID simulation.'''
        try:
            # Create a message box without the parent argument
            CTkMessagebox(
                title="RFID Simulation Complete",
                message=f"{unmapped_count} animals have been successfully mapped with RFID.",
                icon="check"
            )
        except Exception as e:
            print(f"Error displaying message box: {e}")

    def setup_navigation_buttons(self, previous_page):
        '''Set up buttons for serial port selection, change RFID, and removing selections.'''

        # Serial Port Button
        self.serial_port_button = CTkButton(
            self, text="Select Serial Port", compound=TOP, width=15,
            command=self.open_serial_port_selection
        )
        self.serial_port_button.place(relx=0.10, rely=0.95, anchor=CENTER)

        # Change RFID Button
        self.change_rfid_button = CTkButton(
            self, text="Change RFID", compound=TOP, width=15,
            command=self.open_change_rfid
        )
        self.change_rfid_button.place(relx=0.40, rely=0.95, anchor=CENTER)

        # Delete Button
        self.delete_button = CTkButton(
            self, text="Remove Selection(s)", compound=TOP, width=20,
            command=self.remove_selected_items, state="normal"
        )
        self.delete_button.place(relx=0.70, rely=0.95, anchor=CENTER)

        # Menu button setup
        self.set_menu_button(previous_page)
        self.menu_button.configure(command=self.press_back_to_menu_button)
        self.scroll_to_latest_entry()


    def scroll_to_latest_entry(self):
        #Scrolls to the latest entry in the RFID table.
        self.table.yview_moveto(1)

    def right_click_menu(self, event):
       #Opens the right-click menu.
        if len(self.table.selection()) != 0:
            try:
                self.right_click.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click.grab_release()
        

    def open_change_rfid(self):
        '''Opens the change RFID dialog.'''
        selected_items = self.table.selection()
        if len(selected_items) != 1:
            self.raise_warning("Please select a single item to change its RFID.")
            return
        self.changing_value = selected_items[0]
        self.change_rfid_button["state"] = "disabled"
        self.changer.open()

    def open_serial_port_selection(self):
        '''Opens the serial port selection dialog.'''
        self.serial_port_panel.open()

    def raise_warning(self, warning_message='Maximum number of animals reached'):
        '''Raises a warning message.'''
        message = CTk()
        message.title("WARNING")
        message.geometry('320x100')
        label = CTkLabel(message, text=warning_message)
        label.grid(row=0, column=0, padx=10, pady=10)
        ok_button = CTkButton(message, text="OK", command=message.destroy)
        ok_button.grid(row=1, column=0, pady=10)
        AudioManager.play("shared/sounds/error.wav")
        message.mainloop()

    def press_back_to_menu_button(self):
        '''Handles navigation back to the menu.'''
        if len(self.animals) != self.db.get_number_animals():
            self.raise_warning("Not all animals have been mapped.")
        else:
            self.menu_button.navigate()



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

    # Handling for change RFID button
        if len(selected) != 1:
            self.change_rfid_button["state"] = "disabled"
        else:
            self.change_rfid_button["state"] = "normal"


    def remove_selected_items(self):
        '''Removes the selected item from a table, warning if none selected.'''
        selected_items = self.table.selection()

        # Check if any items are selected
        if not selected_items:  # If no items are selected
            self.raise_warning("No item selected. Please select an item to remove.")
            return

        for item in selected_items:
            item_id = int(self.table.item(item, 'values')[0])
            self.table.delete(item)
            self.db.remove_animal(item_id)

            # Update animal list
            self.animals = [(index, rfid) for (index, rfid) in self.animals if index != item_id]

        self.change_entry_text()

    def get_next_animal(self):
        '''returns the next animal in our experiment.'''

        min_unused = 1

        for animal in sorted(self.animals):
            if animal[0] > min_unused: 
                break
            min_unused += 1

        return min_unused

        '''
        next_animal = self.animals[-1][0] + 1
        for i, animal in enumerate(self.animals):
            if i < len(self.animals) - 1 and animal[0] + 1 != self.animals[i+1][0]:
                next_animal = animal[0] + 1
                break
        return next_animal
        '''

    def press_back_to_menu_button(self):
        '''On pressing of back to menu button.'''
        if len(self.animals) != self.db.get_number_animals():
            self.raise_warning(warning_message= 'Not all animals have been mapped to RFIDs')
        else:
            self.menu_button.navigate() #pylint: disable= undefined-variable

    def close_connection(self):
        '''Closes database file.'''
        self.db.close()

class ChangeRFIDDialog():
    '''Change RFID user interface.'''
    def __init__(self, parent: CTk, map_rfid: MapRFIDPage):
        self.parent = parent
        self.map_rfid = map_rfid

    def open(self):
        '''Opens the change rfid dialog.'''
        self.root = root = CTkToplevel(self.parent) # pylint: disable=redefined-outer-name
        root.title("Change RFID")
        root.geometry('400x400')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        simulate_rfid_button = CTkButton(root, text="Simulate RFID", compound=TOP,
                                      width=15, command= self.add_random_rfid)
        simulate_rfid_button.place(relx=0.50, rely=0.20, anchor=CENTER)

        self.root.mainloop()

    def close(self):
        '''Closes change RFID dialog.'''
        self.root.destroy()

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

    def raise_warning(self):
        '''Raises a error window.'''
        message = CTkToplevel()
        message.geometry("320x100")
        message.title('Warning')
        label = CTkLabel(message, text='Please select a serial port from the drop down list')
        label.grid(row=0, column=0, padx=10, pady=10)

        AudioManager.play("shared/sounds/error.wav")