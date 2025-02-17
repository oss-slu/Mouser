'''Data collection ui module.'''
from datetime import date
from tkinter.ttk import Treeview, Style
import time
from customtkinter import *
from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase
from databases.data_collection_database import DataCollectionDatabase
from shared.audio import AudioManager
from shared.scrollable_frame import ScrolledFrame
from shared.serial_handler import SerialDataHandler
import threading

#pylint: disable= undefined-variable
class DataCollectionUI(MouserPage):
    '''Page Frame for Data Collection.'''

    def __init__(self, parent: CTk, prev_page: CTkFrame = None, database_name = ""):

        super().__init__(parent, "Data Collection", prev_page)

        self.rfid_reader = None 
        self.rfid_stop_event = threading.Event()  # Event to stop RFID listener
        self.rfid_thread = None # Store running thread

        self.database = ExperimentDatabase(database_name)
        self.measurement_items = self.database.get_measurement_items()
        
        ## ENSURE ANIMALS ARE IN DATABASE BEFORE EXPERIMENT FOR EXPERIMENTS W/O RFID ##
        if self.database.experiment_uses_rfid() != 1 and self.database.get_animals() == []:
            i = 1
            max_num_animals = self.database.get_number_animals()
            while i <= max_num_animals:
                self.database.add_animal(i, i)
                i = i + 1



        self.measurement_strings = []
        self.measurement_ids = []
        for item in self.measurement_items:
            self.measurement_strings.append(item[1])
            self.measurement_ids.append(str(item[1]).lower().replace(" ", "_"))


        self.data_database = DataCollectionDatabase(database_name, self.measurement_strings)

        if self.database.experiment_uses_rfid() == 0:
            start_function = self.auto_increment
        else:
            start_function = self.rfid_listen
        self.auto_increment_button = CTkButton(self,
                                               text="Start",
                                               compound=TOP,
                                               width=15,
                                               command= start_function)
        self.auto_increment_button.place(relx=0.45, rely=0.4, anchor=CENTER)
        self.auto_inc_id = -1

        self.stop_button = CTkButton(self,
                                     text="Stop Listening",
                                     compound=TOP,
                                     width=15,
                                     command= self.stop_listening)
        self.stop_button.place(relx=0.55, rely=0.4, anchor=CENTER)

        self.animals = self.database.get_animals()
        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.50, rely=0.65, anchor=CENTER)
        


        columns = ['animal_id', 'rfid']
        for measurement_id in self.measurement_ids:
            columns.append(measurement_id)

        self.table = Treeview(self.table_frame,
                              columns=columns, show='headings',
                              selectmode="browse",
                              height=len(self.animals))
        style = Style()
        style.configure("Treeview", font=("Arial", 18), rowheight=40)
        style.configure("Treeview.Heading", font=("Arial", 18))

        for i, column in enumerate(columns):
            if i == 0:
                text = "Animal ID"
            elif i == 1:
                text = "RFID"
            else:
                if i-2 < len(self.measurement_strings):  # Ensure index is in range
                    text = self.measurement_strings[i-2]
                else:
                    text = f"Measurement {i-1}"  # Default placeholder for missing items
            
            self.table.heading(column, text=text)


        self.table.grid(row=0, column=0, sticky='nsew')

        self.date_label = CTkLabel(self)

        self.animals = self.database.get_animals()  # Fetches Animal ID and RFID
        for animal in self.animals:
            animal_id = animal[0]
            rfid = self.database.get_animal_rfid(animal_id)  # Fetch RFID from database
            value = (animal_id, rfid, 0, 0)  # Include RFID in each row
            self.table.insert('', END, values=value)


        self.get_values_for_date(None)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        self.changer = ChangeMeasurementsDialog(parent, self, self.measurement_strings)


    def item_selected(self, _):
        '''On item selection.

        Records the value selected and opens the changer frame.'''
        self.auto_inc_id = -1
        self.changing_value = self.table.selection()[0]
        self.open_changer()

    def open_changer(self):
        '''Opens the changer frame for the selected animal id.'''
        animal_id = self.table.item(self.changing_value)["values"][0]
        self.changer.open(animal_id)

    def auto_increment(self):
        '''Automatically increments changer to hit each animal.'''
        self.auto_inc_id = 0
        self.open_auto_increment_changer()
    
    def rfid_listen(self):
        '''Continuously listens for RFID scans until manually stopped.'''
        
        if self.rfid_thread and self.rfid_thread.is_alive():
            print("⚠️ RFID listener is already running!")
            return  # Prevent multiple listeners

        print("📡 Starting RFID listener...")
        self.rfid_stop_event.clear()  # Reset stop flag

        def listen():
            rfid_reader = SerialDataHandler("reader")
            rfid_reader.start()
            print("🔄 RFID Reader Started!")

            while not self.rfid_stop_event.is_set():
                received_rfid = rfid_reader.get_stored_data()

                if received_rfid:
                    print(f"📡 RFID Scanned: {received_rfid}")
                    
                    animal_id = self.database.get_animal_id(received_rfid)
                    
                    if animal_id is None:
                        print(f"⚠️ No matching animal found for RFID: {received_rfid}")
                        continue  # Prevent NoneType errors

                    print(f"✅ Found Animal ID: {animal_id}")
                    self.after(0, lambda: self.select_animal_by_id(animal_id))

                time.sleep(1)  # Prevent duplicate scans

            print("🛑 RFID listener has stopped.")
            rfid_reader.stop()


        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    def stop_listening(self):
        '''Stops the RFID listener and ensures the serial port is released.'''
        print("🛑 Stopping RFID listener...")
        self.rfid_stop_event.set()  # Signal thread to stop

        if hasattr(self, "rfid_reader") and self.rfid_reader:  # Check if the reader exists
            self.rfid_reader.stop()  # Properly close the serial connection
            self.rfid_reader.close()  # Close the serial port
            self.rfid_reader = None  # Remove reference to force reinitialization

        if self.rfid_thread:
            self.rfid_thread.join()  # Wait for thread to exit
            self.rfid_thread = None  # Reset thread reference

        print("✅ RFID listener has been stopped.")


        print("✅ RFID listener has been stopped.")

    def select_animal_by_id(self, animal_id):
        '''Finds and selects the animal with the given ID in the table, then opens the entry box.'''
        for child in self.table.get_children():
            item_values = self.table.item(child)["values"]
            if str(item_values[0]) == str(animal_id):  # Ensure IDs match as strings
                self.after(0, lambda: self._open_changer_on_main_thread(child))
                return
        
        print(f"⚠️ Animal ID {animal_id} not found in table.")

    def _open_changer_on_main_thread(self, child):
        '''Helper function to safely open the changer on the main thread.'''
        self.table.selection_set(child)  # Select row
        self.changing_value = child
        self.open_changer()  # Open entry box

    def open_auto_increment_changer(self):
        '''Opens auto changer dialog.'''
        if self.table.get_children() :
            self.changing_value = self.table.get_children()[self.auto_inc_id]
            self.open_changer()
        else:
            print("No animals in databse!")
        

    def change_selected_value(self, values):
        '''Updates the table and database, then immediately resumes RFID listening.'''

        item = self.table.item(self.changing_value)
        animal_id = item["values"][0]

        new_values = []
        for val in values:
            new_values.append(val)

        self.table.item(self.changing_value, values=tuple([animal_id] + new_values))

        if "None" in item["values"][1:]:
            self.database.add_data_entry(date.today(), animal_id, new_values)
        else:
            self.database.change_data_entry(date.today(), animal_id, new_values)

        if self.auto_inc_id >= 0 and self.auto_inc_id < len(self.table.get_children()) - 1:
            self.auto_inc_id += 1
            self.open_auto_increment_changer()

        AudioManager.play(filepath="shared/sounds/rfid_success.wav")  # Play success sound

        # Immediately resume RFID listening unless manually stopped
        if not self.rfid_stop_event.is_set():
            print("🔄 Resuming RFID listener...")
            threading.Thread(target=self.rfid_listen, daemon=True).start()



    def get_values_for_date(self, _):
        '''Gets the data for the current date.'''
        self.current_date = str(date.today())
        self.date_label.destroy()
        date_text = "Current Date: " + self.current_date
        self.date_label = CTkLabel(self, text=date_text, font=("Arial", 18))
        self.date_label.place(relx=0.5, rely=0.25, anchor=CENTER)

        values = self.database.get_data_for_date(self.current_date)

        for child in self.table.get_children():
            animal_id = self.table.item(child)["values"][0]
            rfid = self.database.get_animal_rfid(animal_id)  # Fetch RFID
            found_data = False
            for val in values:
                if str(val[1]) == str(animal_id):
                    self.table.item(child, values=tuple([animal_id, rfid] + list(val[2:])))
                    found_data = True
                    break
            if not found_data:
                new_values = [animal_id, rfid]
                for _ in self.measurement_items:
                    new_values.append(None)
                self.table.item(child, values=tuple(new_values))

    def close_connection(self):
        '''Closes database file.'''
        self.database.close()

class ChangeMeasurementsDialog():
    '''Change Measurement Dialog window.'''
    def __init__(self, parent: CTk, data_collection: DataCollectionUI, measurement_items: list):

        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = measurement_items
        self.database = data_collection.database

    def open(self, animal_id):
        '''Opens the change measurement dialog window and handles automated submission.'''
        self.root = root = CTkToplevel(self.parent)

        title_text = "Modify Measurements for: " + str(animal_id)
        root.title(title_text)

        root.geometry('700x700')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        id_label = CTkLabel(root, text="Animal ID: " + str(animal_id), font=("Arial", 18))
        id_label.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.textboxes = []
        count = len(self.measurement_items) + 1

        for i in range(1, count):
            pos_y = i / count
            entry = CTkEntry(root, width=40)
            entry.place(relx=0.60, rely=pos_y, anchor=CENTER)
            self.textboxes.append(entry)

            header = CTkLabel(root, text=self.measurement_items[i - 1] + ": ", font=("Arial", 18))
            header.place(relx=0.28, rely=pos_y, anchor=E)

            if i == 1:
                entry.focus()

                # Start data handling in a separate thread
                data_handler = SerialDataHandler("device")
                data_thread = threading.Thread(target=data_handler.start)
                data_thread.start()

                # Automated handling of data input
                def check_for_data():
                    while True:
                        if len(data_handler.received_data) >= 2:  # Customize condition
                            received_data = data_handler.get_stored_data()
                            entry.insert(1, received_data)
                            data_handler.stop()
                            self.finish()  # Automatically call the finish method
                            break

                threading.Thread(target=check_for_data, daemon=True).start()
            
        self.error_text = CTkLabel(root, text="One or more values are not a number", fg_color="red")

        self.root.mainloop()

    def check_if_num(self, _):
        '''Checks if the values are numbers.'''
        errors = 0
        values = self.get_all_values()
        for value in values:
            try:
                float(value)
            except ValueError:
                self.show_error()
                errors += 1
        if errors == 0:
            self.error_text.place_forget()
            # self.submit_button["state"] = "normal"

    def show_error(self):
        '''Displays an error window if input is invalid.'''
        if self.root.winfo_exists():
            self.error_text.place(relx=0.5, rely=0.85, anchor=CENTER)
            AudioManager.play(filepath="shared/sounds/error.wav")


    def get_all_values(self):
        '''Returns the values of all entries in self.textboxes as an array.'''
        values = []
        for entry in self.textboxes:
            value = str(entry.get())
            value = value.strip()
            if value == "":
                value = "0"
            values.append(value)
        return tuple(values)

    def finish(self):
        '''Cleanup when done with change value dialog.'''
        if self.root.winfo_exists():
            values = self.get_all_values()
            self.close()

            if self.data_collection.winfo_exists():
                self.data_collection.change_selected_value(values)


    def close(self):
        '''Closes change value dialog window.'''
        self.root.destroy()

