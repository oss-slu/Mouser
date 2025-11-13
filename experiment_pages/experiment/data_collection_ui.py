'''Data collection UI module.'''
from datetime import date
import threading
import time
import re
import traceback
import sqlite3 as sql

from tkinter.ttk import Treeview, Style
from customtkinter import *
from CTkMessagebox import CTkMessagebox

from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase
from shared.file_utils import SUCCESS_SOUND, ERROR_SOUND, save_temp_to_file
from shared.audio import AudioManager
from shared.scrollable_frame import ScrolledFrame
from shared.serial_handler import SerialDataHandler
from shared.flash_overlay import FlashOverlay


#pylint: disable= undefined-variable
class DataCollectionUI(MouserPage):
    """Handles live or manual data collection for experiments."""

    def __init__(self, root, file_path, menu_page):
        super().__init__(root, "Data Collection", menu_page)
        self.root = root
        self.file_path = file_path

        # --- Layout Setup ---
        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        CTkLabel(
            self,
            text="Data Collection",
            font=CTkFont("Segoe UI", 32, weight="bold"),
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(40, 10))

        # --- Main Card Container ---
        main_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        main_card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        main_card.grid_columnconfigure(0, weight=1)

        # --- Scrollable Data Display ---
        scrollable_data = CTkScrollableFrame(main_card, fg_color=("white", "#18181b"))
        scrollable_data.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="nsew")
        scrollable_data.grid_columnconfigure(0, weight=1)

        CTkLabel(
            scrollable_data,
            text="Collected Measurements:",
            font=CTkFont("Segoe UI Semibold", 20),
            text_color=("#374151", "#d1d5db")
        ).grid(row=0, column=0, sticky="w", pady=(10, 10))

        # Try fetching one by one
        for rfid in self.database.get_all_animals_rfid():
            print(f"RFID {rfid} -> ID:", self.database.get_animal_id(rfid))

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
                            # Keep only alphanumeric characters,
                            # gets rid of spaces and encrypted greeting messages
                            received_rfid = re.sub(r"[^\w]", "", received_rfid)

                            if not received_rfid:
                                print("⚠️ Empty RFID scan detected, ignoring...")
                                continue

                            print(f"📡 RFID Scanned: {received_rfid}")
                            animal_id = self.database.get_animal_id(received_rfid)

                            if animal_id is not None:
                                print(f"✅ Found Animal ID: {animal_id}")
                                FlashOverlay(
                                    parent=self,
                                    message="Animal Found",
                                    duration=500,
                                    bg_color="#00FF00", # Bright Green
                                    text_color="black"
                                )
                                AudioManager.play(SUCCESS_SOUND)
                                self.after(600, lambda a=animal_id: self.select_animal_by_id(a))
                            else:
                                self.raise_warning("No animal found for scanned RFID.")



                    time.sleep(0.1)  # Shorter sleep time for more responsive stopping
            except sql.Error as e:            
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
            except sql.Error as e:
                print(f"Error closing RFID reader: {e}")
            finally:
                self.rfid_reader = None

        # Wait for thread to finish with timeout
        if self.rfid_thread and self.rfid_thread.is_alive():
            try:
                self.rfid_thread.join(timeout=2)  # Wait up to 2 seconds
                if self.rfid_thread.is_alive():
                    print("⚠️ Warning: RFID thread did not stop cleanly")
            except sql.Error as e:
                print(f"Error joining RFID thread: {e}")

        self.rfid_thread = None
        print("✅ RFID listener cleanup completed.")

        # Safely stop and close the changer
        if hasattr(self, 'changer'):
            self.changer.stop_thread()  # Stop the changer thread if it's running
            self.changer.close()  # Close the changer dialog if it's open

    def select_animal_by_id(self, animal_id):
        '''Finds and selects the animal with the given ID in the table, then opens the entry box.'''
        for child in self.table.get_children():
            item_values = self.table.item(child)["values"]
            if str(item_values[0]) == str(animal_id):  # Ensure IDs match as strings
                self.after(0, lambda c = child: self._open_changer_on_main_thread(c))
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
            self.database.change_data_entry(str(date.today()), animal_id_to_change, new_value, 1)
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

                    FlashOverlay(
                        parent=self,
                        message="Data Collected",
                        duration=1000,
                        bg_color="#00FF00", # Bright Green
                        text_color="black"
                    )

                    # If all animals have data for today, show completion message
                    if self.database.is_data_collected_for_date(str(date.today())):
                        self.after(1100, lambda: FlashOverlay(  # Delay to show after the first overlay
                            parent=self,
                            message="All Animals Measured for Today!",
                            duration=4000,
                            bg_color="#FFF700",  # Different color for completion
                            text_color="black"
                        ))


                except sql.Error as save_error:
                    print(f"Autosave failed: {save_error}")
                    print(f"Error type: {type(save_error)}")
                    print(f"Full traceback: {traceback.format_exc()}")
        except Exception as e:
            self.raise_warning("Failed to save data for animal.")
            print(f"Top level error: {e}")
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

    def raise_frame(self):
        '''Raise the frame for this UI'''
        super().raise_frame()
        self.rfid_listen()


    def press_back_to_menu_button(self):
        '''Stops listening and navigates to the new page in ExperimentMenuUI'''
        self.stop_listening()

        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI

        new_page = ExperimentMenuUI(self.parent, self.current_file_path, self.menu_page, self.current_file_path)
        new_page.raise_frame()


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
        # Get all animal IDs from the database
        self.auto_animal_ids = data_collection.database.get_all_animals_rfid()

        if not self.uses_rfid:
            # Get list of all animal IDs from the table
            self.animal_ids = []
            for child in self.data_collection.table.get_children():
                values = self.data_collection.table.item(child)["values"]
                self.animal_ids.append(values[0])  # First column contains animal IDs
            self.current_index = 0  # Track position in animal_ids list
            self.thread_running = False  # Add a flag to control the thread's life cycle

        else:
            self.animal_ids = [str(aid) for aid in self.database.get_all_animal_ids()]

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
                data_thread = threading.Thread(target=lambda d=d: d.start())
                data_thread.start()

                # Automated handling of data input
                def check_for_data():
                    print("Beginning check for data")
                    if self.data_collection.database.get_measurement_type() == 1:
                        current_index = self.animal_ids.index(animal_id)

                        while current_index < len(self.animal_ids) and self.thread_running:
                            if (len(data_handler.received_data) >= 2
                                 and data_handler.received_data != " "
                                 and data_handler.received_data is not None
                                 and data_handler.received_data != 0):
                                received_data = data_handler.get_stored_data()
                                entry.insert(1, received_data)
                                data_handler.stop()

                                if not self.uses_rfid:
                                    # Find current index in animal_ids list
                                    print("Current table index:", current_index)
                                    # If not at the end of the list, move to next animal
                                    self.finish(animal_id)  # Pass animal_id to finish method
                                    if current_index >= len(self.animal_ids):
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
                AudioManager.play(SUCCESS_SOUND)

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
        '''Closes change value dialog window if it exists'''
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.destroy()

    def stop_thread(self):
        '''Stops the data input thread if running.'''
        self.thread_running = False
        print("❌Measurement thread stopped")
