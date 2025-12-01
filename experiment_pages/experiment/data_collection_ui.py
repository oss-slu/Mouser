"""Data Collection UI Module."""
import re
import sqlite3 as sql
import threading
import time
import traceback
from datetime import date

from customtkinter import *
from CTkMessagebox import CTkMessagebox

from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND, save_temp_to_file
from shared.flash_overlay import FlashOverlay
from shared.serial_handler import SerialDataHandler
from shared.tk_models import MouserPage

class DataCollectionUI(MouserPage):
    """Handles live or manual data collection for active experiments."""

    def __init__(self, parent, prev_page, database_name, file_path: str = ""):
        """Initialize UI."""
        super().__init__(parent, "Data Collection", prev_page)

        self.root = parent
        self.parent = parent
        self.menu_page = prev_page
        self.file_path = file_path or database_name
        self.current_file_path = self.file_path

        self.database = ExperimentDatabase(database_name)

        self.table = None
        self.open_changer = lambda: None
        self.auto_inc_id = 0
        self.changing_value = None

        self.rfid_reader = None
        self.rfid_thread = None
        self.rfid_stop_event = threading.Event()

        self._build_layout()
        self._start_rfid_listener()

    def _build_layout(self):
        """Build visually modern page layout."""
        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        CTkLabel(
            self,
            text="Data Collection",
            font=CTkFont("Segoe UI", 32, weight="bold"),
            text_color=("black", "white"),
        ).grid(row=0, column=0, pady=(40, 10))

        main_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db",
        )
        main_card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        main_card.grid_columnconfigure(0, weight=1)

        scroll = CTkScrollableFrame(main_card, fg_color=("white", "#18181b"))
        scroll.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        CTkLabel(
            scroll,
            text="Collected Measurements:",
            font=CTkFont("Segoe UI Semibold", 20),
            text_color=("#374151", "#d1d5db"),
        ).grid(row=0, column=0, sticky="w", pady=(10, 10))

        for rfid in self.database.get_all_animals_rfid():
            print(f"RFID {rfid} -> ID:", self.database.get_animal_id(rfid))

        self.table = None

    def _start_rfid_listener(self):
        """Begin listening thread for RFID input."""
        self.rfid_stop_event.clear()

        def listen():
            try:
                self.rfid_reader = SerialDataHandler("reader")
                self.rfid_reader.start()
                print("🔄 RFID Reader Started!")

                while not self.rfid_stop_event.is_set():
                    rfid_raw = (
                        self.rfid_reader.get_stored_data()
                        if self.rfid_reader
                        else None
                    )

                    if not rfid_raw:
                        time.sleep(0.1)
                        continue

                    # Clean invalid chars
                    clean = re.sub(r"[^\w]", "", rfid_raw)
                    if not clean:
                        continue

                    print(f"📡 RFID Scanned: {clean}")
                    animal_id = self.database.get_animal_id(clean)

                    if animal_id is None:
                        self.raise_warning("No animal found for scanned RFID.")
                        continue

                    FlashOverlay(
                        parent=self,
                        message="Animal Found",
                        duration=500,
                        bg_color="#00FF00",
                        text_color="black",
                    )
                    AudioManager.play(SUCCESS_SOUND)

                    self.after(600, lambda a=animal_id: self.select_animal_by_id(a))

            except sql.Error as exc:
                print(f"RFID listener SQL Error: {exc}")

            finally:
                if self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader.close()
                self.rfid_reader = None
                print("🛑 RFID listener thread ended.")

        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    def stop_listening(self):
        """Safely stop RFID listener and cleanup."""
        print("🛑 Stopping RFID listener...")
        self.rfid_stop_event.set()

        if self.rfid_reader:
            try:
                self.rfid_reader.stop()
                self.rfid_reader.close()
            except sql.Error:
                pass
            self.rfid_reader = None

        if self.rfid_thread and self.rfid_thread.is_alive():
            self.rfid_thread.join(timeout=2)

        print("✅ RFID listener shutdown complete.")

    def select_animal_by_id(self, animal_id):
        """UI-safe selection of the scanned animal ID."""
        if not self.table:
            return

        for child in self.table.get_children():
            item_id = self.table.item(child)["values"][0]
            if str(item_id) == str(animal_id):
                self.table.selection_set(child)
                self.changing_value = child
                self.open_changer()
                return

        print(f"⚠️ Animal ID {animal_id} not found.")

    def change_selected_value(self, animal_id, list_of_values):
        """Update a given animal ID with new measurement values."""
        try:
            new_value = float(list_of_values[0])

            self.database.change_data_entry(
                str(date.today()), animal_id, new_value, 1
            )

            if self.table:
                for child in self.table.get_children():
                    if animal_id == self.table.item(child)["values"][0]:
                        self.table.item(child, values=(animal_id, new_value))

            self.database.commit()
            save_temp_to_file(self.database.db_file, self.current_file_path)

        except sql.Error:
            print(traceback.format_exc())
            self.raise_warning("Failed to save measurement value.")

    def press_back_to_menu_button(self):
        """Return to the experiment menu UI."""
        self.stop_listening()

        # pylint: disable=import-outside-toplevel
        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI

        new_page = ExperimentMenuUI(
            self.parent,
            self.current_file_path,
            self.menu_page
        )

        new_page.raise_frame()


    def close_connection(self):
        """Close DB connection."""
        self.database.close()

    def raise_warning(self, message):
        """Generic warning popup."""
        CTkMessagebox(title="Warning", message=str(message))

    def rfid_listen(self):
        """Stub function required for UI tests."""
        return

class ChangeMeasurementsDialog:
    """Dialog popup used for modifying a measurement."""

    def __init__(
        self, parent: CTk, data_collection: DataCollectionUI, measurement_items
    ):
        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = str(measurement_items)
        self.database = data_collection.database

        self.uses_rfid = self.database.experiment_uses_rfid() == 1
        self.textboxes = []
        self.thread_running = False
        self.root = None

    def open(self, animal_id):
        """Display popup dialog."""
        self.animal_ids = []
        if self.data_collection.table:
            for child in self.data_collection.table.get_children():
                self.animal_ids.append(
                    self.data_collection.table.item(child)["values"][0]
                )

        self.root = CTkToplevel(self.parent)
        dialog = self.root

        dialog.title(f"Modify Measurements for: {animal_id}")
        dialog.geometry("450x450")
        dialog.resizable(False, False)

        CTkLabel(
            dialog, text=f"Animal ID: {animal_id}", font=("Arial", 25)
        ).place(relx=0.5, rely=0.1, anchor="center")

        entry = CTkEntry(dialog, width=120)
        entry.place(relx=0.60, rely=0.40, anchor="center")
        self.textboxes.append(entry)

        CTkLabel(
            dialog,
            text=f"{self.measurement_items[0]}:",
            font=("Arial", 25),
        ).place(relx=0.28, rely=0.40, anchor="e")

        self.thread_running = True
        handler = SerialDataHandler("device")

        def _reader():
            handler.start()
            while self.thread_running:
                if handler.received_data:
                    val = handler.get_stored_data()
                    if val.strip():
                        entry.insert(0, val.strip())
                        handler.stop()
                        break
                time.sleep(0.25)

        threading.Thread(target=_reader, daemon=True).start()

        submit = CTkButton(
            dialog, text="Submit", command=lambda: self.finish(animal_id)
        )
        submit.place(relx=0.5, rely=0.85, anchor="center")

        dialog.mainloop()

    def finish(self, animal_id):
        """Process dialog result."""
        values = self.get_all_values()
        self.close()

        if self.data_collection.winfo_exists():
            self.data_collection.change_selected_value(animal_id, values)
            AudioManager.play(SUCCESS_SOUND)

    def get_all_values(self):
        """Return measurement entry contents as tuple."""
        vals = []
        for entry in self.textboxes:
            txt = entry.get().strip()
            vals.append(txt if txt else "0")
        return tuple(vals)

    def close(self):
        """Close dialog window safely."""
        self.thread_running = False
        if self.root and self.root.winfo_exists():
            self.root.destroy()

    def raise_frame(self):
        """Compatibility override for pylint."""
        super().raise_frame()

