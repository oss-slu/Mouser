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

def get_random_rfid():
    '''Returns a simulated rfid number'''
    return random.randint(1000000, 9999999)

def play_sound_async(filename):
    '''Plays the given filename.'''
    threading.Thread(target=playsound, args=(filename,), daemon=True).start()

class MapRFIDPage(MouserPage):# pylint: disable= undefined-variable
    '''Map RFID user interface and window.'''
    def __init__(self, database, parent: CTk, previous_page: CTkFrame = None):

        super().__init__(parent, "Map RFID", previous_page)


        file = database
        self.db = ExperimentDatabase(file)
        self.serial_port_controller = SerialPortController("serial_port_preference.csv")

        self.animals = []
        self.animal_id = 1

        self.animal_id_entry_text = StringVar(value="1")

        
        

        simulate_rfid_button = CTkButton(self, text="Simulate RFID", compound=TOP,
                                      width=15, command=self.add_random_rfid)
        simulate_rfid_button.place(relx=0.80, rely=0.17, anchor=CENTER)


        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.15, rely=0.40, relheight=0.50, relwidth=0.80)
        self.table_frame.grid_columnconfigure(0, weight= 1)
        self.table_frame.grid_rowconfigure(0, weight= 1)

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

        self.changer = ChangeRFIDDialog(parent, self)
        self.serial_port_panel = SerialPortSelection(parent,self.serial_port_controller, self)

        self.serial_port_button = CTkButton(self, text="Select Serial Port", compound=TOP,
                                      width=15, command=self.open_serial_port_selection)
        self.serial_port_button.place(relx=0.10, rely=0.95, anchor=CENTER)

        self.change_rfid_button = CTkButton(self, text="Change RFID", compound=TOP,
                                         width=15, command=self.open_change_rfid)
        self.change_rfid_button.place(relx=0.40, rely=0.95, anchor=CENTER)

        self.delete_button = CTkButton(self, text="Remove Selection(s)", compound=TOP,
                                       width=20, command=self.remove_selected_items,
                                       state="normal")  # Initialize button as disabled
        self.delete_button.place(relx=0.70, rely=0.95, anchor=CENTER)

        self.item_selected(None)

        animals_setup = self.db.get_all_animal_ids()
        for animal in animals_setup:
            rfid = self.db.get_animal_rfid(animal)
            value = (int(animal), rfid)
            self.table.tag_configure('text_font', font=('Arial', 10))
            self.table.insert('', END, values=value, tags='text_font')
            self.animals.append(value)
            self.animal_id_entry_text.set(animal)

        ##setting previous button behavior
        self.menu_button = None
        self.set_menu_button(previous_page)
        self.menu_page = previous_page

        self.menu_button.configure(command = self.press_back_to_menu_button)
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
        if len(self.animals) == self.db.get_number_animals():
            self.raise_warning()
        elif self.serial_port_controller.get_writer_port() is not None:
            self.serial_port_controller.write_to("123")
            constant_rfid = self.serial_port_controller.read_info()
            rand_rfid = constant_rfid+str(random.randint(10000, 99999))
            self.add_value(int(rand_rfid))
        else:
            rfid = get_random_rfid()
            self.add_value(rfid)

    def add_value(self, rfid):
        '''Adds rfid number and animal to the table and to the database.'''
        item_id = self.animal_id
        self.table.insert('', item_id-1, values=(item_id, rfid), tags='text_font')
        # self.animals.append((item_id, rfid))
        self.animals.insert(item_id-1, (item_id, rfid))
        self.change_entry_text()
        self.db.add_animal(item_id, rfid)
        AudioManager.play("shared/sounds/rfid_success.wav")


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

    def open_change_rfid(self):
        '''Opens change RFID window if an item is selected, otherwise shows a warning.'''
        selected_items = self.table.selection()
    
        # Check if there is exactly one item selected (assuming RFID change is intended for single selections)
        if len(selected_items) != 1:
            self.raise_warning("No item selected. Please select a single item to change its RFID.")
            return

        # If an item is selected, proceed to open the RFID change dialog
        self.changing_value = selected_items[0]
        self.change_rfid_button["state"] = "disabled"
        self.changer.open()

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

    def add_random_rfid(self):
        '''Adds a random frid number to selected value.'''
        rfid = get_random_rfid()
        self.map_rfid.change_selected_value(rfid)
        self.close()

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