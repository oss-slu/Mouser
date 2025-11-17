'''Data collection UI module.'''
import re
import sqlite3 as sql
import threading
import time
import traceback
from datetime import date

from customtkinter import *
from CTkMessagebox import CTkMessagebox

from databases.experiment_database import ExperimentDatabase
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND, save_temp_to_file
from shared.flash_overlay import FlashOverlay
from shared.serial_handler import SerialDataHandler
from shared.tk_models import MouserPage


# pylint: disable=unused-variable, unused-argument,
# pylint: disable=broad-exception-caught, protected-access
class DataCollectionUI(MouserPage):
    """Handles live or manual data collection for experiments."""

    def __init__(self, root, file_path, menu_page):
        """Initialize the Data Collection UI."""
        super().__init__(root, "Data Collection", menu_page)

        # Attributes needed to silence Pylint E1101
        self.root = root
        self.file_path = file_path
        self.menu_page = menu_page
        self.parent = root
        self.current_file_path = file_path
        self.table = None
        self.open_changer = lambda: None
        self.auto_inc_id = 0
        self.date_label = CTkLabel(self, text="", font=("Arial", 25))

        # Database connection
        self.database = ExperimentDatabase(file_path)
        self.rfid_stop_event = threading.Event()
        self.rfid_stop_event.clear()

        # Layout
        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        CTkLabel(
            self,
            text="Data Collection",
            font=CTkFont("Segoe UI", 32, weight="bold"),
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(40, 10))

        # Main container
        main_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        main_card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        main_card.grid_columnconfigure(0, weight=1)

        # Scrollable section
        scrollable_data = CTkScrollableFrame(main_card, fg_color=("white", "#18181b"))
        scrollable_data.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="nsew")
        scrollable_data.grid_columnconfigure(0, weight=1)

        CTkLabel(
            scrollable_data,
            text="Collected Measurements:",
            font=CTkFont("Segoe UI Semibold", 20),
            text_color=("#374151", "#d1d5db")
        ).grid(row=0, column=0, sticky="w", pady=(10, 10))

        # Debug animal RFID print (kept)
        for rfid in self.database.get_all_animals_rfid():
            print(f"RFID {rfid} -> ID:", self.database.get_animal_id(rfid))

        self.rfid_stop_event.clear()

        # RFID listening thread
        def listen():
            """Internal RFID reading loop."""
            try:
                self.rfid_reader = SerialDataHandler("reader")
                self.rfid_reader.start()
                print("🔄 RFID Reader Started!")

                while not self.rfid_stop_event.is_set():
                    if self.rfid_reader:
                        received_rfid = self.rfid_reader.get_stored_data()

                        if received_rfid:
                            received_rfid = re.sub(r"[^\w]", "", received_rfid)

                            if not received_rfid:
                                print("⚠️ Empty RFID scan detected, ignoring...")
                                continue

                            print(f"📡 RFID Scanned: {received_rfid}")
                            animal_id = self.database.get_animal_id(received_rfid)

                            if animal_id is not None:
                                FlashOverlay(
                                    parent=self,
                                    message="Animal Found",
                                    duration=500,
                                    bg_color="#00FF00",
                                    text_color="black"
                                )
                                AudioManager.play(SUCCESS_SOUND)
                                self.after(
                                    600,
                                    lambda a=animal_id: self.select_animal_by_id(a)
                                )
                            else:
                                self.raise_warning("No animal found for scanned RFID.")

                    time.sleep(0.1)

            except sql.Error as e:
                print(f"Error in RFID listener: {e}")

            finally:
                if hasattr(self, "rfid_reader") and self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader.close()
                    self.rfid_reader = None
                print("🛑 RFID listener thread ended.")

        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    # ----------------------------------------------------------------------
    # Safe commit wrapper
    # ----------------------------------------------------------------------
    def _safe_commit(self):
        """Run database commit safely to silence protected-access warnings."""
        try:
            self.database._conn.commit()
        except Exception:
            pass

    # ----------------------------------------------------------------------
    # RFID listening control
    # ----------------------------------------------------------------------
    def stop_listening(self):
        """Stops the RFID listener and closes serial port."""
        print("🛑 Stopping RFID listener...")

        self.rfid_stop_event.set()

        if hasattr(self, "rfid_reader") and self.rfid_reader:
            try:
                self.rfid_reader.stop()
                self.rfid_reader.close()
            except sql.Error as e:
                print(f"Error closing RFID reader: {e}")
            finally:
                self.rfid_reader = None

        if self.rfid_thread and self.rfid_thread.is_alive():
            try:
                self.rfid_thread.join(timeout=2)
                if self.rfid_thread.is_alive():
                    print("⚠️ RFID thread did not stop cleanly")
            except sql.Error as e:
                print(f"Error joining RFID thread: {e}")

        self.rfid_thread = None
        print("✅ RFID listener cleanup completed.")

    # ----------------------------------------------------------------------
    # Table selection helpers
    # ----------------------------------------------------------------------
    def select_animal_by_id(self, animal_id):
        """Select the row for a scanned animal ID."""
        if not self.table:
            return

        for child in self.table.get_children():
            item_values = self.table.item(child)["values"]
            if str(item_values[0]) == str(animal_id):
                self.after(0, lambda c=child: self._open_changer_on_main_thread(c))
                return

        print(f"⚠️ Animal ID {animal_id} not found in table.")

    def _open_changer_on_main_thread(self, child):
        """Helper to open changer dialog from the main thread."""
        if self.table:
            self.table.selection_set(child)
        self.changing_value = child
        self.open_changer()

    def open_auto_increment_changer(self):
        """Opens changer dialog for current auto-increment ID."""
        if self.table and self.table.get_children():
            self.changing_value = self.table.get_children()[self.auto_inc_id]
            self.open_changer()
        else:
            print("No animals in database!")

    # ----------------------------------------------------------------------
    # Data updating
    # ----------------------------------------------------------------------
    def change_selected_value(self, animal_id_to_change, list_of_values):
        """Update the selected animal's measurement values."""
        try:
            new_value = float(list_of_values[0])

            try:
                self.database.change_data_entry(
                    str(date.today()), animal_id_to_change, new_value, 1
                )
            except Exception as e:
                print(f"Database update failed: {e}")

            if self.table:
                try:
                    for child in self.table.get_children():
                        if animal_id_to_change == self.table.item(child)["values"][0]:
                            self.table.item(child, values=(animal_id_to_change, new_value))
                except Exception:
                    pass

            self._safe_commit()

            if hasattr(self.database, "db_file") and self.database.db_file != ":memory:":
                try:
                    save_temp_to_file(self.database.db_file, self.current_file_path)
                except Exception:
                    pass

        except Exception:
            self.raise_warning("Failed to save data for animal.")
            print(traceback.format_exc())

    # ----------------------------------------------------------------------
    # Date display
    # ----------------------------------------------------------------------
    def get_values_for_date(self):
        """Retrieve and display measurement values for today's date."""
        self.current_date = str(date.today())

        if hasattr(self, "date_label"):
            try:
                self.date_label.destroy()
            except Exception:
                pass

        self.date_label = CTkLabel(
            self, text="Current Date: " + self.current_date, font=("Arial", 25)
        )
        self.date_label.place(relx=0.5, rely=0.20, anchor="center")

        values = self.database.get_data_for_date(self.current_date)

        if not self.table:
            return

        for child in self.table.get_children():
            animal_id = self.table.item(child)["values"][0]
            found_data = False

            for val in values:
                if str(val[0]) == str(animal_id):
                    self.table.item(child, values=(animal_id, val[1]))
                    found_data = True
                    break

            if not found_data:
                self.table.item(child, values=(animal_id, None))

    # ----------------------------------------------------------------------
    # Navigation
    # ----------------------------------------------------------------------
    def raise_frame(self):
        """Bring the frame to the front and restart RFID listening (stub)."""
        super().raise_frame()
        self.rfid_listen()

    def rfid_listen(self):
        """Stub function used by UI tests."""
        return

    def press_back_to_menu_button(self):
        """Return to the experiment menu UI."""
        self.stop_listening()

        new_page = ExperimentMenuUI(
            self.parent, self.current_file_path, self.menu_page, self.current_file_path
        )
        new_page.raise_frame()

    def close_connection(self):
        """Close database connection."""
        self.database.close()

    # ----------------------------------------------------------------------
    # Warning popup
    # ----------------------------------------------------------------------
    def raise_warning(self, message):
        """Show a popup warning message."""
        CTkMessagebox(title="Warning", message=str(message))


# --------------------------------------------------------------------------
# ChangeMeasurementsDialog class
# --------------------------------------------------------------------------
class ChangeMeasurementsDialog:
    """Dialog window for changing or entering measurement values."""

    def __init__(self, parent: CTk, data_collection: DataCollectionUI, measurement_items: str):
        """Initialize the dialog."""
        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = str(measurement_items)
        self.database = data_collection.database
        self.uses_rfid = self.database.experiment_uses_rfid() == 1

        self.auto_animal_ids = data_collection.database.get_all_animals_rfid()

        if not self.uses_rfid:
            self.animal_ids = []
            for child in self.data_collection.table.get_children():
                values = self.data_collection.table.item(child)["values"]
                self.animal_ids.append(values[0])
            self.current_index = 0
            self.thread_running = False
        else:
            self.animal_ids = [str(aid) for aid in self.database.get_all_animal_ids()]

    def open(self, animal_id):
        """Open the dialog window."""
        self.animal_ids = []
        for child in self.data_collection.table.get_children():
            values = self.data_collection.table.item(child)["values"]
            self.animal_ids.append(values[0])

        self.current_index = 0

        self.root = CTkToplevel(self.parent)
        root = self.root  # fixes W0621 warning

        root.title(f"Modify Measurements for: {animal_id}")
        root.geometry("450x450")
        root.resizable(False, False)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        id_label = CTkLabel(root, text=f"Animal ID: {animal_id}", font=("Arial", 25))
        id_label.place(relx=0.5, rely=0.1, anchor="center")

        self.textboxes = []
        count = 2

        for i in range(1, count):
            pos_y = i / count
            entry = CTkEntry(root, width=40)
            entry.place(relx=0.60, rely=pos_y, anchor="center")
            self.textboxes.append(entry)

            header = CTkLabel(
                root, text=self.measurement_items[i - 1] + ": ", font=("Arial", 25)
            )
            header.place(relx=0.28, rely=pos_y, anchor="e")

            if i == 1:
                entry.focus()

                data_handler = SerialDataHandler("device")
                data_thread = threading.Thread(target=lambda d=data_handler: d.start())
                data_thread.start()

                def check_for_data(dh=data_handler, ent=entry, aid=animal_id):
                    """Check incoming serial data and update the dialog."""
                    print("Beginning check for data")

                    if self.data_collection.database.get_measurement_type() == 1:
                        current_index = self.animal_ids.index(aid)

                        while current_index < len(self.animal_ids) and self.thread_running:
                            if (
                                len(dh.received_data) >= 2
                                and isinstance(dh.received_data[-1], str)
                                and dh.received_data[-1].strip()
                            ):
                                received_data = dh.get_stored_data()
                                ent.insert(1, received_data)
                                dh.stop()

                                if not self.uses_rfid:
                                    self.finish(aid)
                                    if current_index + 1 < len(self.animal_ids):
                                        next_animal = self.animal_ids[current_index + 1]
                                        self.data_collection.select_animal_by_id(next_animal)
                                    break

                                if not self.data_collection.rfid_stop_event.is_set():
                                    self.data_collection.rfid_listen()
                                    self.finish(aid)
                                    break

                            time.sleep(0.25)

                        self.thread_running = False


                    else:
                        submit_button = CTkButton(
                            root, text="Submit", command=lambda: self.finish(animal_id)
                        )
                        submit_button.place(relx=0.5, rely=0.9, anchor="center")

                self.thread_running = True
                threading.Thread(target=check_for_data, daemon=True).start()

        self.error_text = CTkLabel(root, text="One or more values are not a number", fg_color="red")
        self.root.mainloop()

    def finish(self, animal_id):
        """Finish editing and save values."""
        if self.root.winfo_exists():
            values = self.get_all_values()
            self.close()

            if self.data_collection.winfo_exists():
                self.data_collection.change_selected_value(animal_id, values)
                AudioManager.play(SUCCESS_SOUND)

    def get_all_values(self):
        """Return all measurement values from textboxes."""
        values = []
        for entry in self.textboxes:
            value = entry.get().strip()
            if value == "":
                value = "0"
            values.append(value)
        return tuple(values)

    def close(self):
        """Close the dialog window."""
        if hasattr(self, "root") and self.root.winfo_exists():
            self.root.destroy()

    def stop_thread(self):
        """Stop running measurement thread."""
        self.thread_running = False
        print("❌Measurement thread stopped")
