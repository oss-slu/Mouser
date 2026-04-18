'''Map RFID module.'''
import time
import platform
import shutil
import subprocess
import re
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
from shared.file_utils import SUCCESS_SOUND, ERROR_SOUND
from shared.tk_models import *
from shared.serial_port_controller import SerialPortController
from shared.serial_handler import SerialDataHandler
from shared.hid_wedge import HIDWedgeListener

from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager

import shared.file_utils as file_utils
from shared.flash_overlay import FlashOverlay

class RFIDHandler:
    def __init__(self):
        # initialize serial port and flags
        try:
            self.rfid_serial_port_controller = SerialPortController("reader")
            self.flag_listening = False
            self.thread = None
            self.content = None
        except Exception as e:
            print(f"An exception occurred {e}")
            self.flag_listening = False



    def start_listening(self):
        # start hardware RFID scanning in a thread
        self.thread = threading.Thread(target=self.scan_rfid)
        if self.flag_listening is False:
            self.flag_listening = True
            self.thread.start()

    def stop_listening(self):
        # stop thread and clean up resources
        if self.flag_listening is True:
            self.flag_listening = False
            self.thread.join()
            self.rfid_serial_port_controller.close()
        

    def scan_rfid(self):
        # loop and read RFID data
        while self.flag_listening is True:
            self.content = self.rfid_serial_port_controller.read_data()
            if self.content:
                print("Valid data")
            else:
                try:
                    print(self.content)
                except Exception as e:
                    print(f"An exception occurred: {e}")

            time.sleep(0.1)  

def simulate_rfid():
    # generate fake RFID for testing
    process_id = os.getpid()
    random_id = get_random_rfid()
    print(random_id)
    print(process_id)
    return random_id

def get_random_rfid():
    '''Returns a simulated rfid number'''
    return random.randint(1000000000, 9999999999)

class MapRFIDPage(MouserPage):# pylint: disable= undefined-variable
    '''Map RFID user interface and window.'''
    def __init__(self, database, parent: CTk, previous_page: CTkFrame = None, file_path = ""):

        super().__init__(parent, "RFID Mapping", previous_page)
        ui = get_ui_metrics()
        self._ui = ui
        action_button_font = CTkFont("Segoe UI Semibold", ui["nav_font_size"])
        is_dark = get_appearance_mode().lower() == "dark"

        def _pick(color_value):
            if isinstance(color_value, (tuple, list)) and len(color_value) >= 2:
                return color_value[1] if is_dark else color_value[0]
            return color_value

        self._palette = {
            "page_bg": ("#eef2ff", "#0b1220"),
            "card_bg": ("#ffffff", "#101827"),
            "card_border": ("#c7d2fe", "#22304a"),
            "text": ("#0f172a", "#e5e7eb"),
            "muted_text": ("#334155", "#cbd5e1"),
            "table_bg": ("#f0f9ff", "#0b1220"),
            "table_alt_bg": ("#e0f2fe", "#0f172a"),
            "table_header_bg": ("#0284c7", "#0369a1"),
            "table_header_fg": ("#ffffff", "#ffffff"),
            "table_selected_bg": ("#0ea5e9", "#0ea5e9"),
            "table_selected_fg": ("#ffffff", "#ffffff"),
        }
        self.configure(fg_color=self._palette["page_bg"])

        self._button_styles = {
            "primary": {"fg_color": "#4f46e5", "hover_color": "#4338ca", "text_color": "white"},
            "info": {"fg_color": "#0ea5e9", "hover_color": "#0284c7", "text_color": "white"},
            "success": {"fg_color": "#16a34a", "hover_color": "#15803d", "text_color": "white"},
            "warning": {"fg_color": "#f59e0b", "hover_color": "#d97706", "text_color": "#111827"},
            "neutral": {"fg_color": "#64748b", "hover_color": "#475569", "text_color": "white"},
            "danger": {"fg_color": "#ef4444", "hover_color": "#dc2626", "text_color": "white"},
        }
        self._disabled_button_style = {
            "fg_color": "#cbd5e1",
            "hover_color": "#cbd5e1",
            "text_color": "#64748b",
        }
        if is_dark:
            self._disabled_button_style = {
                "fg_color": "#1f2937",
                "hover_color": "#1f2937",
                "text_color": "#64748b",
            }

        self.rfid_reader = None
        self.rfid_stop_event = threading.Event()  # Event to stop RFID listener
        self.rfid_thread = None # Store running thread
        self.hid_listener = None
        self.use_hid_fallback = False
        self._serial_first_data_timeout = 8.0
        self._recent_tag = None
        self._recent_tag_time = 0.0

        # Store the parent reference
        self.parent = parent

        file = database
        self.db = ExperimentDatabase(file)

        self.animal_rfid_list = self.db.get_all_animals_rfid()
        self.animals = []
        self.animal_id = 1
        
        self.animal_id_entry_text = StringVar(value="1")

        self._scanning_active = False

        title_font = CTkFont(family="Segoe UI Semibold", size=26)
        stat_title_font = CTkFont("Segoe UI Semibold", max(10, ui["label_font_size"] - 3))
        stat_value_font = CTkFont("Segoe UI Semibold", max(18, ui["label_font_size"] + 10))

        # Header (match `new_experiment_ui.py` pattern: transparent frame + packed title/subtitle)
        subtitle_font = CTkFont(family="Segoe UI", size=14)
        header = CTkFrame(self, fg_color="transparent")
        header.place(relx=0.0, rely=0.0, x=48, y=72, anchor="nw")
        title_row = CTkFrame(header, fg_color="transparent")
        title_row.pack(anchor="w")
        self.page_title_icon = CTkLabel(
            title_row,
            # Avoid the emoji-variation selector (U+FE0F) here; Tk can measure it as extra width,
            # which creates an oversized gap before the title label on some systems.
            text="\U0001f3f7",
            font=title_font,
            text_color=self._palette["text"],
            width=0,
        )
        self.page_title_icon.pack(side="left", padx=(0, 4))
        self.page_title_label = CTkLabel(
            title_row,
            text="RFID Mapping",
            font=title_font,
            text_color=self._palette["text"],
        )
        self.page_title_label.pack(side="left")
        self.page_subtitle_label = CTkLabel(
            header,
            text="Map animals to RFID tags ✨",
            font=subtitle_font,
            text_color=self._palette["muted_text"],
        )
        self.page_subtitle_label.pack(anchor="w", pady=(2, 0))

        self.reader_status_chip = CTkFrame(
            self,
            fg_color=self._palette["card_bg"],
            corner_radius=18,
            border_width=1,
            border_color=self._palette["card_border"],
            width=300,
        )
        self.reader_status_chip.place(relx=0.95, rely=0.08, anchor="ne")
        self.reader_status_chip_label = CTkLabel(
            self.reader_status_chip,
            text="Reader: Idle",
            font=CTkFont("Segoe UI Semibold", max(12, ui["label_font_size"])),
            text_color=self._palette["muted_text"],
            wraplength=260,
            justify="left",
        )
        self.reader_status_chip_label.pack(padx=14, pady=6)

        # Summary cards
        self.summary_frame = CTkFrame(self, fg_color="transparent")
        self.summary_frame.place(relx=0.05, rely=0.23, relwidth=0.90, relheight=0.12, anchor="nw")

        def _build_stat_card(relx, title_text, accent_color, bg_color):
            card = CTkFrame(
                self.summary_frame,
                fg_color=bg_color,
                corner_radius=14,
                border_width=1,
                border_color=self._palette["card_border"],
            )
            card.place(relx=relx, rely=0.0, relwidth=0.30, relheight=1.0, anchor="nw")
            CTkFrame(card, height=6, corner_radius=14, fg_color=accent_color).pack(fill="x")
            CTkLabel(
                card,
                text=title_text,
                font=stat_title_font,
                text_color=accent_color,
            ).place(x=14, y=14, anchor="nw")
            value_label = CTkLabel(
                card,
                text="0",
                font=stat_value_font,
                text_color=self._palette["text"],
            )
            value_label.place(x=14, y=46, anchor="nw")
            return value_label

        self.total_animals_value = _build_stat_card(0.00, "ANIMALS", "#3b82f6", ("#eff6ff", "#0b1b35"))
        self.scanned_value = _build_stat_card(0.35, "SCANNED", "#22c55e", ("#ecfdf5", "#042f2e"))
        self.pending_value = _build_stat_card(0.70, "PENDING", "#f59e0b", ("#fffbeb", "#2e1f0a"))

        # Single Start/Stop scanning toggle button
        self.scan_toggle_button = CTkButton(
            self,
            text="▶ Start scanning",
            compound=TOP,
            width=ui["action_width"] + 40,
            height=ui["action_height"],
            font=action_button_font,
            command=self.toggle_scanning,
        )
        setattr(self.scan_toggle_button, "_mouser_variant", "success")
        self.scan_toggle_button.place(relx=0.50, rely=0.42, anchor=CENTER)

        self.table_frame = CTkFrame(
            self,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        self.table_frame.place(relx=0.05, rely=0.49, relheight=0.35, relwidth=0.90, anchor="nw")
        self.table_frame.grid_columnconfigure(0, weight= 1)
        self.table_frame.grid_rowconfigure(0, weight= 1)

        self.file_path = file_path

        table_style = Style()
        # On Windows, the default ttk theme (vista/xpnative) can ignore heading background colors.
        # Switch to a theme that honors `Treeview.Heading` styling so header colors apply.
        try:
            if table_style.theme_use() in {"vista", "xpnative"}:
                table_style.theme_use("clam")
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        table_style.configure(
            "MapRFID.Treeview",
            background=_pick(self._palette["table_bg"]),
            fieldbackground=_pick(self._palette["table_bg"]),
            foreground=_pick(self._palette["text"]),
            rowheight=ui["table_row_height"],
            font=("Segoe UI", max(12, ui["table_font_size"])),
            borderwidth=0,
        )
        table_style.configure(
            "MapRFID.Treeview.Heading",
            background=_pick(self._palette["table_header_bg"]),
            foreground=_pick(self._palette["table_header_fg"]),
            font=("Segoe UI Semibold", max(12, ui["table_font_size"])),
            relief="flat",
            padding=(10, 6),
        )
        table_style.map(
            "MapRFID.Treeview",
            background=[("selected", _pick(self._palette["table_selected_bg"]))],
            foreground=[("selected", _pick(self._palette["table_selected_fg"]))],
        )
        table_style.map(
            "MapRFID.Treeview.Heading",
            background=[("active", _pick(self._palette["table_selected_bg"]))],
            foreground=[("active", _pick(self._palette["table_selected_fg"]))],
        )

        columns = ('animal_id', 'rfid')
        self.table = Treeview(
            self.table_frame, columns=columns, show='headings', height=10, style='MapRFID.Treeview')
        self.table.tag_configure("text_font", font=("Segoe UI", max(12, ui["table_font_size"])))
        self.table.tag_configure("even_row", background=_pick(self._palette["table_bg"]))
        self.table.tag_configure("odd_row", background=_pick(self._palette["table_alt_bg"]))

        self.table.heading('animal_id', text='Animal ID')
        self.table.heading('rfid', text='RFID Tag')
        self.table.column('animal_id', anchor='center')
        self.table.column('rfid', anchor='center')
        self.table.heading('animal_id', anchor='center')
        self.table.heading('rfid', anchor='center')

        self.table.grid(row=0, column=0, sticky='nsew', padx=(12, 0), pady=12)
        self.table.grid_columnconfigure(0, weight = 1)
        self.table.grid_rowconfigure(0, weight = 1)


        scrollbar = CTkScrollbar(self.table_frame, orientation=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.configure(
            fg_color=_pick(self._palette["card_bg"]),
            button_color=_pick(self._palette["card_border"]),
            button_hover_color=_pick(self._palette["table_selected_bg"]),
        )
        scrollbar.grid(row=0, column=1, sticky='ns', padx=(0, 12), pady=12)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        self.right_click = Menu(self, tearoff=0)
        try:
            self.right_click.configure(
                background=_pick(self._palette["card_bg"]),
                foreground=_pick(self._palette["text"]),
                activebackground=_pick(self._palette["table_selected_bg"]),
                activeforeground=_pick(self._palette["table_selected_fg"]),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        self.right_click.add_command(
            label="Remove Selection(s)", command=self.remove_selected_items)
        self.table.bind("<Button-3>", self.right_click_menu)

        self.delete_button = CTkButton(self, text="Remove Selection(s)", compound=TOP,
                                       width=ui["action_width"], height=ui["action_height"],
                                       font=action_button_font, command=self.remove_selected_items,
                                       state="normal")  # Initialize button as disabled
        setattr(self.delete_button, "_mouser_variant", "neutral")
        self.delete_button.place(relx=0.20, rely=0.90, anchor=CENTER)
        self._set_button_enabled(self.delete_button, True)

        # Add Sacrifice button with normal state
        self.sacrifice_button = CTkButton(self, text="Sacrifice Selected", compound=TOP,
                                      width=ui["action_width"], height=ui["action_height"],
                                      font=action_button_font, command=self.sacrifice_selected_items,
                                      state="normal")  # Initialize as enabled
        setattr(self.sacrifice_button, "_mouser_variant", "danger")
        self.sacrifice_button.place(relx=0.50, rely=0.90, anchor=CENTER)
        self._set_button_enabled(self.sacrifice_button, True)

        self.simulate_all_rfid_button = CTkButton(
            self,
            text="Simulate ALL RFID",
            compound=TOP,
            width=ui["action_width"],
            height=ui["action_height"],
            font=action_button_font,
            command=self.simulate_all_rfid,
        )
        setattr(self.simulate_all_rfid_button, "_mouser_variant", "info")
        self.simulate_all_rfid_button.place(relx=0.82, rely=0.90, anchor=CENTER)
        self._set_button_enabled(self.simulate_all_rfid_button, True)

        self.item_selected(None)

        animals_setup = self.db.get_all_animal_ids()
        for row_index, animal in enumerate(animals_setup):
            rfid = self.db.get_animal_rfid(animal)
            value = (int(animal), rfid)
            row_tag = "even_row" if row_index % 2 == 0 else "odd_row"
            self.table.insert('', END, values=value, tags=("text_font", row_tag))
            self.animals.append(value)
            self.animal_id_entry_text.set(animal)

        self._refresh_summary_cards()
        if self.db.experiment_uses_rfid() == 0:
            self._set_button_enabled(self.scan_toggle_button, False)
        else:
            self._set_scanning_state(False)

        ##setting previous button behavior
        self.menu_page = previous_page

        if not self.menu_button and previous_page:
            self.set_menu_button(previous_page)

        if self.menu_button:
            self.menu_button.configure(command=self.press_back_to_menu_button)
        # Match back-button styling from `new_experiment_ui.py` for visual consistency.
        try:
            if self.menu_button:
                self.menu_button.configure(
                corner_radius=12,
                height=40,
                width=54,
                text="\u2B05",
                font=("Segoe UI Semibold", 20),
                text_color="white",
                fg_color="#f59e0b",
                hover_color="#d97706",
                )
                self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=8, anchor="nw")
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        self.scroll_to_latest_entry()
        if self.db.experiment_uses_rfid() == 0:
            self.set_reader_status("RFID disabled for this experiment.")

    def set_reader_status(self, status_text):
        """Update reader status text safely on the UI thread."""
        def _update():
            if hasattr(self, "reader_status_label") and self.reader_status_label.winfo_exists():
                self.reader_status_label.configure(text=str(status_text) if status_text else "")
            if hasattr(self, "reader_status_chip_label") and self.reader_status_chip_label.winfo_exists():
                self.reader_status_chip_label.configure(text=f"Reader: {self._status_chip_text(status_text)}")

        if self.winfo_exists():
            self.after(0, _update)

    def _status_chip_text(self, status_text):
        """Return the status text for the header chip."""
        text = (status_text or "").strip()
        if not text:
            return "Idle"
        return text

    def _refresh_summary_cards(self):
        """Update ANIMALS / SCANNED / PENDING cards."""
        try:
            total = int(self.db.get_total_number_animals() or 0)
        except Exception:  # pylint: disable=broad-exception-caught
            total = 0
        try:
            scanned = int(len(self.db.get_animals()))
        except Exception:  # pylint: disable=broad-exception-caught
            scanned = int(len(self.animals))
        pending = max(total - scanned, 0)
        if hasattr(self, "total_animals_value") and self.total_animals_value.winfo_exists():
            self.total_animals_value.configure(text=str(total))
        if hasattr(self, "scanned_value") and self.scanned_value.winfo_exists():
            self.scanned_value.configure(text=str(scanned))
        if hasattr(self, "pending_value") and self.pending_value.winfo_exists():
            self.pending_value.configure(text=str(pending))

    def _set_scanning_state(self, active: bool):
        """Update scan toggle button UI state without altering scan logic."""
        self._scanning_active = bool(active)
        if not hasattr(self, "scan_toggle_button") or not self.scan_toggle_button.winfo_exists():
            return
        if self._scanning_active:
            self.scan_toggle_button.configure(text="⏹ Stop scanning")
            setattr(self.scan_toggle_button, "_mouser_variant", "warning")
            self._set_button_enabled(self.scan_toggle_button, True)
        else:
            self.scan_toggle_button.configure(text="▶ Start scanning")
            setattr(self.scan_toggle_button, "_mouser_variant", "success")
            enabled = self.db.experiment_uses_rfid() != 0
            self._set_button_enabled(self.scan_toggle_button, enabled)

    def toggle_scanning(self):
        """Single button to start/stop RFID scanning (only scan control behavior changes)."""
        if getattr(self, "_scanning_active", False):
            self.stop_listening()
            self._set_scanning_state(False)
            return
        self._set_scanning_state(True)
        self.rfid_listen()

    def _set_button_enabled(self, button, enabled):
        """Apply enabled/disabled visual style while preserving behavior."""
        if enabled:
            variant = getattr(button, "_mouser_variant", "primary")
            active_style = self._button_styles.get(variant, self._button_styles["primary"])
            button.configure(state="normal", **active_style)
        else:
            button.configure(state="disabled", **self._disabled_button_style)

    def rfid_listen(self):
        """Starts RFID listener, ensuring the previous session is fully closed before restarting."""
        self._set_scanning_state(True)
        self.set_reader_status("Starting scanner...")

        # Ensure old listener is properly stopped before starting a new one
        if self.rfid_thread and self.rfid_thread.is_alive():
            print("⚠️ Stopping stale RFID listener before restarting...")
            self.stop_listening()
            time.sleep(0.5)  # Allow OS to release the port

        if len(self.db.get_animals()) != self.db.get_total_number_animals():
            FlashOverlay(
                parent=self,
                message="RFID Scanning Started",
                duration=1000,
                bg_color="#00FF00", #Bright Green
                text_color="black"
            )

        time.sleep(.1)

        print("📡 Starting a fresh RFID listener...")
        print("RFIDs already scanned: ", self.animal_rfid_list)
        self.rfid_stop_event.clear()  # Reset the stop flag

        # Try serial mode first; fallback to HID if serial can't open.
        self.rfid_reader = SerialDataHandler("reader")
        serial_reader = getattr(self.rfid_reader, "reader", None)
        serial_port = getattr(serial_reader, "ser", None)
        if serial_port is None:
            self._switch_to_hid_fallback("Serial RFID unavailable.")
            return

        self.use_hid_fallback = False
        self._start_hid_listener(show_flash=False)
        self.set_reader_status("Started scanning.")

        switching_to_hid = False

        def listen():
            nonlocal switching_to_hid
            try:
                self.rfid_reader.start()
                print("🔄 RFID Reader Started!")

                last_rfid = None
                serial_start_time = time.monotonic()
                got_first_serial_data = False

                while not self.rfid_stop_event.is_set():
                    serial_reader = getattr(self.rfid_reader, "reader", None)
                    serial_port = getattr(serial_reader, "ser", None)
                    if serial_port is None or not getattr(serial_port, "is_open", False):
                        switching_to_hid = True
                        self.after(0, lambda: self._switch_to_hid_fallback("Serial connection lost."))
                        return

                    received_rfid = self.rfid_reader.get_stored_data()
                    elapsed = time.monotonic() - serial_start_time
                    if (not got_first_serial_data) and (not received_rfid) and elapsed > self._serial_first_data_timeout:
                        switching_to_hid = True
                        self.after(0, lambda: self._switch_to_hid_fallback("No serial RFID data received."))
                        return

                    if not received_rfid or received_rfid == last_rfid:
                        time.sleep(0.5)
                        continue

                    got_first_serial_data = True
                    last_rfid = received_rfid
                    print(f"📡 RFID Scanned: {received_rfid}")
                    self.after(0, lambda value=received_rfid: self._handle_scanned_rfid(value))

            except Exception as e:
                print(f"Error in RFID listener: {e}")
            finally:
                if hasattr(self, 'rfid_reader') and self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader.close()
                    self.rfid_reader = None
                print("RFID listener thread ended.")
                if (not switching_to_hid) and self.winfo_exists():
                    self.after(0, lambda: self._set_scanning_state(False))


        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()

    def stop_listening(self):
        """Stops the RFID listener thread and ensures the serial port is released."""
        print("⛔ Stopping RFID scanning...")
        self.set_reader_status("Stopping scanner...")
        self.rfid_stop_event.set()  # Stop the listener loop
        self._stop_hid_listener()
        self.use_hid_fallback = False

        if self.rfid_thread and self.rfid_thread.is_alive():
            self.rfid_thread.join(timeout=1)  # Ensure the thread fully stops

        if self.rfid_reader:
            try:
                print("🔌 Closing serial connection...")
                self.rfid_reader.stop()
                self.rfid_reader = None
            except Exception as e:
                self.raise_warning("Failed to close the serial port properly.")
                print(f"⚠️ Error closing serial port: {e}")


        time.sleep(0.5)  # Allow OS to release the port
        self.set_reader_status("Stopped listening.")
        self._set_scanning_state(False)

    def _switch_to_hid_fallback(self, reason=""):
        """Stop serial reading and switch to HID fallback mode."""
        if reason:
            print(f"⚠️ {reason} Switching to HID fallback.")

        if reason:
            self.set_reader_status(f"{reason} HID fallback active.")
        else:
            self.set_reader_status("HID fallback active.")

        if self.rfid_reader:
            try:
                self.rfid_reader.stop()
            except Exception:
                pass
            finally:
                self.rfid_reader = None

        self.use_hid_fallback = True
        self._start_hid_listener()

    def _start_hid_listener(self, show_flash=True):
        """Start HID keyboard-wedge fallback listener."""
        self._stop_hid_listener()

        def on_tag(tag):
            self._handle_scanned_rfid(tag)

        self.hid_listener = HIDWedgeListener(self, on_tag=on_tag, capture_all=True)
        self.hid_listener.start()
        self.parent.focus_force()
        self.set_reader_status("Scan tag")
        if show_flash:
            FlashOverlay(
                parent=self,
                message="HID Fallback Active: Scan tag then press Enter",
                duration=2000,
                bg_color="#FDE68A",
                text_color="black"
            )

    def _stop_hid_listener(self):
        """Stop HID keyboard-wedge fallback listener."""
        if self.hid_listener:
            self.hid_listener.stop()
            self.hid_listener = None

    def _handle_scanned_rfid(self, received_rfid):
        """Handle scanned RFID from serial or HID in one place."""
        if not received_rfid:
            return

        clean_rfid = received_rfid.strip().replace("\x02", "").replace("\x03", "")
        clean_rfid = clean_rfid.strip()

        if not clean_rfid:
            print("⚠️ Empty or invalid RFID detected, skipping...")
            return

        now = time.monotonic()
        if clean_rfid == self._recent_tag and (now - self._recent_tag_time) < 0.35:
            return
        self._recent_tag = clean_rfid
        self._recent_tag_time = now
        self.set_reader_status(f"Tag detected: {clean_rfid}")

        if clean_rfid in self.animal_rfid_list:
            print(f"⚠️ RFID {clean_rfid} is already in use! Skipping...")
            AudioManager.play(ERROR_SOUND)
            self.raise_warning("This RFID tag has already been mapped to an animal")
            return

        self.add_value(clean_rfid)

    def simulate_all_rfid(self):
        '''Simulates RFID for all remaining unmapped animals.'''
        confirm = CTkMessagebox(
            title= "Confirm Simulate All",
            message= "Are you sure you want to SimAll? \nThis should only be used in testing.",
            option_1="No",
            option_2="Yes"
        )
        if confirm.get() == "Yes":
            self.set_reader_status("Simulating RFID mapping...")
            total_needed = self.db.get_total_number_animals()
            current_count = len(self.db.get_animals())

            print(f"Simulating RFIDs: {current_count} mapped, {total_needed} total needed")

            if current_count >= total_needed:
                self.raise_warning()
                return

            while current_count < total_needed:
                previous_count = current_count
                self.add_random_rfid()
                current_count = len(self.db.get_animals())
                if current_count == previous_count:
                    self.raise_warning("Unable to map remaining animals. Check group capacity and serial setup.")
                    break
                # Force UI update
                self.update()
                self.scroll_to_latest_entry()

            self.save()
            AudioManager.play(SUCCESS_SOUND)
            self.set_reader_status("Simulation complete.")
            self._refresh_summary_cards()


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
        while str(rfid) in [str(existing) for existing in self.animal_rfid_list]:
            rfid = get_random_rfid()

        self._add_rfid_mapping(rfid, play_audio=False)


    def add_value(self, rfid):
        """Adds RFID to the table, similar to add_random_rfid but with a provided RFID."""
        if rfid is None or rfid == "":
            print("🚫 Skipping None/Empty RFID value... No entry will be added.")
            return

        active_animals = len(self.db.get_animals())
        if active_animals >= self.db.get_total_number_animals():
            self.raise_warning()
            return

        added = self._add_rfid_mapping(rfid, play_audio=True)
        if not added:
            return

        total_scanned = len(self.db.get_animals())
        total_expected = self.db.get_total_number_animals()
        print(f"✅ Scanned: {total_scanned} / Expected: {total_expected}")

        # Save changes
        self.save()

        # If we haven't scanned all animals yet, restart serial listening.
        # HID fallback stays active and keeps listening without restart.
        if total_scanned < total_expected:
            print("⌨️ Waiting for next tag...")
            FlashOverlay(
                parent=self,
                message="Scan Successful!",
                duration=1000,
                bg_color="#00FF00", #Bright Green
                text_color="black"
            )
            return
        else:
            print("🎉 All animals have been mapped to RFIDs! RFID scanning completed.")
            print("RFIDs scanned: ", self.db.get_all_animals_rfid())
            self.save()
            AudioManager.play(SUCCESS_SOUND)
            FlashOverlay(
                parent=self,
                message="Scan successful! All RFIDs scanned.",
                duration=4000,
                bg_color="#FFF700", #Yellow to indicate completion
                text_color="black"
            )

    def _add_rfid_mapping(self, rfid, play_audio=True):
        """Insert RFID mapping into database and table. Returns True on success."""
        animal_id = self.get_next_animal()
        group_id = self.db.find_next_available_group()
        if group_id is None:
            self.raise_warning("No available group slot. Check group capacity.")
            return False

        inserted_id = self.db.add_animal(animal_id, rfid, group_id, '')
        if inserted_id is None:
            self.raise_warning("Failed to map RFID. Please try again.")
            return False

        self.db._conn.commit()
        row_index = len(self.table.get_children())
        row_tag = "even_row" if row_index % 2 == 0 else "odd_row"
        self.table.insert('', END, values=(animal_id, rfid), tags=("text_font", row_tag))
        self.animals.append((animal_id, rfid))
        if rfid not in self.animal_rfid_list:
            self.animal_rfid_list.append(rfid)
        self.change_entry_text()
        self.scroll_to_latest_entry()
        self._refresh_summary_cards()

        if play_audio:
            AudioManager.play(SUCCESS_SOUND)
        return True

    def item_selected(self, _):
        selected = self.table.selection()
        print("Selection ", selected, " changed.")

        enable_button = len(selected) > 0
        self._set_button_enabled(self.delete_button, enable_button)
        self._set_button_enabled(self.sacrifice_button, enable_button)

    def remove_selected_items(self):
        '''Removes the selected item from a table, warning if none selected.'''
        selected_items = self.table.selection()

        # Check if any items are selected
        if not selected_items:  # If no items are selected
            self.raise_warning("No item selected. Please select an item to remove.")
            return

        for item in selected_items:
            item_id = int(self.table.item(item, 'values')[0])
            rfid_value = self.table.item(item, 'values')[1]
            self.table.selection_remove(item)
            self.table.delete(item)
            self.db.remove_animal(item_id)
            self.animals = [(index, tag) for (index, tag) in self.animals if index != item_id]
            if rfid_value in self.animal_rfid_list:
                self.animal_rfid_list.remove(rfid_value)
            print("Total number of animal rows in the table:", len(self.table.get_children()))

        self.save()
        self.change_entry_text()
        self.set_reader_status("Removed selected mapping(s).")
        self._refresh_summary_cards()

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
        existing_animal_ids = self.db.get_all_animals()

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

        FlashOverlay(
            parent=self,
            message=warning_message,
            duration=2000,
            bg_color="red",
            text_color="black"
        )
        AudioManager.play(ERROR_SOUND)

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
        for row_index, animal in enumerate(animals_setup):
            rfid = self.db.get_animal_rfid(animal)
            value = (int(animal), rfid)
            row_tag = "even_row" if row_index % 2 == 0 else "odd_row"
            self.table.insert('', END, values=value, tags=("text_font", row_tag))
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
        if len(self.db.get_all_animals_rfid()) != self.db.get_total_number_animals():
            self.raise_warning('Not all animals have been mapped to RFIDs')
        else:
            try:
                # Close threads first
                self.stop_listening()
                # Save database state to permanent file
                self.save()

                # Close the database connection
                self.db.close()  # This will now handle the singleton cleanup

                # Return to the existing ExperimentMenuUI instead of creating a new instance.
                if getattr(self, "menu_page", None) is not None:
                    self.menu_page.raise_frame()
                    return

                # Fallback for legacy call-sites that didn't provide a menu_page.
                from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
                new_page = ExperimentMenuUI(self.parent, self.file_path, None)
                new_page.raise_frame()

            except Exception as e:
                self.raise_warning("An error occurred while saving or cleaning up.")
                print(f"Error during save and cleanup: {e}")



    def raise_frame(self):
        '''Raise the frame for this UI'''
        super().raise_frame()

    def save(self):
        '''Saves current database state to permanent file'''
        try:
            # Save the current state before cleaning up
            current_file = self.db.db_file

            # Ensure all changes are committed
            self.db._conn.commit()
            print("Changes committed")

            # Save back to original file location
            print(f"Saving {current_file} to {self.file_path}")
            file_utils.save_temp_to_file(current_file, self.file_path)
            try:
                from ui.commands import save_file  # pylint: disable=import-outside-toplevel
                save_file()
            except Exception as save_exc:
                print(f"Could not run global save_file() hook: {save_exc}")
            print("Save successful!")

        except Exception as e:
            self.raise_warning("An error occurred while saving or cleaning up.")
            print(f"Error during save and cleanup: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")

    def sacrifice_selected_items(self):
        '''Decreases the maximum number of animals in the experiment by 1'''
        selected_items = self.table.selection()

        if not selected_items:
            self.raise_warning("No items selected. Please select animals to sacrifice.")
            return

        # First mark the selected animals as inactive
        for item in selected_items:
            animal_id = int(self.table.item(item, 'values')[0])
            rfid_value = self.table.item(item, 'values')[1]
            self.table.selection_remove(item)
            self.table.delete(item)
            self.db.set_animal_active_status(animal_id, 0)  # Mark as inactive
            self.animals = [(index, rfid) for (index, rfid) in self.animals if index != animal_id]
            if rfid_value in self.animal_rfid_list:
                self.animal_rfid_list.remove(rfid_value)

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

        # Lastly, commit and save changes (After all animals sacrificed)
        self.save()
        self.change_entry_text()
        self.set_reader_status("Updated sacrificed animal selection.")
        self._refresh_summary_cards()

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
        self.socat_process = None
        self.dynamic_virtual_ports = []

    def _current_virtual_ports(self):
        """Return discovered virtual ports, including runtime-created socat ports."""
        ports = self.dynamic_virtual_ports if self.dynamic_virtual_ports else self.serial_controller.get_virtual_port()
        # Keep order stable and unique
        return list(dict.fromkeys(ports))

    def _start_socat_pair(self):
        """Create a PTY pair using socat on macOS/Linux and return two device paths."""
        if platform.system() == "Windows":
            return []
        if shutil.which("socat") is None:
            return []

        try:
            self.socat_process = subprocess.Popen(
                ["socat", "-d", "-d", "pty,raw,echo=0", "pty,raw,echo=0"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )
            ports = []
            for _ in range(20):
                if self.socat_process.stderr is None:
                    break
                line = self.socat_process.stderr.readline()
                if not line:
                    continue
                match = re.search(r"/dev/\S+", line)
                if match:
                    port = match.group(0)
                    if port not in ports:
                        ports.append(port)
                if len(ports) >= 2:
                    self.dynamic_virtual_ports = ports[:2]
                    return self.dynamic_virtual_ports
        except Exception as e:
            print(f"Failed to start socat PTY pair: {e}")

        # Cleanup on partial failure
        self._stop_socat_pair()
        return []

    def _stop_socat_pair(self):
        """Terminate socat process if we started one."""
        if self.socat_process:
            try:
                self.socat_process.terminate()
            except Exception:
                pass
            self.socat_process = None

    def open(self):

        '''Opens the serial simulator dialog.'''
        virtual_ports = self._current_virtual_ports()
        if len(virtual_ports) == 0:
            if platform.system() in ("Darwin", "Linux"):
                warning = CTkMessagebox(
                    title="Warning",
                    message="No virtual serial ports detected. Create a temporary pair now?",
                    icon="warning",
                    option_1="Cancel",
                    option_2="Create"
                )
                if warning.get() == "Create":
                    virtual_ports = self._start_socat_pair()
                    if len(virtual_ports) < 2:
                        CTkMessagebox(
                            title="Error",
                            message="Unable to create virtual ports. Install socat and try again.",
                            icon="cancel"
                        )
                        return
                else:
                    return
            else:
                warning = CTkMessagebox(title="Warning",
                                        message="Virtual ports missing, would you like to download the virtual ports?",
                                        icon="warning",
                                        option_1="Cancel",
                                        option_2="Download")
                if warning.get() == "Download":
                    self.download_link()
                return

        if len(virtual_ports) < 2:
            return

        self.root = CTkToplevel(self.parent)
        self.root.title("Serial Port Selection")
        self.root.geometry('400x400')

        self.read_message = CTkTextbox(self.root, height=15, width = 40)
        self.read_message.place(relx=0.10, rely = 0.00)

        self.drop_down_ports = CTkComboBox(self.root, values=virtual_ports)
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

        available_port = self._current_virtual_ports()
        if self.written_port in available_port:
            available_port.remove(self.written_port)

        if not available_port:
            raise serialutil.SerialException("No paired virtual port available.")

        self.serial_controller.set_reader_port(available_port[0])

    def read_and_display(self):
        '''Reads from available port.'''
        available_port = self._current_virtual_ports()
        if self.written_port in available_port:
            available_port.remove(self.written_port)

        if len(available_port)==0:
            CTkMessagebox(
                message="There seems to be problem with the virtual port, please submit bug report.",
                title="Warning",
                icon="cancel"
            )

        else:
            message = self.serial_controller.read_info()
            if message is not None:
                self.read_message.insert(END, str(message))

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
        if platform.system() == "Windows":
            webbrowser.open("https://softradar.com/com0com/")
        else:
            webbrowser.open("https://man7.org/linux/man-pages/man1/socat.1.html")

    def on_closing(self):
        '''Closes all ports and closes the window.'''
        self.serial_controller.close_all_port()
        self._stop_socat_pair()
        self.dynamic_virtual_ports = []
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

        AudioManager.play(ERROR_SOUND)

        message.mainloop()
