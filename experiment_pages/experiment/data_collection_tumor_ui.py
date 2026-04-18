"""Tumor-level data collection UI."""
from datetime import date
import re
import time
import threading
from tkinter.ttk import Treeview, Style

from customtkinter import (
    CTkFont,
    CTkFrame,
    CTkButton,
    CTkLabel,
    CTkScrollbar,
    CTkInputDialog,
    CENTER,
    VERTICAL,
)
from CTkMessagebox import CTkMessagebox

from shared.tk_models import MouserPage, get_ui_metrics
from shared.serial_handler import SerialDataHandler
from shared.flash_overlay import FlashOverlay
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND, ERROR_SOUND, save_temp_to_file
from databases.experiment_database import ExperimentDatabase


class TumorDataCollectionUI(MouserPage):
    """Tumor measurement collection UI."""

    def __init__(self, parent, prev_page=None, database_name="", file_path=""):
        super().__init__(parent, "Tumor Data Collection", prev_page)
        ui = get_ui_metrics()
        self._ui = ui
        action_button_font = CTkFont("Segoe UI Semibold", ui["action_font_size"])
        table_font_size = ui["table_font_size"]

        self.parent = parent
        self.menu_page = prev_page
        self.current_file_path = file_path
        self.database = ExperimentDatabase(database_name)

        self.rfid_reader = None
        self.rfid_stop_event = threading.Event()
        self.rfid_thread = None
        self._measurement_in_progress = False
        self._auto_after = False
        self._auto_target_animal = None

        self.current_date = str(date.today())
        self.calc_method = self.database.get_calc_method()
        self.uses_rfid = self.database.experiment_uses_rfid() == 1

        self._ensure_animals_and_tumors()

        start_function = self.rfid_listen if self.uses_rfid else self.auto_increment
        start_button_text = "Start Scanning" if self.uses_rfid else "Start"

        self.auto_increment_button = CTkButton(
            self,
            text=start_button_text,
            compound="top",
            width=ui["action_width"],
            height=ui["action_height"],
            font=action_button_font,
            command=start_function,
        )
        self.auto_increment_button.place(relx=0.28, rely=0.30, anchor=CENTER)

        self.stop_button = CTkButton(
            self,
            text="Stop Listening",
            compound="top",
            width=ui["action_width"],
            height=ui["action_height"],
            font=action_button_font,
            command=self.stop_listening,
        )
        self.stop_button.place(relx=0.48, rely=0.30, anchor=CENTER)
        self.stop_button.configure(state="disabled")

        self.dead_button = CTkButton(
            self,
            text="Mark Dead",
            width=ui["action_width"],
            height=ui["action_height"],
            font=action_button_font,
            fg_color="#dc2626",
            hover_color="#991b1b",
            command=lambda: self.mark_selected_animal_status("dead"),
        )
        self.dead_button.place(relx=0.68, rely=0.30, anchor=CENTER)

        self.censored_button = CTkButton(
            self,
            text="Mark Censored",
            width=ui["action_width"],
            height=ui["action_height"],
            font=action_button_font,
            fg_color="#d97706",
            hover_color="#b45309",
            command=lambda: self.mark_selected_animal_status("censored"),
        )
        self.censored_button.place(relx=0.88, rely=0.30, anchor=CENTER)

        self.status_label = CTkLabel(
            self,
            text=f"Status: Ready ({self.current_date})",
            font=("Arial", max(14, ui["label_font_size"])),
            text_color=("#1f2937", "#d1d5db"),
        )
        self.status_label.place(relx=0.5, rely=0.39, anchor=CENTER)

        self.table_frame = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=14,
            border_width=1,
            border_color="#d1d5db",
        )
        self.table_frame.place(relx=0.50, rely=0.68, relheight=0.44, relwidth=0.80, anchor=CENTER)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        columns = ["animal_id", "tumor", "length", "width", "status"]
        self.table = Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=15,
            style="TumorCollection.Treeview",
        )
        style = Style()
        style.configure("TumorCollection.Treeview", font=("Arial", table_font_size), rowheight=ui["table_row_height"] + 4)
        style.configure("TumorCollection.Treeview.Heading", font=("Arial", table_font_size, "bold"))
        style.map("TumorCollection.Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", "#111827")])

        self.table.heading("animal_id", text="Animal ID", anchor="center")
        self.table.heading("tumor", text="Tumor", anchor="center")
        self.table.heading("length", text="Length", anchor="center")
        self.table.heading("width", text="Width", anchor="center")
        self.table.heading("status", text="Status", anchor="center")
        for col in columns:
            self.table.column(col, anchor="center", width=150, stretch=True)

        self.table.grid(row=0, column=0, sticky="nsew")
        table_scroll = CTkScrollbar(self.table_frame, orientation=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=table_scroll.set)
        table_scroll.grid(row=0, column=1, sticky="ns")

        self.table.bind("<<TreeviewSelect>>", self.item_selected)
        self.table.bind("<Double-1>", self._open_selected_for_edit)

        self.tumor_rows = []
        self._populate_table()

        self.auto_inc_idx = 0
        self.selected_tumor_id = None

    def _ensure_animals_and_tumors(self):
        if self.database.get_animals() == [] and not self.uses_rfid:
            # Auto-create animals based on experiment counts
            i = 1
            current_group = 1
            max_num_animals = self.database.get_total_number_animals()
            while i <= max_num_animals:
                cage_capacity = self.database.get_cage_capacity(current_group)
                group_count = self.database.get_group_animal_count(current_group)
                if group_count >= cage_capacity:
                    current_group += 1
                    continue
                self.database.add_animal(
                    animal_id=i,
                    rfid=i,
                    group_id=current_group,
                    remarks="",
                )
                i += 1

        # Ensure tumors exist for all animals
        for animal_id, _rfid in self.database.get_animals():
            self.database.ensure_tumors_for_animal(animal_id)

    def _populate_table(self):
        self.table.delete(*self.table.get_children())
        self.tumor_rows = self.database.get_all_tumors()
        for tumor_id, animal_id, _group_id, _cage_id, _tumor_index, label, _order in self.tumor_rows:
            length, width, status = (None, None, None)
            existing = self.database.get_tumor_measurement(tumor_id, self.current_date)
            if existing:
                length, width, status = existing
            display_status = status or ""
            self.table.insert(
                "",
                "end",
                iid=str(tumor_id),
                values=(animal_id, label, length, width, display_status),
            )

    def item_selected(self, _):
        selected = self.table.selection()
        if selected:
            self.selected_tumor_id = int(selected[0])

    def _open_selected_for_edit(self, _):
        selected = self.table.selection()
        if selected:
            self.selected_tumor_id = int(selected[0])
            self._open_measurement_dialog(self.selected_tumor_id)

    def _open_measurement_dialog(self, tumor_id):
        # Manual entry fallback
        self._auto_after = False
        length_val = self._prompt_value("Enter Length (mm):")
        if length_val is None:
            return
        width_val = None
        if self.calc_method != 10:
            width_val = self._prompt_value("Enter Width (mm):")
            if width_val is None:
                return
        else:
            width_val = 1.0
        self._save_measurement(tumor_id, length_val, width_val)

    def _prompt_value(self, prompt_text):
        dialog = CTkInputDialog(title="Measurement Entry", text=prompt_text)
        user_input = dialog.get_input() if dialog else None
        if user_input is None:
            return None
        try:
            val = float(str(user_input).strip())
            if val < 0:
                self.raise_warning("Measurements must be non-negative.")
                return None
            return val
        except ValueError:
            self.raise_warning("Invalid measurement value.")
            return None

    def _save_measurement(self, tumor_id, length, width):
        existing = self.database.get_tumor_measurement(tumor_id, self.current_date)
        if existing:
            confirm = CTkMessagebox(
                title="Overwrite?",
                message="A measurement already exists for this tumor today. Overwrite it?",
                option_1="No",
                option_2="Yes",
            )
            if confirm.get() != "Yes":
                self.set_status("Overwrite cancelled.")
                return
        self.database.upsert_tumor_measurement(
            tumor_id=tumor_id,
            date_measured=self.current_date,
            length=length,
            width=width,
            status="measured",
        )
        self._update_row(tumor_id, length, width, "measured")
        self._autosave()
        FlashOverlay(
            parent=self,
            message="Measurement Saved",
            duration=1000,
            bg_color="#00FF00",
            text_color="black",
        )
        if self._auto_after:
            self.after(150, lambda: self._open_next_unmeasured_tumor(self._auto_target_animal))

    def _update_row(self, tumor_id, length, width, status):
        if self.table.exists(str(tumor_id)):
            values = list(self.table.item(str(tumor_id))["values"])
            values[2] = length
            values[3] = width
            values[4] = status
            self.table.item(str(tumor_id), values=values)

    def _autosave(self):
        if hasattr(self.database, "db_file") and self.database.db_file != ":memory:":
            try:
                self.database._conn.commit()
                save_temp_to_file(self.database.db_file, self.current_file_path)
            except Exception as exc:
                print(f"Autosave failed: {exc}")

    def set_status(self, text):
        if self.winfo_exists():
            self.after(0, lambda: self.status_label.configure(text=f"Status: {text}"))

    def auto_increment(self):
        self.auto_inc_idx = 0
        self._auto_after = True
        self._auto_target_animal = None
        self._open_next_unmeasured_tumor()

    def _open_next_unmeasured_tumor(self, animal_id=None):
        # Find next unmeasured tumor (optionally for animal)
        for tumor_id, animal_id_row, *_rest in self.tumor_rows:
            if animal_id is not None and int(animal_id_row) != int(animal_id):
                continue
            existing = self.database.get_tumor_measurement(tumor_id, self.current_date)
            if not existing:
                self.selected_tumor_id = int(tumor_id)
                self.table.selection_set(str(tumor_id))
                self._capture_measurement_for_tumor(tumor_id, animal_id=animal_id)
                return
        self.set_status("No unmeasured tumors remaining.")

    def _capture_measurement_for_tumor(self, tumor_id, animal_id=None):
        if self._measurement_in_progress:
            return
        self._auto_after = True
        self._auto_target_animal = animal_id
        self._measurement_in_progress = True
        self.set_status(f"Capturing measurement for tumor {tumor_id}...")

        def run_capture():
            length, width = self._read_two_values_from_device(timeout_seconds=5.0)
            if length is None:
                self.after(0, lambda: self._open_measurement_dialog(tumor_id))
            else:
                self.after(0, lambda: self._save_measurement(tumor_id, length, width))
            self._measurement_in_progress = False

        threading.Thread(target=run_capture, daemon=True).start()

    def _read_two_values_from_device(self, timeout_seconds=5.0):
        data_handler = None
        try:
            data_handler = SerialDataHandler("device")
            data_handler.start()
            values = []
            start_time = time.monotonic()
            while time.monotonic() - start_time < timeout_seconds and len(values) < 2:
                raw = data_handler.get_stored_data()
                if raw:
                    match = re.search(r"-?\d+(?:\.\d+)?", str(raw))
                    if match:
                        val = float(match.group(0))
                        if val < 0:
                            continue
                        values.append(val)
                        if self.calc_method == 10:
                            break
                time.sleep(0.1)
            if not values:
                return None, None
            if self.calc_method == 10:
                return values[0], 1.0
            if len(values) < 2:
                return None, None
            return values[0], values[1]
        except Exception:
            return None, None
        finally:
            if data_handler:
                data_handler.stop()

    def rfid_listen(self):
        if not self.uses_rfid:
            self.set_status("RFID is disabled for this experiment.")
            return
        if self.rfid_thread and self.rfid_thread.is_alive():
            self.set_status("RFID listener already running.")
            return
        self.set_status("Starting RFID listener...")
        self.auto_increment_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.rfid_stop_event.clear()

        def listen():
            try:
                self.rfid_reader = SerialDataHandler("reader")
                self.rfid_reader.start()
                while not self.rfid_stop_event.is_set():
                    received_rfid = self.rfid_reader.get_stored_data()
                    if received_rfid:
                        received_rfid = re.sub(r"[^\w]", "", received_rfid)
                        if not received_rfid:
                            continue
                        animal_id = self.database.get_animal_id(received_rfid)
                        if animal_id is not None:
                            self.after(0, lambda aid=animal_id: self._open_next_unmeasured_tumor(aid))
                        else:
                            self.raise_warning("No animal found for scanned RFID.")
                    time.sleep(0.1)
            finally:
                if self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader.close()
                    self.rfid_reader = None
                self.auto_increment_button.configure(state="normal")
                self.stop_button.configure(state="disabled")
                self.set_status("Listener stopped.")

        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    def stop_listening(self):
        self.rfid_stop_event.set()
        if self.rfid_reader:
            try:
                self.rfid_reader.stop()
                self.rfid_reader.close()
            except Exception:
                pass
            self.rfid_reader = None
        self.auto_increment_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.set_status("Listener stopped.")

    def mark_selected_animal_status(self, status):
        selected = self.table.selection()
        if not selected:
            self.raise_warning("Select a tumor row first.")
            return
        tumor_id = int(selected[0])
        # Find animal for tumor
        row = next((r for r in self.tumor_rows if int(r[0]) == tumor_id), None)
        if not row:
            return
        animal_id = row[1]
        tumors = [t for t in self.tumor_rows if int(t[1]) == int(animal_id)]
        for t in tumors:
            t_id = t[0]
            existing = self.database.get_tumor_measurement(t_id, self.current_date)
            if existing and existing[2] == "measured":
                continue
            self.database.upsert_tumor_measurement(
                tumor_id=t_id,
                date_measured=self.current_date,
                length=None,
                width=None,
                status=status,
            )
            self._update_row(t_id, None, None, status)
        self._autosave()
        self.set_status(f"Marked animal {animal_id} as {status}.")

    def raise_warning(self, warning_message="An error occurred"):
        CTkMessagebox(title="Warning", message=warning_message, icon="warning")
        AudioManager.play(ERROR_SOUND)
