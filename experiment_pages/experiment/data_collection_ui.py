'''Data collection ui module.'''
from datetime import date
from tkinter.ttk import Treeview, Style
import time
from customtkinter import *
from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager
from shared.scrollable_frame import ScrolledFrame
from shared.serial_handler import SerialDataHandler
from shared.file_utils import save_temp_to_file
import threading

#pylint: disable= undefined-variable
class DataCollectionUI(MouserPage):
    '''Page Frame for Data Collection.'''

    def __init__(self, parent: CTk, prev_page: CTkFrame = None, database_name = "", file_path = ""):

        super().__init__(parent, "Data Collection", prev_page)

        self.rfid_reader = None
        self.rfid_stop_event = threading.Event()  # Event to stop RFID listener
        self.rfid_thread = None # Store running thread

        self.current_file_path = file_path

        self.database = ExperimentDatabase(database_name)

        self.measurement_items = self.database.get_measurement_items()

        ## ENSURE ANIMALS ARE IN DATABASE BEFORE EXPERIMENT FOR ALL EXPERIMENTS ##
        if self.database.experiment_uses_rfid() != 1 and self.database.get_animals() == []:
            print("No RFIDs Detected. Filling out Database\n")

            i = 1
            current_group = 1
            max_num_animals = self.database.get_total_number_animals()
            print(f"Total animals to add: {max_num_animals}")

            while i <= max_num_animals:
                # Get cage capacity for current group
                cage_capacity = self.database.get_cage_capacity(current_group)
                print(f"Group {current_group} capacity: {cage_capacity}")

                # Get current number of animals in group
                group_count = self.database.get_group_animal_count(current_group)
                print(f"Current animals in group {current_group}: {group_count}")

                # If current group is full, move to next group
                if group_count >= cage_capacity:
                    print(f"Group {current_group} is full, moving to next group")
                    current_group += 1
                    continue

                # Add animal to current group
                print(f"Adding animal {i} to group {current_group}")
                self.database.add_animal(
                    animal_id=i,
                    rfid=i,     # Keep as integer for RFID
                    group_id=current_group,
                    remarks='',
                )
                i = i + 1


        # # Call the new method to insert blank data for today
        # if len(self.database.get_measurements_by_date(date.today())) == 0:
        #     today_date = str(date.today())
        #     animal_ids = [animal[0] for animal in self.database.get_animals()]  # Get all animal IDs
        #     self.database.insert_blank_data_for_day(animal_ids, today_date)  # Insert blank dataS

        self.measurement_strings = []
        self.measurement_strings.append(self.measurement_items)
        self.measurement_ids = self.database.get_measurement_name()
        print(self.measurement_items)

        if self.database.experiment_uses_rfid() == 0:
            start_function = self.auto_increment
        else:
            start_function = self.rfid_listen




        self.auto_increment_button = CTkButton(self,
                                               text="Start",
                                               compound=TOP,
                                               width=250, height=75,
                                               font=("Georgia", 65),
                                               command= start_function)
        self.auto_increment_button.place(relx=0.35, rely=0.30, anchor=CENTER)
        self.auto_inc_id = -1

        self.stop_button = CTkButton(self,
                                     text="Stop Listening",
                                     compound=TOP,
                                     width=250, height=75,
                                     font=("Georgia", 65),
                                     command= self.stop_listening)
        self.stop_button.place(relx=0.55, rely=0.30, anchor=CENTER)

        self.animals = self.database.get_animals()
        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.50, rely=0.65, anchor=CENTER)



        columns = ['animal_id']
        print(self.database.get_measurement_name())
        columns.append(str(self.database.get_measurement_name())) # Add measurement name as column

        # Initialize the Treeview with the defined columns
        self.table = Treeview(self.table_frame,
                              columns=columns, show='headings',
                              selectmode="browse",
                              height=len(self.animals))

        # Set up the column headings
        style = Style()
        style.configure("Treeview", font=("Arial", 25), rowheight=40)
        style.configure("Treeview.Heading", font=("Arial", 25))

        for i, column in enumerate(columns):

            if i != 0: # i!= 0 means the column will hold measurement data
                text = self.measurement_strings[i-1]
            else: # i == 0, column is for animal id
                text = "Animal ID"

            print(f"Setting heading for column: {column} with text: {text}")  # Debugging line
            if text:  # Only set heading if text is not empty
                self.table.heading(column, text=text)

        # Add the table to the grid
        self.table.grid(row=0, column=0, sticky='nsew')

        self.date_label = CTkLabel(self)

        self.animals = self.database.get_animals()  # Fetches Animal ID and RFID
        for animal in self.animals:
            animal_id = animal[0]
            value = (animal_id, None)  # Initial values with just ID
            self.table.insert('', END, values=value)


        self.get_values_for_date()

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
            try:
                self.rfid_reader = SerialDataHandler("reader")
                self.rfid_reader.start()
                print("🔄 RFID Reader Started!")

                while not self.rfid_stop_event.is_set():
                    if self.rfid_reader:  # Check if reader still exists
                        received_rfid = self.rfid_reader.get_stored_data()

                        if received_rfid:
                            print(f"📡 RFID Scanned: {received_rfid}")
                            animal_id = self.database.get_animal_id(received_rfid)

                            if animal_id is not None:
                                print(f"✅ Found Animal ID: {animal_id}")
                                self.after(0, lambda: self.select_animal_by_id(animal_id))

                    time.sleep(0.1)  # Shorter sleep time for more responsive stopping
            except Exception as e:
                print(f"Error in RFID listener: {e}")
            finally:
                if hasattr(self, 'rfid_reader') and self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader.close()
                    self.rfid_reader = None
                print("🛑 RFID listener thread ended.")

        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    def stop_listening(self):
        '''Stops the RFID listener and ensures the serial port is released.'''
        print("🛑 Stopping RFID listener...")

        # Set the stop event first
        self.rfid_stop_event.set()

        # Stop and close the RFID reader
        if hasattr(self, 'rfid_reader') and self.rfid_reader:
            try:
                self.rfid_reader.stop()
                self.rfid_reader.close()
            except Exception as e:
                print(f"Error closing RFID reader: {e}")
            finally:
                self.rfid_reader = None

        # Wait for thread to finish with timeout
        if self.rfid_thread and self.rfid_thread.is_alive():
            try:
                self.rfid_thread.join(timeout=2)  # Wait up to 2 seconds
                if self.rfid_thread.is_alive():
                    print("⚠️ Warning: RFID thread did not stop cleanly")
            except Exception as e:
                print(f"Error joining RFID thread: {e}")

        self.rfid_thread = None
        print("✅ RFID listener cleanup completed.")

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


    def change_selected_value(self, animal_id_to_change, list_of_values):
        '''Updates the table and database with the new value.'''
        try:
            new_value = float(list_of_values[0])
            print(f"Saving data point for animal {animal_id_to_change}: {new_value}")

            # Write change to database
            self.database.change_data_entry(str(date.today()), animal_id_to_change, new_value)
            print("Database entry updated")

            # Update display table 
            try:
                for child in self.table.get_children():
                    if animal_id_to_change == self.table.item(child)["values"][0]:
                        self.table.item(child, values=(animal_id_to_change, new_value))
                print("Table display updated")
            except Exception as table_error:
                print(f"Error updating table display: {table_error}")

            # Autosave: Commit and save the database file
            if hasattr(self.database, 'db_file') and self.database.db_file != ":memory:":
                try:
                    # Ensure all changes are committed
                    self.database._conn.commit()
                    print("Changes committed")
                    
                    print(f"Attempting to save {self.database.db_file} to {self.current_file_path}")
                    save_temp_to_file(self.database.db_file, self.current_file_path)
                    print("Autosave Success!")
                    
                except Exception as save_error:
                    print(f"Autosave failed: {save_error}")
                    print(f"Error type: {type(save_error)}")
                    import traceback
                    print(f"Full traceback: {traceback.format_exc()}")
        except Exception as e:
            print(f"Top level error: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")

    def get_values_for_date(self):
        '''Gets the data for the current date as a string in YYYY-MM-DD.'''
        self.current_date = str(date.today())
        self.date_label.destroy()
        date_text = "Current Date: " + self.current_date
        self.date_label = CTkLabel(self, text=date_text, font=("Arial", 25))
        self.date_label.place(relx=0.5, rely=0.20, anchor=CENTER)

        # Get all measurements for current date
        values = self.database.get_data_for_date(self.current_date)

        # Update each row in the table
        for child in self.table.get_children():
            animal_id = self.table.item(child)["values"][0]
            found_data = False
            for val in values:
                if str(val[0]) == str(animal_id):  # val[0] is animal_id
                    # Update table with animal_id, rfid, and measurement value
                    self.table.item(child, values=(animal_id, val[1]))  # val[1] is measurement_value
                    found_data = True
                    break

            if not found_data:
                # If no measurement found, show animal_id and rfid with None for measurement
                self.table.item(child, values=(animal_id, None))

    def close_connection(self):
        '''Closes database file.'''
        self.database.close()

class ChangeMeasurementsDialog():
    '''Change Measurement Dialog window.'''
    def __init__(self, parent: CTk, data_collection: DataCollectionUI, measurement_items: str):
        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = str(measurement_items)  # Ensure measurement_items is a single string
        self.database = data_collection.database  # Reference to the updated database
        self.uses_rfid = self.database.experiment_uses_rfid() == 1
        self.thread_running = False

    def open(self, animal_id):
        '''Opens the change measurement dialog window and handles automated submission.'''
         # Initialize animal_ids unconditionally - we need this list for both RFID and non-RFID cases
        self.animal_ids = []
        for child in self.data_collection.table.get_children():
            values = self.data_collection.table.item(child)["values"]
            self.animal_ids.append(values[0])
        self.current_index = 0
        
        self.root = root = CTkToplevel(self.parent)

        title_text = "Modify Measurements for: " + str(animal_id)
        root.title(title_text)

        root.geometry('450x450')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        id_label = CTkLabel(root, text="Animal ID: " + str(animal_id), font=("Arial", 25))
        id_label.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.textboxes = []
        count = 2  # Assuming one measurement item, adjust if needed

        for i in range(1, count):
            pos_y = i / count
            entry = CTkEntry(root, width=40)
            entry.place(relx=0.60, rely=pos_y, anchor=CENTER)
            self.textboxes.append(entry)

            header = CTkLabel(root, text=self.measurement_items[i - 1] + ": ", font=("Arial", 25))
            header.place(relx=0.28, rely=pos_y, anchor=E)

            if i == 1:
                entry.focus()

                # Start data handling in a separate thread
                data_handler = SerialDataHandler("device")
                data_thread = threading.Thread(target=data_handler.start)
                data_thread.start()

                # Automated handling of data input
                def check_for_data():
                    print("Beginning check for data")
                    if self.data_collection.database.get_measurement_type() == 1:
                        print("Inside the if statement")

                        if animal_id = len(self.animal_ids) + 1:
                            current_index = len(self.animal_ids) + 1
                        else:
                            current_index = self.animal_ids.index(animal_id)

                        while current_index < len(self.animal_ids) and self.thread_running:
                            if len(data_handler.received_data) >= 2:  # Customize condition
                                received_data = data_handler.get_stored_data()
                                entry.insert(1, received_data)
                                data_handler.stop()

                                if not self.uses_rfid:
                                    # Find current index in animal_ids list
                                    print("Current table index:", current_index)
                                    # If not at the end of the list, move to next animal
                                    self.finish(animal_id)  # Pass animal_id to finish method
                                    if current_index >= len(self.animal_ids):
                                        print("closing!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                                        data_thread.join()
                                        break
                                    else:
                                        if current_index + 1 < len(self.animal_ids): # If there are more animals
                                            next_animal_id = self.animal_ids[current_index + 1]
                                            self.data_collection.select_animal_by_id(next_animal_id)
                                            break
                                        else: # End of animal list, pass value to exit while loop
                                            next_animal_id = len(self.animal_ids) + 1
                                            self.data_collection.select_animal_by_id(next_animal_id)
                                            break

                                else:
                                    # Resume RFID listening if in RFID mode
                                    if not self.data_collection.rfid_stop_event.is_set():
                                        self.data_collection.rfid_listen()
                                        self.finish(animal_id)  # Pass animal_id to finish method
                                        break

                                time.sleep(.25)

                        # Stop the thread once max measurements are reached
                        self.thread_running = False
                        print("Thread finished")

                    else:
                        submit_button = CTkButton(root, text="Submit", command=lambda: self.finish(animal_id))
                        submit_button.place(relx=0.5, rely=0.9, anchor=CENTER)

                self.thread_running = True  # Set flag to True when the thread starts
                threading.Thread(target=check_for_data, daemon=True).start()


        self.error_text = CTkLabel(root, text="One or more values are not a number", fg_color="red")
        self.root.mainloop()

    def finish(self, animal_id):
        '''Cleanup when done with change value dialog.'''
        if self.root.winfo_exists():
            values = self.get_all_values()
            self.close()

            current_animal_id = animal_id

            if self.data_collection.winfo_exists():
                # Update the database with the new values
                self.data_collection.change_selected_value(current_animal_id, values)

    def get_all_values(self):
        '''Returns the values of all entries in self.textboxes as an array.'''
        values = []
        for entry in self.textboxes:
            value = str(entry.get()).strip()
            if value == "":
                value = "0"
            values.append(value)
        return tuple(values)

    def close(self):
        '''Closes change value dialog window.'''
        self.root.destroy()
