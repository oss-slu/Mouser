from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from tk_models import *
import tkinter.font as tkfont
import random
from playsound import playsound
import threading
import webbrowser
from serial_port_controller import SerialPortController
from serial import serialutil


from database_apis.experiment_database import ExperimentDatabase

def get_random_rfid():
    return random.randint(1000000, 9999999)


def play_sound_async(filename):
    threading.Thread(target=playsound, args=(filename,), daemon=True).start()

         


class MapRFIDPage(MouserPage):
    def __init__(self, database, parent: Tk, previous_page: Frame = None):
        super().__init__(parent, "Map RFID", previous_page)

        file = "databases/experiments/" + str(database) + '.db'
        self.db = ExperimentDatabase(file)

        self.animals = []
        self.animal_id = 0

        self.animal_id_entry_text = StringVar(value="1")

        self.animal_id_entry = Entry(
            self, width=40, textvariable=self.animal_id_entry_text)
        self.animal_id_entry.place(relx=0.50, rely=0.20, anchor=CENTER)
        animal_id_header = Label(self, text="Animal ID:", font=("Arial", 12))
        animal_id_header.place(relx=0.28, rely=0.20, anchor=E)

        simulate_rfid_button = Button(self, text="Simulate RFID", compound=TOP,
                                      width=15, command=lambda: self.add_random_rfid())
        simulate_rfid_button.place(relx=0.80, rely=0.20, anchor=CENTER)


        self.table_frame = Frame(self)
        self.table_frame.place(relx=0.15, rely=0.40, relheight= 0.40, relwidth=0.80)
        self.table_frame.grid_columnconfigure(0, weight= 1)
        self.table_frame.grid_rowconfigure(0, weight= 1)
        

        heading_style = Style()
        heading_style.configure("Treeview.Heading", font=('Arial', 10))

        columns = ('animal_id', 'rfid')
        self.table = Treeview(
            self.table_frame, columns=columns, show='headings', height=5, style='column.Treeview')

        self.table.heading('animal_id', text='Animal ID')
        self.table.heading('rfid', text='RFID')

        self.table.grid(row=0, column=0, sticky='nsew')
        self.table.grid_columnconfigure(0, weight = 1)
        self.table.grid_rowconfigure(0, weight = 1)


        scrollbar = Scrollbar(
            self.table_frame, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        self.right_click = Menu(self, tearoff=0)
        self.right_click.add_command(
            label="Remove Selection(s)", command=self.remove_selected_items)
        self.table.bind("<Button-3>", self.right_click_menu)

        self.changer = ChangeRFIDDialog(parent, self)
        self.serial_port_panel = SerialPortSelection(parent, self)

        self.serial_port_button = Button(self, text="Select Serial Port", compound=TOP,
                                      width=15, command=self.open_serial_port_selection)
        self.serial_port_button.place(relx=0.10, rely=0.85, anchor=CENTER)

        self.change_rfid_button = Button(self, text="Change RFID", compound=TOP,
                                         width=15, command=self.open_change_rfid)
        self.change_rfid_button.place(relx=0.40, rely=0.85, anchor=CENTER)

        self.delete_button = Button(self, text="Remove Selection(s)", compound=TOP,
                                    width=20, command=self.remove_selected_items)
        self.delete_button.place(relx=0.70, rely=0.85, anchor=CENTER)

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

        self.menu_button.configure(command = lambda: self.press_back_to_menu_button())
        self.scroll_to_latest_entry()
    def scroll_to_latest_entry(self):
        self.table.yview_moveto(1)

    def right_click_menu(self, event):
        if len(self.table.selection()) != 0:
            try:
                self.right_click.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click.grab_release()

    def add_random_rfid(self):
        if (len(self.animals) == self.db.get_number_animals()):
            self.raise_warning()
        else:
            rfid = get_random_rfid()
            self.add_value(rfid)

    def add_value(self, rfid):
        self.animal_id = self.db.add_animal(rfid)
        value = (self.animal_id, rfid)
        self.table.tag_configure('text_font', font=('Arial', 10))
        self.table.insert('', END, values=value, tags='text_font')
        self.animals.append(value)
        self.animal_id_entry_text.set(str(self.animal_id))
        self.scroll_to_latest_entry()
        play_sound_async('./sounds/rfid_success.mp3')

    def change_selected_value(self, rfid):
        item = self.table.item(self.changing_value)
        self.table.item(self.changing_value, values=(
            item['values'][0], rfid))
        self.change_rfid_button["state"] = "normal"
        play_sound_async('./sounds/rfid_success.mp3')

    def item_selected(self, event):
        selected = self.table.selection()

        if len(selected) != 1:
            self.change_rfid_button["state"] = "disabled"
            self.serial_port_button["state"] = "disabled"
        else:
            self.change_rfid_button["state"] = "normal"
            self.serial_port_button["state"] = "normal"

        if len(selected) == 0:
            self.delete_button["state"] = "disabled"
        else:
            self.delete_button["state"] = "normal"

    
    def remove_selected_items(self):
        for item in self.table.selection():
            # Animal ID Before Removing
            animal_id_remove = int(self.table.item(item, 'values')[0])
            
            self.table.delete(item)

            # If Animal ID is greater than the ID to remove, subtract the animal ID by one
            if self.animal_id > animal_id_to_remove:
                self.animal_id -= 1

    def open_change_rfid(self):
        self.changing_value = self.table.selection()[0]
        self.change_rfid_button["state"] = "disabled"
        self.changer.open()

    def open_serial_port_selection(self):
        self.serial_port_button["state"] = "disabled"
        self.serial_port_panel.open()


    def raise_warning(self, warning_message = 'Maximum number of animals reached'):
        message = Tk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(False, False)

        label = Label(message, text= warning_message)
        label.grid(row=0, column=0, padx=10, pady=10)

        ok_button = Button(message, text="OK", width=10, 
                        command= lambda: [message.destroy()])
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        message.mainloop()

    def press_back_to_menu_button(self):
        if (len(self.animals) != self.db.get_number_animals()):
            self.raise_warning(warning_message= 'Not all animals have been mapped to RFIDs')
        else:
            self.menu_page.tkraise()
    def close_connection(self):
        self.db.close()

    def close_connection(self):
        self.db.close()


class ChangeRFIDDialog():
    def __init__(self, parent: Tk, map_rfid: MapRFIDPage):
        self.parent = parent
        self.map_rfid = map_rfid

    def open(self):
        self.root = root = Toplevel(self.parent)
        root.title("Change RFID")
        root.geometry('400x400')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        simulate_rfid_button = Button(root, text="Simulate RFID", compound=TOP,
                                      width=15, command=lambda: self.add_random_rfid())
        simulate_rfid_button.place(relx=0.50, rely=0.20, anchor=CENTER)

        self.root.mainloop()

    def add_random_rfid(self):
        rfid = get_random_rfid()
        self.map_rfid.change_selected_value(rfid)
        self.close()

    def close(self):
        self.root.destroy()

class SerialPortSelection():
    def __init__(self, parent: Tk, map_rfid: MapRFIDPage):
        self.parent = parent
        self.map_rfid = map_rfid
        self.id = None
        self.portController = SerialPortController()
        self.serial_simulator = SerialSimulator(self.parent)
    
    def open(self):
        root = Toplevel(self.parent)
        root.title("Serial Port Selection")
        root.geometry('400x400')
        columns = ('port', 'description')
        self.table = Treeview(root, columns=columns, show='headings')


        #headings
        self.table.heading('port', text='Port')
        self.table.column('port', width = 100)
        self.table.heading('description', text='Description')
        self.table.column('description', width = 400)

        #grid for the serial ports
        self.table.grid(row=0, column=0, sticky=NSEW)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        #scrollbar
        scrollbar = Scrollbar(root, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.update_ports()

        self.select_port = Button(root, text = "Select Port", compound=TOP, width=15, command=self.conform_selection)
        self.select_port.place(relx=0.50, rely=0.85, anchor=CENTER)

        self.run_simulate = Button(root, text = "Run Simulation", compound=TOP, width=15, command=self.open_simulator)
        self.run_simulate.place(relx=0.75, rely=0.85, anchor=CENTER)


    def update_ports(self):
        ports = self.portController.get_available_ports()
        self.table.tag_configure('TkTextFont', font=tkfont.nametofont('TkTextFont'))
        style = Style()
        style.configure('TkTextFont', font = (NONE,30))
        for line in ports:
            self.table.insert('', END, values = line, tags='TkTextFont')
        
    def item_selected(self, event):
        self.id = self.table.selection()[0]


    def conform_selection(self):
        if (self.id != None):
            item_details = self.table.item(self.id)      #port_info = ['port name', 'description']
            port_info = item_details.get("values")
            self.portController.set_reader_port(port_info[0])
            # Todo: complete the implementation of read_info in serial_port_controller

    def open_simulator(self):
        self.serial_simulator.open()


class SerialSimulator():
    def __init__(self, parent: Tk):
        self.parent = parent
        self.serial_controller = SerialPortController()
        self.written_port = None

    def open(self):
        if (len(self.serial_controller.get_virtual_port()) == 0):
            warning = messagebox.askyesno(
                message=f"Virtual ports missing, would you like to download the virtual ports?",
                title="Warning"
                )
            if (warning):
                self.download_link()
              
        else:
            self.root = Toplevel(self.parent)
            self.root.title("Serial Port Selection")
            self.root.geometry('400x400')

            self.read_message = Text(self.root, height=15, width = 40)
            self.read_message.place(relx=0.10, rely = 0.00)

            self.drop_down_ports = Combobox(self.root, values=self.serial_controller.get_virtual_port())
            self.drop_down_ports.place(relx=0.30, rely = 0.88)

            self.comfirm_port = Button(self.root, text="confirm port", width=15,
                                        command=self.set_written_port)
            self.comfirm_port.place(relx=0.80, rely=0.900, anchor=CENTER)

            self.input_entry = Entry(self.root, width=40)
            self.input_entry.place(relx=0.50, rely=0.80, anchor=CENTER)

            self.sent_button = Button(self.root, text = "sent", width = 15, command=self.sent)
            self.sent_button.place(relx=0.80, rely = 0.80, anchor=CENTER)
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def sent(self):
        if (self.written_port != None):
            print(self.written_port)
            message = self.input_entry.get()
            self.serial_controller.write_to(message)
            self.read_and_display()
        else:
            self.raise_warning()
            """
            messagebox.showinfo(
                message=f"Please select a serial port from the drop down list",
                title="Warning"
                )"""
    
    def setup_ports(self):

        self.serial_controller.set_writer_port(self.written_port)

        available_port = self.serial_controller.get_virtual_port()
        available_port.remove(self.written_port)

        self.serial_controller.set_reader_port(available_port[0])


    def read_and_display(self):
        available_port = self.serial_controller.get_virtual_port()
        available_port.remove(self.written_port)
        if (len(available_port)==0):
            messagebox.showwarning(
                message=f"There seems to be problem with the virtual port, please submit bug report.",
                title="Warning"
                )
        else:
            message = self.serial_controller.read_info()
            self.read_message.insert(END,message)



    def check_written_port(self):
        if (self.written_port == None):
            return False
        else:
            return True

    
    def set_written_port(self):
        self.written_port = self.drop_down_ports.get()
        try:
            self.setup_ports()
        except serialutil.SerialException:
            self.raise_warning()

    def download_link(self):
        webbrowser.open("https://softradar.com/com0com/")

    def on_closing(self):
        self.serial_controller.close_all_port()
        self.written_port = None
        self.root.destroy()

    def raise_warning(self):
        message = Toplevel()
        message.geometry("320x100")
        message.title('Warning')
        label = Label(message, text='Please select a serial port from the drop down list')
        label.grid(row=0, column=0, padx=10, pady=10)
