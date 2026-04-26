'''Data collection ui module.'''
from datetime import date
import re
import csv
from collections import deque
from functools import partial
import tkinter as tk
import tkinter.font as tkfont
from tkinter.ttk import Treeview, Style
from tkinter import dialog, filedialog
import time
import sqlite3
import serial
import os
from customtkinter import *
from CTkMessagebox import CTkMessagebox
from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase
from shared.file_utils import SUCCESS_SOUND, ERROR_SOUND
from shared.audio import AudioManager
from shared.serial_handler import SerialDataHandler
from shared.file_utils import save_temp_to_file
import threading
from shared.flash_overlay import FlashOverlay
from shared.hid_wedge import HIDWedgeListener

#pylint: disable= undefined-variable
class DataCollectionUI(MouserPage):
    '''Page Frame for Data Collection.'''

    def __init__(self, parent: CTk, prev_page: CTkFrame = None, database_name = "", file_path = "", original_file_path: str | None = None):

        super().__init__(parent, "Data Collection", prev_page)
        ui = get_ui_metrics()
        self._ui = ui
        action_button_font = CTkFont("Segoe UI Semibold", ui["action_font_size"])
        table_font_size = ui["table_font_size"]
        is_dark = get_appearance_mode().lower() == "dark"

        def _pick(color_value):
            if isinstance(color_value, (tuple, list)) and len(color_value) >= 2:
                return color_value[1] if is_dark else color_value[0]
            return color_value
        self._pick = _pick

        self._palette = {
            "page_bg": ("#eef2ff", "#0b1220"),
            "card_bg": ("#ffffff", "#101827"),
            "card_border": ("#c7d2fe", "#22304a"),
            "text": ("#0f172a", "#e5e7eb"),
            "muted_text": ("#334155", "#cbd5e1"),
            # Table styling (more "realistic" grid look)
            "table_bg": ("#ffffff", "#0b1220"),
            "table_alt_bg": ("#f8fafc", "#0f172a"),
            "table_header_bg": ("#e0f2fe", "#1e293b"),
            "table_header_fg": ("#0f172a", "#e5e7eb"),
            "table_selected_bg": ("#dbeafe", "#1d4ed8"),
            "table_selected_fg": ("#111827", "#ffffff"),
        }
        self.configure(fg_color=self._palette["page_bg"])

        self.parent = parent

        self.rfid_reader = None
        self.rfid_stop_event = threading.Event()  # Event to stop RFID listener
        self.rfid_thread = None # Store running thread
        self._measurement_in_progress = False
        self._hid_rfid_listener = None
        self._rfid_input_mode = None  # "serial" | "hid"
        self._device_poll_job = None
        self._last_hid_tag_time = 0.0
        self._serial_controllers = {"device": None, "reader": None}
        self._active_animal_id = None
        self._measurement_serial_threads = {}
        self._measurement_serial_stop = threading.Event()
        self._activity_entries = deque(maxlen=200)
        self._last_device_status = {}
        self._device_connected_until = {}
        self._last_connected_port = {}

        self.current_file_path = file_path
        self.original_file_path = original_file_path or file_path
        self.menu_page = prev_page

        self.database = ExperimentDatabase(database_name)

        def _split_measurements(raw_value):
            if raw_value is None:
                return []
            if isinstance(raw_value, (list, tuple)):
                parts = []
                for item in raw_value:
                    parts.extend(_split_measurements(item))
                return parts
            text = str(raw_value).strip()
            if not text:
                return []
            # Common separators used in the project UI/DB.
            parts = re.split(r"[,\n;/|]+", text)
            return [p.strip() for p in parts if p and p.strip()]

        def _format_measurement_header(name: str) -> str:
            text = (name or "").strip()
            if not text:
                return "Value"
            # Backwards compatibility: older experiments stored custom devices as "Custom:<name>".
            if text.lower().startswith("custom:"):
                text = text.split(":", 1)[1].strip() or "Custom"
            # Render units on a second line when written like "Weight (g)".
            match = re.match(r"^(.*)\s+\((.*)\)\s*$", text)
            if match:
                return f"{match.group(1).strip()}\n({match.group(2).strip()})"
            # Normalize common labels used by devices.
            lowered = text.lower()
            if lowered == "caliper":
                return "Length\n(mm)"
            if lowered in {"weight", "balancer", "balance"}:
                return "Balancer\n(g)"
            return text

        # Used by dynamic column updates when devices are added.
        self._format_measurement_header = _format_measurement_header

        # Database stores a single measurement name in `experiment.measurement`.
        # Older code paths may return tuples from fetchone(); normalize to a string.
        self.measurement_items = self.database.get_measurement_items()
        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(command=self.press_back_to_menu_button)
            # Match back-button styling from the modern pages.
            try:
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

        # Top bar (reference layout)
        top_bar = CTkFrame(self, fg_color=self._palette["card_bg"], corner_radius=0, height=84)
        top_bar.place(relx=0.0, rely=0.0, relwidth=1.0)
        CTkFrame(top_bar, fg_color=_pick(self._palette["card_border"]), height=1).pack(
            side="bottom", fill="x"
        )

        # Back button (keep regular Mouser styling used across pages)
        if hasattr(self, "menu_button") and self.menu_button:
            try:
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
                self.menu_button.place_configure(in_=top_bar, relx=0.0, rely=0.0, x=16, y=22, anchor="nw")
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        # Title/subtitle are shown above the Start Scanning button (left panel) per updated layout.

        header_right = CTkFrame(top_bar, fg_color="transparent")
        header_right.place(relx=1.0, rely=0.0, x=-16, y=18, anchor="ne")
        self.status_chip = CTkFrame(
            header_right,
            fg_color=_pick(self._palette["table_alt_bg"]),
            corner_radius=16,
            border_width=1,
            border_color=_pick(self._palette["card_border"]),
        )
        self.status_chip.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="e")
        self.status_chip_label = CTkLabel(
            self.status_chip,
            text="● Idle",
            font=CTkFont("Segoe UI Semibold", 12),
            text_color=("#047857", "#34d399"),
        )
        self.status_chip_label.pack(padx=12, pady=6)

        self.export_csv_button = CTkButton(
            header_right,
            text="⇩  Export CSV",
            width=120,
            height=34,
            corner_radius=10,
            fg_color=self._palette["card_bg"],
            hover_color=_pick(self._palette["table_alt_bg"]),
            border_width=1,
            border_color=_pick(self._palette["card_border"]),
            text_color=_pick(self._palette["text"]),
            font=CTkFont("Segoe UI Semibold", 13),
            command=self.handle_export_csv,
        )
        self.export_csv_button.grid(row=0, column=1, pady=4, sticky="e")

        self.export_notification = CTkLabel(
            self,
            text="",
            text_color=_pick(self._palette["muted_text"]),
            font=CTkFont("Segoe UI Semibold", 13),
            fg_color="transparent",
            corner_radius=8,
            padx=10,
            pady=5
        )
        self.export_notification.place(relx=0.5, rely=0.0, y=86, anchor="n")


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

        measurement_name = self.database.get_measurement_name()
        if isinstance(measurement_name, (list, tuple)):
            measurement_name = measurement_name[0] if measurement_name else None
        self.measurement_strings = _split_measurements(measurement_name)
        print("Measurement(s):", self.measurement_strings)

        if self.database.experiment_uses_rfid() == 0:
            start_function = self.auto_increment
            start_button_text = "▶ Start"
        else:
            start_function = self.rfid_listen
            start_button_text = "▶ Start scanning"

        self._scan_start_function = start_function
        self._scan_start_text = start_button_text
        self._scan_stop_text = "Stop scanning"
        self._scan_is_running = False
        self._scan_button_style_start = {
            "fg_color": ("#16a34a", "#16a34a"),
            "hover_color": ("#15803d", "#15803d"),
            "border_width": 0,
            "text_color": "#ffffff",
        }
        self._scan_button_style_stop = {
            "fg_color": ("#ef4444", "#ef4444"),
            "hover_color": ("#dc2626", "#dc2626"),
            "border_width": 0,
            "text_color": "#ffffff",
        }

        # Body layout (left content + right sidebar)
        body = CTkFrame(self, fg_color="transparent")
        body.place(relx=0.5, rely=0.0, y=88, anchor="n", relwidth=0.94, relheight=0.90)
        body.grid_rowconfigure(0, weight=1)
        # Keep left/right panels stable even if the table has many fixed-width columns.
        body.grid_columnconfigure(0, weight=3, uniform="body")
        body.grid_columnconfigure(1, weight=2, uniform="body")

        self.left_panel = CTkFrame(body, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.left_panel.grid_columnconfigure(0, weight=1)
        # Prevent the Treeview's requested width from resizing the overall layout.
        try:
            self.left_panel.grid_propagate(False)
        except Exception:
            pass
        # Layout: header, summary tiles, controls, table, spacer.
        self.left_panel.grid_rowconfigure(0, weight=0)
        self.left_panel.grid_rowconfigure(1, weight=0)
        self.left_panel.grid_rowconfigure(2, weight=0)
        self.left_panel.grid_rowconfigure(3, weight=0)
        self.left_panel.grid_rowconfigure(4, weight=1)

        self.right_panel = CTkFrame(body, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        try:
            self.right_panel.grid_propagate(False)
        except Exception:
            pass
        self.right_panel.grid_rowconfigure(1, weight=0)
        self.right_panel.grid_rowconfigure(2, weight=1)

        # Header above Start Scanning (matches reference structure)
        left_header = CTkFrame(self.left_panel, fg_color="transparent")
        left_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        left_title_row = CTkFrame(left_header, fg_color="transparent")
        left_title_row.pack(anchor="w")
        CTkLabel(
            left_title_row,
            text="\U0001f4ca",
            font=CTkFont("Segoe UI Semibold", 18),
            text_color=self._palette["text"],
            width=0,
        ).pack(side="left", padx=(0, 8))
        CTkLabel(
            left_title_row,
            text="Data collection",
            font=CTkFont("Segoe UI Semibold", 24),
            text_color=self._palette["text"],
        ).pack(side="left")
        CTkLabel(
            left_header,
            text=f"Collect today\u2019s measurements \u00b7 {date.today().strftime('%B %d, %Y')}",
            font=CTkFont("Segoe UI", 12),
            text_color=self._palette["muted_text"],
        ).pack(anchor="w", pady=(2, 0))

        # Summary tiles under header (total / measured / remaining / completion).
        stats_row = CTkFrame(self.left_panel, fg_color="transparent")
        stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for col in range(4):
            stats_row.grid_columnconfigure(col, weight=1, uniform="stats")

        def _stat_tile(col_index, title, value_color, tile_bg, tile_border):
            tile = CTkFrame(
                stats_row,
                fg_color=_pick(tile_bg),
                corner_radius=14,
                border_width=1,
                border_color=_pick(tile_border),
            )
            tile.grid(row=0, column=col_index, sticky="ew", padx=6, pady=0)
            CTkLabel(
                tile,
                text=title,
                font=CTkFont("Segoe UI", 12),
                text_color=self._palette["muted_text"],
                anchor="w",
            ).pack(fill="x", padx=14, pady=(12, 0))
            value_label = CTkLabel(
                tile,
                text="--",
                font=CTkFont("Segoe UI Semibold", 26),
                text_color=value_color,
                anchor="w",
            )
            value_label.pack(fill="x", padx=14, pady=(2, 12))
            return value_label

        self.total_animals_value = _stat_tile(
            0,
            "Total animals",
            _pick(self._palette["text"]),
            ("#f1f5f9", "#0f172a"),
            ("#94a3b8", "#475569"),
        )
        self.measured_today_value = _stat_tile(
            1,
            "Measured today",
            ("#16a34a", "#34d399"),
            ("#ecfdf5", "#042f2e"),
            ("#34d399", "#34d399"),
        )
        self.remaining_value = _stat_tile(
            2,
            "Remaining",
            ("#a16207", "#fbbf24"),
            ("#fffbeb", "#2e1f0a"),
            ("#f59e0b", "#f59e0b"),
        )
        self.completion_value = _stat_tile(
            3,
            "Completion",
            ("#4f46e5", "#818cf8"),
            ("#eef2ff", "#111827"),
            ("#818cf8", "#818cf8"),
        )

        control_bar = CTkFrame(self.left_panel, fg_color="transparent")
        control_bar.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        control_bar.grid_columnconfigure(0, weight=1)
        control_bar.grid_columnconfigure(1, weight=1)

        self.animals = self.database.get_animals()
        total_animals = len(self.animals)




        self.scan_button = CTkButton(
            control_bar,
            text=start_button_text,
            compound=TOP,
            width=210,
            height=44,
            font=CTkFont("Segoe UI Semibold", 14),
            fg_color=_pick(self._scan_button_style_start["fg_color"]),
            hover_color=_pick(self._scan_button_style_start["hover_color"]),
            border_width=self._scan_button_style_start["border_width"],
            text_color=self._scan_button_style_start["text_color"],
            command=self._toggle_scanning,
        )
        self.scan_button.grid(row=0, column=0, columnspan=2, padx=0, pady=6)
        self._set_scan_button_state(False)
        # Backwards-compatible alias used throughout this module.
        self.auto_increment_button = self.scan_button
        self.auto_inc_id = -1

        # Keep the original status label for internal updates, but show status via chip.
        self.status_label = CTkLabel(self, text="Status: Idle")
        self.status_label.place_forget()

        # Table container (layout only). Keep it visually transparent so the Treeview is the only "box".
        self.table_frame = CTkFrame(
            self.left_panel,
            fg_color="transparent",
            corner_radius=0,
            border_width=0,
        )
        self.table_frame.grid(row=3, column=0, sticky="new")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(1, weight=0)

        CTkFrame(self.left_panel, fg_color="transparent").grid(row=4, column=0, sticky="nsew")



        display_measurements = self.measurement_strings if self.measurement_strings else ["Value"]
        columns = ["animal_id", *display_measurements, "status"]

        # Initialize the Treeview with the defined columns
        self.table = Treeview(
            self.table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
            height=13,
            style="DataCollection.Treeview",
        )

        # Set up the column headings / table theme.
        style = Style()
        try:
            if style.theme_use() in {"vista", "xpnative"}:
                style.theme_use("clam")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        style.configure(
            "DataCollection.Treeview",
            background=_pick(self._palette["table_bg"]),
            fieldbackground=_pick(self._palette["table_bg"]),
            foreground=_pick(self._palette["text"]),
            rowheight=ui["table_row_height"] + 4,
            font=("Segoe UI", max(12, table_font_size)),
            borderwidth=0,
        )
        style.configure(
            "DataCollection.Treeview.Heading",
            background=_pick(self._palette["table_header_bg"]),
            foreground=_pick(self._palette["table_header_fg"]),
            font=("Segoe UI Semibold", max(12, table_font_size)),
            relief="flat",
            padding=(10, 6),
        )
        style.map(
            "DataCollection.Treeview",
            background=[("selected", _pick(self._palette["table_selected_bg"]))],
            foreground=[("selected", _pick(self._palette["table_selected_fg"]))],
        )
        style.map(
            "DataCollection.Treeview.Heading",
            background=[("active", _pick(self._palette["table_selected_bg"]))],
            foreground=[("active", _pick(self._palette["table_selected_fg"]))],
        )

        # Row stage colors (reference: Done/Scanning/Pending)
        self.table.tag_configure("done", background=_pick(("#d1fae5", "#064e3b")), foreground=_pick(self._palette["text"]))
        self.table.tag_configure("scanning", background=_pick(("#ede9fe", "#312e81")), foreground=_pick(self._palette["text"]))
        self.table.tag_configure("pending", background=_pick(self._palette["card_bg"]), foreground=_pick(self._palette["text"]))

        heading_font = tkfont.Font(family="Segoe UI Semibold", size=max(12, table_font_size))

        def _measure_heading_width(heading_text: str) -> int:
            """Compute a column width that fits the full heading text (with optional newlines)."""
            try:
                lines = str(heading_text or "").split("\n")
            except Exception:
                lines = [str(heading_text)]
            max_px = 0
            for line in lines:
                try:
                    max_px = max(max_px, int(heading_font.measure(str(line))))
                except Exception:
                    max_px = max(max_px, len(str(line)) * 8)
            # Add padding so it doesn't touch edges.
            return max_px + 36

        for i, column in enumerate(columns):
            if column == "animal_id":
                text = "Animal"
                width = 160
            elif column == "status":
                text = "Status"
                width = 120
            else:
                text = _format_measurement_header(str(column))
                width = max(130, _measure_heading_width(text))

            print(f"Setting heading for column: {column} with text: {text}")  # Debugging line
            if text:  # Only set heading if text is not empty
                self.table.heading(column, text=text, anchor="center")
            # Keep stable base widths, but let the Status column absorb extra space so there is no blank gap.
            self.table.column(
                column,
                anchor="center",
                width=width,
                stretch=(column == "status"),
            )

        # Add the table to the grid
        self.table.grid(row=0, column=0, sticky='nsew')
        table_scroll = CTkScrollbar(self.table_frame, orientation=VERTICAL, command=self.table.yview)
        self.table.configure(yscrollcommand=table_scroll.set)
        table_scroll.configure(
            fg_color="transparent",
            button_color=_pick(self._palette["card_border"]),
            button_hover_color=_pick(self._palette["table_selected_bg"]),
        )
        table_scroll.grid(row=0, column=1, sticky='ns', padx=(8, 0))

        # Horizontal scroll (only shown when columns overflow).
        self.table_hscroll = CTkScrollbar(self.table_frame, orientation=HORIZONTAL, command=self.table.xview)
        self.table.configure(xscrollcommand=self.table_hscroll.set)
        self.table_hscroll.configure(
            fg_color="transparent",
            button_color=_pick(self._palette["card_border"]),
            button_hover_color=_pick(self._palette["table_selected_bg"]),
        )
        self.table_hscroll.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.table_hscroll.grid_remove()

        # Keep scrollbar visibility in sync on resize.
        try:
            self.table.bind("<Configure>", lambda _e: self.after(50, self._update_table_hscroll_visibility))
        except Exception:
            pass

        self.date_label = CTkLabel(self, text="Current Date: --")
        self.date_label.place_forget()

        for animal in self.animals:
            animal_id = animal[0]
            values = [animal_id, *([None] * len(display_measurements)), "Pending"]
            self.table.insert("", END, values=tuple(values), tags=("pending",))

        # Determine whether RFID input is via serial or HID keyboard wedge.
        self._rfid_input_mode = self._detect_rfid_input_mode()

        # Cache serial controllers (used for real-time device detection).
        try:
            from shared.serial_port_controller import SerialPortController  # pylint: disable=import-error
            self._serial_controllers["device"] = SerialPortController("device")
            self._serial_controllers["reader"] = SerialPortController("reader")
        except Exception:
            self._serial_controllers["device"] = None
            self._serial_controllers["reader"] = None

        # Right sidebar: show selected devices + connection status.
        devices_card = CTkFrame(
            self.right_panel,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
            height=350,
        )
        devices_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        devices_card.grid_columnconfigure(0, weight=1)
        # Keep buttons anchored at the bottom; let the scroll area take remaining space.
        devices_card.grid_rowconfigure(0, weight=0)  # title
        devices_card.grid_rowconfigure(1, weight=0)  # summary
        devices_card.grid_rowconfigure(2, weight=1)  # scroll area
        devices_card.grid_rowconfigure(3, weight=0)  # divider
        devices_card.grid_rowconfigure(4, weight=0)  # actions
        # Keep the card height fixed so it doesn't push the Activity log down.
        try:
            devices_card.grid_propagate(False)
        except Exception:
            pass

        CTkLabel(
            devices_card,
            text="Devices",
            font=CTkFont("Segoe UI Semibold", 14),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        self.devices_summary_label = CTkLabel(
            devices_card,
            text="—",
            font=CTkFont("Segoe UI", 12),
            text_color=self._palette["muted_text"],
        )
        self.devices_summary_label.grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

        self.devices_rows_frame = CTkScrollableFrame(
            devices_card,
            fg_color="transparent",
            corner_radius=0,
            border_width=0,
        )
        # Add a small inset so the scrollbar stays visually inside the card border.
        self.devices_rows_frame.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 0))
        self.devices_rows_frame.grid_columnconfigure(0, weight=1)
        self._inline_add_device_row = None

        def _device_row(parent_frame, row_index, title, port_text, status_text, state):
            state_map = {
                "ok": {"bg": ("#ecfdf5", "#042f2e"), "border": ("#34d399", "#34d399"), "dot": ("#10b981", "#10b981")},
                "warn": {"bg": ("#fffbeb", "#2e1f0a"), "border": ("#f59e0b", "#f59e0b"), "dot": ("#f59e0b", "#f59e0b")},
                "error": {"bg": ("#fee2e2", "#3f1d1d"), "border": ("#ef4444", "#ef4444"), "dot": ("#ef4444", "#ef4444")},
                "idle": {"bg": ("#f3f4f6", "#111827"), "border": ("#d1d5db", "#374151"), "dot": ("#9ca3af", "#9ca3af")},
            }
            colors = state_map.get(state, state_map["idle"])
            row = CTkFrame(
                parent_frame,
                fg_color=_pick(colors["bg"]),
                corner_radius=12,
                border_width=1,
                border_color=_pick(colors["border"]),
            )
            row.grid(row=row_index, column=0, sticky="ew", padx=6, pady=4)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)
            row.grid_columnconfigure(3, weight=0)

            left = CTkFrame(row, fg_color="transparent")
            left.grid(row=0, column=0, sticky="w", padx=12, pady=8)
            title_label = CTkLabel(
                left,
                text=title,
                font=CTkFont("Segoe UI Semibold", 13),
                text_color=self._palette["text"],
                wraplength=240,
                justify="left",
            )
            title_label.grid(row=0, column=0, sticky="w")

            status_label = CTkLabel(
                left,
                text=status_text or "",
                font=CTkFont("Segoe UI", 12),
                text_color=self._palette["muted_text"],
                wraplength=140,
                justify="left",
            )
            status_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

            port_label = CTkLabel(
                row,
                text=f"Port: {port_text or ''}",
                font=CTkFont("Segoe UI Semibold", 12),
                text_color=self._palette["muted_text"],
                width=120,
                anchor="e",
            )
            port_label.grid(row=0, column=1, sticky="e", padx=(0, 10), pady=8)

            dot_label = CTkLabel(
                row,
                text="●",
                font=CTkFont("Segoe UI Semibold", 14),
                text_color=_pick(colors["dot"]),
            )
            dot_label.grid(row=0, column=2, sticky="e", padx=12, pady=8)

            delete_button = CTkButton(
                row,
                text="🗑",
                width=34,
                height=30,
                corner_radius=10,
                fg_color="transparent",
                hover_color=_pick(self._palette["table_alt_bg"]),
                border_width=1,
                border_color=_pick(self._palette["card_border"]),
                text_color=_pick(self._palette["muted_text"]),
                font=CTkFont("Segoe UI Semibold", 12),
            )
            delete_button.grid(row=0, column=3, sticky="e", padx=(0, 12), pady=8)
            delete_button.grid_remove()

            return {
                "frame": row,
                "title": title_label,
                "status": status_label,
                "port": port_label,
                "dot": dot_label,
                "delete": delete_button,
            }

        def _selected_measurement_devices():
            devices = []
            for raw in (self.measurement_strings or []):
                text = str(raw or "").strip()
                if not text:
                    continue
                lower = text.lower()
                if lower in {"weight", "balancer", "balance"}:
                    devices.append({"name": "Balancer", "kind": "device"})
                elif lower == "caliper":
                    devices.append({"name": "Caliper", "kind": "device"})
                elif lower.startswith("custom:"):
                    # Backwards compatibility: stored as "Custom:<name>"
                    custom_name = text.split(":", 1)[1].strip() or "Custom"
                    devices.append({"name": custom_name, "kind": "device", "custom": True})
                else:
                    devices.append({"name": text, "kind": "device"})
            if self.database.experiment_uses_rfid() == 1:
                devices.append({"name": "RFID reader", "kind": "reader"})
            return devices

        def _resolve_serial_port_for_device(device_name: str, kind: str):
            """Return (port, description, connected_bool, note)."""
            controller = self._serial_controllers.get("reader" if kind == "reader" else "device")
            if not controller:
                return None, "", False, "serial unavailable"

            available_detailed = []
            try:
                if hasattr(controller, "get_available_ports_detailed"):
                    available_detailed = controller.get_available_ports_detailed() or []
            except Exception:
                available_detailed = []
            available = controller.get_available_ports() or []
            available_names = [dev for dev, _desc in available]
            configured_port = getattr(controller, "reader_port", None)

            # Prefer the configured port if present.
            if configured_port and configured_port in available_names:
                desc = ""
                for dev, d in available:
                    if dev == configured_port:
                        desc = d or ""
                        break
                return configured_port, desc, True, "configured"

            # Otherwise, try to auto-match based on description/manufacturer/product keywords.
            name_lower = (device_name or "").strip().lower()

            # Known device keyword sets (extend as needed).
            keywords = []
            if name_lower in {"balancer", "balance"}:
                keywords = [
                    "balance",
                    "scale",
                    "weigh",
                    "mettler",
                    "mettl",
                    "mettler",
                    "ohaus",
                    "sartorius",
                    "and",
                    "ad",
                ]
            elif name_lower == "caliper":
                keywords = ["caliper", "mitutoyo", "digimatic"]
            elif kind == "reader":
                keywords = ["rfid", "reader"]
            else:
                # For custom devices, use the device name tokens as keywords.
                keywords = [t for t in re.split(r"[^a-z0-9]+", name_lower) if t]

            def _score_port(port_item: dict) -> int:
                text = " ".join(
                    [
                        str(port_item.get("device") or ""),
                        str(port_item.get("description") or ""),
                        str(port_item.get("manufacturer") or ""),
                        str(port_item.get("product") or ""),
                        str(port_item.get("hwid") or ""),
                    ]
                ).lower()
                score = 0
                for k in keywords:
                    if k and k in text:
                        score += 3
                # Prefer USB devices with metadata when auto-detecting.
                if port_item.get("vid") is not None and port_item.get("pid") is not None:
                    score += 1
                return score

            # If we don't have detailed metadata, build a minimal version from (device, desc).
            if not available_detailed:
                available_detailed = [{"device": dev, "description": desc} for dev, desc in available]

            best_item = None
            best_score = 0
            for item in available_detailed:
                score = _score_port(item)
                if score > best_score:
                    best_score = score
                    best_item = item

            if best_item and best_score > 0 and best_item.get("device"):
                desc = best_item.get("description") or best_item.get("product") or best_item.get("manufacturer") or ""
                return str(best_item.get("device")), str(desc), True, "detected"

            # If we have a configured port but it's not present, surface it anyway.
            if configured_port:
                return configured_port, "", False, "not found"

            return None, "", False, "not configured"

        # Expose for runtime measurement listeners.
        self._resolve_serial_port_for_device = _resolve_serial_port_for_device

        self._selected_devices = _selected_measurement_devices()
        self._device_row_factory = _device_row
        self._device_row_widgets = []
        for idx, device in enumerate(self._selected_devices):
            widgets = _device_row(self.devices_rows_frame, idx, device.get("name", "Device"), "", "", "idle")
            self._device_row_widgets.append(widgets)
            if device.get("kind") == "device":
                try:
                    widgets["delete"].configure(command=partial(self._on_delete_device_clicked, device.get("name")))
                    widgets["delete"].grid()
                except Exception:
                    pass

        def _scroll_devices_to_bottom():
            """Ensure the last row in the devices scroll area is visible."""
            try:
                self.devices_rows_frame.update_idletasks()
            except Exception:
                pass
            # CustomTkinter CTkScrollableFrame uses a Canvas internally; try common attribute names.
            for attr in ("_parent_canvas", "_canvas", "canvas"):
                canvas = getattr(self.devices_rows_frame, attr, None)
                if canvas is not None and hasattr(canvas, "yview_moveto"):
                    try:
                        canvas.yview_moveto(1.0)
                        return
                    except Exception:
                        pass

        def _update_devices_card_once():
            # Re-detect RFID mode when not actively scanning.
            if not getattr(self, "_scan_is_running", False):
                self._rfid_input_mode = self._detect_rfid_input_mode()

            now = time.monotonic()
            connected = 0
            registered = len(self._selected_devices)

            # Snapshot available COM ports (used for the "no COM ports at all" rule).
            device_ports = []
            reader_ports = []
            if self._serial_controllers.get("device"):
                try:
                    device_ports = self._serial_controllers["device"].get_available_ports() or []
                except Exception:
                    device_ports = []
            if self._serial_controllers.get("reader"):
                try:
                    reader_ports = self._serial_controllers["reader"].get_available_ports() or []
                except Exception:
                    reader_ports = []

            any_com_present = bool(device_ports or reader_ports)

            for idx, device in enumerate(self._selected_devices):
                widgets = self._device_row_widgets[idx]
                name = device.get("name", "Device")
                kind = device.get("kind", "device")
                device_key = (str(name), str(kind))

                port_text = ""
                status_text = "Not found" if not any_com_present else "Not found"
                state = "warn" if any_com_present else "idle"

                # Ensure delete button visibility for all measurement devices (including custom-added ones).
                try:
                    if kind == "device":
                        widgets["delete"].configure(command=partial(self._on_delete_device_clicked, name))
                        widgets["delete"].grid()
                    else:
                        widgets["delete"].grid_remove()
                except Exception:
                    pass

                if kind == "reader" and self.database.experiment_uses_rfid() == 1 and self._rfid_input_mode == "hid":
                    port_text = "HID"
                    # In HID wedge mode, avoid OS keyboard probing subprocesses.
                    # Treat an active listener (or recent tag) as connected to keep status stable.
                    listener_active = bool(getattr(self, "_hid_rfid_listener", None))
                    recent_scan = bool(self._last_hid_tag_time and (now - self._last_hid_tag_time) < 10.0)
                    if listener_active or recent_scan:
                        status_text = "Connected"
                        state = "ok"
                        self._device_connected_until[device_key] = now + 3.0
                        self._last_connected_port[device_key] = port_text
                        connected += 1
                    elif getattr(self, "_scan_is_running", False):
                        status_text = "Listening"
                        state = "ok"
                        connected += 1
                    else:
                        status_text = "Ready"
                        state = "idle"
                else:
                    port, desc, is_connected, _note = _resolve_serial_port_for_device(name, kind)
                    if port and is_connected:
                        port_text = str(port)
                        status_text = "Connected"
                        state = "ok"
                        self._device_connected_until[device_key] = now + 3.0
                        self._last_connected_port[device_key] = port_text
                        connected += 1
                    else:
                        grace_until = float(self._device_connected_until.get(device_key, 0.0) or 0.0)
                        if now < grace_until:
                            # Debounce transient port-drop reads to prevent connect/disconnect flapping.
                            port_text = str(self._last_connected_port.get(device_key, "") or "")
                            status_text = "Connected"
                            state = "ok"
                            connected += 1
                        else:
                            # Requirement: when nothing connected, keep port blank but show "Port: ".
                            port_text = ""
                            status_text = "Not found"
                            state = "warn" if any_com_present else "idle"

                # Activity: only log device state changes (avoid spam during polling).
                try:
                    prev = self._last_device_status.get(device_key)
                    now_state = (status_text, port_text)
                    if prev != now_state:
                        self._last_device_status[device_key] = now_state
                        if status_text == "Connected":
                            shown_port = port_text or ("HID" if (kind == "reader" and self._rfid_input_mode == "hid") else "")
                            self._log_activity(f"{name} connected (Port: {shown_port})")
                        else:
                            self._log_activity(f"{name} not found")
                except Exception:
                    pass

                try:
                    widgets["title"].configure(text=name)
                    widgets["status"].configure(text=status_text)
                    widgets["port"].configure(text=f"Port: {port_text}")
                    # Dot color is handled by recreating row colors; simplest is leave dot as-is and rely on state.
                    # For now, update dot color + row border/bg by tweaking frame colors.
                    state_map = {
                        "ok": {"bg": ("#ecfdf5", "#042f2e"), "border": ("#34d399", "#34d399"), "dot": ("#10b981", "#10b981")},
                        "warn": {"bg": ("#fffbeb", "#2e1f0a"), "border": ("#f59e0b", "#f59e0b"), "dot": ("#f59e0b", "#f59e0b")},
                        "idle": {"bg": ("#f3f4f6", "#111827"), "border": ("#d1d5db", "#374151"), "dot": ("#9ca3af", "#9ca3af")},
                        "error": {"bg": ("#fee2e2", "#3f1d1d"), "border": ("#ef4444", "#ef4444"), "dot": ("#ef4444", "#ef4444")},
                    }
                    colors = state_map.get(state, state_map["idle"])
                    widgets["frame"].configure(
                        fg_color=_pick(colors["bg"]),
                        border_color=_pick(colors["border"]),
                    )
                    widgets["dot"].configure(text_color=_pick(colors["dot"]))
                except Exception:
                    pass

            if hasattr(self, "devices_summary_label") and self.devices_summary_label:
                self.devices_summary_label.configure(text=f"{registered} registered · {connected} connected")

        self._update_devices_card_once = _update_devices_card_once
        self._update_devices_card_once()

        # Divider between the scroll area and the action buttons.
        CTkFrame(
            devices_card,
            height=1,
            fg_color=_pick(self._palette["card_border"]),
        ).grid(row=3, column=0, sticky="ew", padx=14, pady=(6, 0))

        actions_row = CTkFrame(devices_card, fg_color="transparent")
        actions_row.grid(row=4, column=0, sticky="ew", padx=14, pady=(18, 10))
        actions_row.grid_columnconfigure(0, weight=1)
        actions_row.grid_columnconfigure(1, weight=1)

        def _hide_inline_add_row():
            if getattr(self, "_inline_add_device_row", None) is None:
                return
            try:
                frame = self._inline_add_device_row.get("frame")
                if frame and frame.winfo_exists():
                    frame.destroy()
            except Exception:
                pass
            self._inline_add_device_row = None

        def _commit_inline_add():
            if getattr(self, "_inline_add_device_row", None) is None:
                return
            try:
                entry = self._inline_add_device_row.get("entry")
                name = entry.get().strip() if entry else ""
            except Exception:
                name = ""
            if not name:
                _hide_inline_add_row()
                return

            # Add to the devices list only (no serial pre-configuration required).
            try:
                if any(
                    (d.get("kind") == "device" and str(d.get("name") or "").strip().lower() == name.lower())
                    for d in (self._selected_devices or [])
                ):
                    self.raise_warning("Device already exists.")
                    _hide_inline_add_row()
                    return
            except Exception:
                pass
            self._selected_devices.append({"name": name, "kind": "device"})
            new_widgets = _device_row(self.devices_rows_frame, len(self._device_row_widgets), name, "", "", "idle")
            self._device_row_widgets.append(new_widgets)
            try:
                new_widgets["delete"].configure(command=partial(self._on_delete_device_clicked, name))
                new_widgets["delete"].grid()
            except Exception:
                pass
            self._add_measurement_column(name)
            try:
                if getattr(self, "_scan_is_running", False):
                    self._start_measurement_serial_listeners()
            except Exception:
                pass
            _hide_inline_add_row()
            try:
                if hasattr(self, "_update_devices_card_once") and self._update_devices_card_once:
                    self.after(0, self._update_devices_card_once)
            except Exception:
                pass

        def _show_inline_add_row():
            # Only allow one inline add row at a time.
            if getattr(self, "_inline_add_device_row", None) is not None:
                try:
                    entry = self._inline_add_device_row.get("entry")
                    if entry and entry.winfo_exists():
                        entry.focus_set()
                        return
                except Exception:
                    pass

            row_index = len(self._device_row_widgets)
            frame = CTkFrame(
                self.devices_rows_frame,
                fg_color=_pick(("#f8fafc", "#0f172a")),
                corner_radius=12,
                border_width=1,
                border_color=_pick(self._palette["card_border"]),
            )
            frame.grid(row=row_index, column=0, sticky="ew", padx=0, pady=4)
            # Keep the row from expanding the right sidebar: fixed-size entry + compact actions.
            frame.grid_columnconfigure(0, weight=0)
            frame.grid_columnconfigure(1, weight=0)
            frame.grid_columnconfigure(2, weight=0)

            entry = CTkEntry(
                frame,
                placeholder_text="Device name (e.g., Glucometer)",
                width=200,
            )
            entry.grid(row=0, column=0, sticky="w", padx=12, pady=10)

            add_btn = CTkButton(
                frame,
                text="✓",
                width=44,
                height=32,
                corner_radius=10,
                fg_color="#16a34a",
                hover_color="#15803d",
                text_color="white",
                font=CTkFont("Segoe UI Semibold", 12),
                command=_commit_inline_add,
            )
            add_btn.grid(row=0, column=1, sticky="e", padx=(0, 8), pady=10)

            cancel_btn = CTkButton(
                frame,
                text="✕",
                width=44,
                height=32,
                corner_radius=10,
                fg_color="#ef4444",
                hover_color="#dc2626",
                text_color="white",
                font=CTkFont("Segoe UI Semibold", 12),
                command=_hide_inline_add_row,
            )
            cancel_btn.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=10)

            entry.bind("<Return>", lambda _event: _commit_inline_add())
            entry.bind("<Escape>", lambda _event: _hide_inline_add_row())
            try:
                entry.focus_set()
            except Exception:
                pass

            self._inline_add_device_row = {"frame": frame, "entry": entry}
            # Auto-scroll so the inline entry is immediately visible.
            try:
                self.after(50, _scroll_devices_to_bottom)
            except Exception:
                pass

        CTkButton(
            actions_row,
            text="+  Add device",
            height=38,
            corner_radius=12,
            fg_color=("#16a34a", "#16a34a"),
            hover_color=("#15803d", "#15803d"),
            border_width=0,
            text_color="#ffffff",
            font=CTkFont("Segoe UI Semibold", 13),
            command=_show_inline_add_row,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        CTkButton(
            actions_row,
            text="↻  Refresh",
            height=38,
            corner_radius=12,
            fg_color=("#2563eb", "#2563eb"),
            hover_color=("#1d4ed8", "#1d4ed8"),
            border_width=0,
            text_color="#ffffff",
            font=CTkFont("Segoe UI Semibold", 13),
            command=self._update_devices_card_once,
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0))

        # RFID reader port selection is auto-detected (serial) or inferred (HID) on refresh; no manual config needed.

        activity_card = CTkFrame(
            self.right_panel,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        activity_card.grid(row=1, column=0, sticky="ew")
        activity_card.grid_columnconfigure(0, weight=1)
        activity_card.grid_rowconfigure(1, weight=0)

        CTkLabel(
            activity_card,
            text="Activity log",
            font=CTkFont("Segoe UI Semibold", 14),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 8))

        self.activity_text = CTkTextbox(
            activity_card,
            height=215,
            font=("Segoe UI", 12),
            wrap="word",
            fg_color=_pick(self._palette["table_alt_bg"]),
            text_color=_pick(self._palette["text"]),
            border_width=1,
            border_color=_pick(self._palette["card_border"]),
            corner_radius=12,
        )
        self.activity_text.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        try:
            self.activity_text.configure(state="disabled")
        except Exception:
            pass

        CTkFrame(self.right_panel, fg_color="transparent").grid(row=2, column=0, sticky="nsew")
        self._log_activity("Ready.")


        self.get_values_for_date()

        self.table.bind('<<TreeviewSelect>>', self.item_selected)
        self.table.bind("<1>", self._on_table_click)
        
        # Initialize inline editor tracking
        self._inline_editor = None

        self.changer = ChangeMeasurementsDialog(parent, self, self.measurement_strings)

    def _log_activity(self, message: str):
        """Append a line to the Activity log."""
        try:
            msg = str(message).strip()
        except Exception:
            msg = ""
        if not msg:
            return

        timestamp = time.strftime("%H:%M:%S")
        line = f"{timestamp}  {msg}"
        try:
            self._activity_entries.append(line)
        except Exception:
            return

        if not hasattr(self, "activity_text") or not self.activity_text:
            return

        def _render():
            if not self.winfo_exists():
                return
            try:
                self.activity_text.configure(state="normal")
            except Exception:
                pass
            try:
                self.activity_text.delete("1.0", "end")
                self.activity_text.insert("end", "\n".join(self._activity_entries))
                self.activity_text.see("end")
            except Exception:
                pass
            try:
                self.activity_text.configure(state="disabled")
            except Exception:
                pass

        try:
            self.after(0, _render)
        except Exception:
            pass

    def _update_table_hscroll_visibility(self):
        """Show the bottom horizontal scrollbar only when needed."""
        if not hasattr(self, "table_hscroll") or not self.table_hscroll:
            return
        try:
            if not self.table.winfo_exists():
                return
        except Exception:
            return

        try:
            columns = list(self.table["columns"] or [])
            total_width = 0
            for col in columns:
                try:
                    total_width += int(self.table.column(col, "width") or 0)
                except Exception:
                    pass
            view_width = int(self.table.winfo_width() or 0)
            needs = total_width > max(view_width, 0) + 8
        except Exception:
            needs = False

        try:
            if needs:
                self.table_hscroll.grid()
            else:
                self.table_hscroll.grid_remove()
        except Exception:
            pass

    def _detect_rfid_input_mode(self):
        """Return 'serial' or 'hid' when RFID is enabled for the experiment."""
        try:
            if self.database.experiment_uses_rfid() != 1:
                return None
        except Exception:  # pylint: disable=broad-exception-caught
            return None

        try:
            controller = getattr(self, "_serial_controllers", {}).get("reader")
            if not controller:
                return "hid"
            configured_port = getattr(controller, "reader_port", None)
            available = [dev for dev, _desc in controller.get_available_ports() or []]
            if configured_port and configured_port in available:
                return "serial"
        except Exception:
            pass

        # Default to HID wedge when we cannot confirm a serial RFID reader.
        return "hid"

    def _start_hid_rfid_listening(self):
        """Start HID keyboard-wedge RFID listening (no serial port required)."""
        if getattr(self, "_hid_rfid_listener", None) is not None:
            try:
                self._hid_rfid_listener.stop()
            except Exception:
                pass
            self._hid_rfid_listener = None

        def _on_tag(raw_tag: str):
            if self.rfid_stop_event.is_set():
                return
            tag = re.sub(r"[^\w]", "", str(raw_tag or "")).strip()
            if not tag:
                return
            self._last_hid_tag_time = time.monotonic()
            try:
                animal_id = self.database.get_animal_id(tag)
            except Exception:
                animal_id = None
            if animal_id is None:
                # Ignore non-matching keystrokes (prevents accidental capture of normal typing).
                self.set_status("HID RFID scanned (unmapped).")
                return
            self.after(0, lambda aid=animal_id: self.process_scanned_animal(aid))

        # Capture from the top-level window so scans work even when focus changes.
        self._hid_rfid_listener = HIDWedgeListener(self, _on_tag, capture_all=True)
        self._hid_rfid_listener.start()

    def _stop_hid_rfid_listening(self):
        if getattr(self, "_hid_rfid_listener", None) is None:
            return
        try:
            self._hid_rfid_listener.stop()
        except Exception:
            pass
        self._hid_rfid_listener = None

    def _start_device_polling(self):
        if getattr(self, "_device_poll_job", None) is not None:
            return

        def _tick():
            self._device_poll_job = None
            if not self.winfo_exists():
                return
            try:
                if hasattr(self, "_update_devices_card_once") and self._update_devices_card_once:
                    self._update_devices_card_once()
            except Exception:
                pass
            self._device_poll_job = self.after(1000, _tick)

        self._device_poll_job = self.after(250, _tick)

    def _stop_device_polling(self):
        job = getattr(self, "_device_poll_job", None)
        self._device_poll_job = None
        if job is None:
            return
        try:
            self.after_cancel(job)
        except Exception:
            pass

    def _get_serial_device_kwargs(self):
        """Best-effort serial parameters for measurement devices (balance/caliper/etc.)."""
        settings = {
            "baudrate": 9600,
            "bytesize": serial.EIGHTBITS,
            "parity": serial.PARITY_NONE,
            "stopbits": serial.STOPBITS_ONE,
            "timeout": 0.2,
        }
        controller = getattr(self, "_serial_controllers", {}).get("device")
        try:
            if controller and getattr(controller, "baud_rate", None):
                settings["baudrate"] = int(controller.baud_rate)
            if controller and getattr(controller, "byte_size", None):
                settings["bytesize"] = controller.byte_size
            if controller and getattr(controller, "parity", None):
                settings["parity"] = controller.parity
            if controller and getattr(controller, "stop_bits", None):
                settings["stopbits"] = controller.stop_bits
        except Exception:
            pass
        return settings

    def _start_measurement_serial_listeners(self):
        """Start background listeners for each measurement column (serial devices).

        Values read from each device are routed to the corresponding column for the most recently scanned RFID.
        """
        # Only run for automatic measurement mode.
        try:
            if self.database.get_measurement_type() != 1:
                return
        except Exception:
            return

        if not hasattr(self, "_resolve_serial_port_for_device"):
            return

        self._measurement_serial_stop.clear()
        serial_kwargs = self._get_serial_device_kwargs()

        for measurement_index, measurement_name in enumerate(self.measurement_strings or []):
            device_label = str(measurement_name or "").strip()
            if not device_label:
                continue

            port, _desc, is_connected, _note = self._resolve_serial_port_for_device(device_label, "device")
            if not port or not is_connected:
                continue

            thread_key = f"{measurement_index}:{port}"
            if thread_key in self._measurement_serial_threads:
                continue

            def _thread_target(mi: int, port_name: str, key: str):
                ser_obj = None
                try:
                    ser_obj = serial.Serial(port=port_name, **serial_kwargs)
                except Exception as exc:
                    print(f"Failed to open device port {port_name} for measurement index {mi}: {exc}")
                    return

                buffer = ""
                try:
                    while not self._measurement_serial_stop.is_set():
                        try:
                            chunk = ser_obj.read(64)
                        except Exception:
                            break
                        if not chunk:
                            continue
                        try:
                            buffer += chunk.decode("utf-8", errors="ignore")
                        except Exception:
                            continue

                        if "\n" not in buffer and "\r" not in buffer:
                            continue

                        lines = re.split(r"[\r\n]+", buffer)
                        buffer = lines[-1]  # keep trailing partial
                        for line in lines[:-1]:
                            raw = str(line).strip()
                            if not raw:
                                continue
                            match = re.search(r"-?\d+(?:\.\d+)?", raw)
                            if not match:
                                continue
                            value_text = match.group(0)

                            animal_id = getattr(self, "_active_animal_id", None)
                            if animal_id is None:
                                continue

                            self.after(
                                0,
                                lambda aid=animal_id, idx=mi, val=value_text: self.change_selected_value_at(aid, idx, val),
                            )
                finally:
                    try:
                        if ser_obj and ser_obj.is_open:
                            ser_obj.close()
                    except Exception:
                        pass
                    try:
                        if key in self._measurement_serial_threads:
                            del self._measurement_serial_threads[key]
                    except Exception:
                        pass

            t = threading.Thread(target=_thread_target, args=(measurement_index, port, thread_key), daemon=True)
            self._measurement_serial_threads[thread_key] = t
            t.start()

    def _stop_measurement_serial_listeners(self):
        self._measurement_serial_stop.set()
        self._measurement_serial_threads = {}

    def showSaveFileDialog(self):
        '''Opens a file dialog for the user to select where to save the CSV file.'''
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV"
        )
        return file_path

    def _add_measurement_column(self, name: str):
        """Add a new measurement column to the left table and persist to the experiment DB."""
        try:
            text = str(name or "").strip()
        except Exception:  # pylint: disable=broad-exception-caught
            text = ""
        if not text:
            return

        # Avoid duplicates (case-insensitive).
        existing = [str(m or "").strip() for m in (self.measurement_strings or [])]
        if any(text.lower() == e.lower() for e in existing if e):
            return

        self.measurement_strings = list(self.measurement_strings or [])
        self.measurement_strings.append(text)

        # Persist the measurement list so DB reads/writes align to new measurement_id slots.
        try:
            if hasattr(self.database, "update_measurement_name"):
                self.database.update_measurement_name(", ".join(self.measurement_strings))
        except Exception:
            pass

        # Rebuild table columns.
        try:
            columns = ["animal_id", *self.measurement_strings, "status"]
            self.table.configure(columns=columns)
            table_font_size = int(self._ui.get("table_font_size", 14)) if hasattr(self, "_ui") else 14
            heading_font = tkfont.Font(family="Segoe UI Semibold", size=max(12, table_font_size))

            def _measure_heading_width(heading_text: str) -> int:
                try:
                    lines = str(heading_text or "").split("\n")
                except Exception:
                    lines = [str(heading_text)]
                max_px = 0
                for line in lines:
                    try:
                        max_px = max(max_px, int(heading_font.measure(str(line))))
                    except Exception:
                        max_px = max(max_px, len(str(line)) * 8)
                return max_px + 36

            for column in columns:
                if column == "animal_id":
                    heading_text = "Animal"
                    width = 160
                elif column == "status":
                    heading_text = "Status"
                    width = 120
                else:
                    heading_text = self._format_measurement_header(str(column)) if hasattr(self, "_format_measurement_header") else str(column)
                    width = max(130, _measure_heading_width(heading_text))
                self.table.heading(column, text=heading_text, anchor="center")
                # Keep stable base widths, but let the Status column absorb extra space so there is no blank gap.
                self.table.column(
                    column,
                    anchor="center",
                    width=width,
                    stretch=(column == "status"),
                )
        except Exception:
            return

        try:
            self.after(50, self._update_table_hscroll_visibility)
        except Exception:
            pass

        # Refresh values/status/tiles for the current date with new column count.
        try:
            self.get_values_for_date()
        except Exception:
            pass

        # Update changer dialog measurement items (if present).
        try:
            if hasattr(self, "changer") and self.changer:
                self.changer.measurement_items = list(self.measurement_strings)
        except Exception:
            pass

    def _delete_device(self, name: str):
        """Delete a device from the Devices card and remove its measurement column."""
        text = str(name or "").strip()
        if not text:
            return

        def _norm_key(value: str) -> str:
            try:
                v = str(value or "").strip().lower()
            except Exception:
                return ""
            # Remove separators/newlines/etc. to make matching robust.
            key = re.sub(r"[^a-z0-9]+", "", v)
            # Backwards compatibility: stored as "Custom:<name>" in older experiments.
            if key.startswith("custom") and len(key) > 6:
                key = key[6:]
            return key

        target_key = _norm_key(text)
        if not target_key:
            return

        # Don't allow deleting all measurement columns.
        if len(self.measurement_strings or []) <= 1:
            self.raise_warning("At least one measurement device is required.")
            return

        # Find the measurement column index.
        measurement_index = None
        for idx, item in enumerate(self.measurement_strings or []):
            if _norm_key(item) == target_key:
                measurement_index = idx
                break
        if measurement_index is None:
            # Fallback: try prefix match (handles odd truncation or formatting).
            for idx, item in enumerate(self.measurement_strings or []):
                item_key = _norm_key(item)
                if item_key and (item_key.startswith(target_key) or target_key.startswith(item_key)):
                    measurement_index = idx
                    break
        if measurement_index is None:
            try:
                keys = [f"{str(i)}:{_norm_key(v)}" for i, v in enumerate(self.measurement_strings or [])]
                self._log_activity(
                    f"Delete failed: could not find column for '{text}'. Columns={keys}"
                )
            except Exception:
                self._log_activity(f"Delete failed: could not find column for '{text}'")
            return

        # Stop listeners while we reshuffle indices.
        restart_listeners = bool(getattr(self, "_scan_is_running", False))
        if restart_listeners:
            try:
                self._stop_measurement_serial_listeners()
            except Exception:
                pass

        # Update DB measurement slots: delete+shift IDs so remaining columns still map correctly.
        try:
            if hasattr(self.database, "delete_measurement_column"):
                self.database.delete_measurement_column(measurement_index + 1)
        except Exception:
            pass

        # Update measurement strings and persist new measurement list.
        self.measurement_strings = list(self.measurement_strings or [])
        try:
            self.measurement_strings.pop(measurement_index)
        except Exception:
            return
        try:
            if hasattr(self.database, "update_measurement_name"):
                self.database.update_measurement_name(", ".join(self.measurement_strings))
        except Exception:
            pass

        # Remove device from right-side list (only the first matching device entry).
        try:
            for i, dev in enumerate(list(self._selected_devices or [])):
                if dev.get("kind") == "device" and _norm_key(dev.get("name")) == target_key:
                    self._selected_devices.pop(i)
                    break
        except Exception:
            pass

        # Rebuild the left table columns to match.
        try:
            columns = ["animal_id", *self.measurement_strings, "status"]
            self.table.configure(columns=columns)

            table_font_size = int(self._ui.get("table_font_size", 14)) if hasattr(self, "_ui") else 14
            heading_font = tkfont.Font(family="Segoe UI Semibold", size=max(12, table_font_size))

            def _measure_heading_width(heading_text: str) -> int:
                try:
                    lines = str(heading_text or "").split("\n")
                except Exception:
                    lines = [str(heading_text)]
                max_px = 0
                for line in lines:
                    try:
                        max_px = max(max_px, int(heading_font.measure(str(line))))
                    except Exception:
                        max_px = max(max_px, len(str(line)) * 8)
                return max_px + 36

            for column in columns:
                if column == "animal_id":
                    heading_text = "Animal"
                    width = 160
                elif column == "status":
                    heading_text = "Status"
                    width = 120
                else:
                    heading_text = self._format_measurement_header(str(column)) if hasattr(self, "_format_measurement_header") else str(column)
                    width = max(130, _measure_heading_width(heading_text))
                self.table.heading(column, text=heading_text, anchor="center")
                self.table.column(column, anchor="center", width=width, stretch=(column == "status"))
        except Exception:
            pass

        # Update in-memory row values quickly (remove the cell at the deleted column position).
        try:
            remove_at = measurement_index + 1  # account for animal_id at 0
            for child in self.table.get_children():
                values = list(self.table.item(child).get("values") or [])
                if len(values) > remove_at:
                    values.pop(remove_at)
                self.table.item(child, values=tuple(values))
        except Exception:
            pass

        # Update changer dialog measurement items.
        try:
            if hasattr(self, "changer") and self.changer:
                self.changer.measurement_items = list(self.measurement_strings)
        except Exception:
            pass

        # Rebuild the device rows UI so indexes/buttons match.
        try:
            self._rebuild_devices_rows()
        except Exception:
            pass

        # Refresh values/status/tiles with updated schema.
        try:
            self.get_values_for_date()
        except Exception:
            pass

        try:
            self.after(50, self._update_table_hscroll_visibility)
        except Exception:
            pass

        self._log_activity(f"Deleted device: {text}")

        if restart_listeners:
            try:
                self._start_measurement_serial_listeners()
            except Exception:
                pass

    def _on_delete_device_clicked(self, name: str):
        """UI handler for delete buttons; logs failures instead of failing silently."""
        try:
            self._delete_device(name)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            try:
                self._log_activity(f"Delete failed for {name}: {exc}")
            except Exception:
                pass

    def _rebuild_devices_rows(self):
        """Rebuild the devices list UI after add/delete."""
        if not hasattr(self, "devices_rows_frame") or not self.devices_rows_frame:
            return
        factory = getattr(self, "_device_row_factory", None)
        if not factory:
            return

        for widget in list(self.devices_rows_frame.winfo_children()):
            try:
                widget.destroy()
            except Exception:
                pass

        self._device_row_widgets = []
        for idx, device in enumerate(self._selected_devices or []):
            widgets = factory(self.devices_rows_frame, idx, device.get("name", "Device"), "", "", "idle")
            self._device_row_widgets.append(widgets)
            if device.get("kind") == "device":
                try:
                    widgets["delete"].configure(command=partial(self._on_delete_device_clicked, device.get("name")))
                    widgets["delete"].grid()
                except Exception:
                    pass

        # Hide any inline-add row if present (it will be recreated on demand).
        self._inline_add_device_row = None
    
    def get_measurement_names(self):
        '''Retrieves measurement names from the database.'''
        # Prefer the parsed measurement list used to build the UI columns.
        try:
            if hasattr(self, "measurement_strings") and self.measurement_strings:
                return list(self.measurement_strings)
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        name = self.database.get_measurement_name()
        if name is None:
            return []
        if isinstance(name, (list, tuple)):
            name = name[0] if name else None
        if not name:
            return []
        return [item.strip() for item in str(name).split(",") if item.strip()]
    
    def get_measurements_for_animal_today(self, animal_id):
        '''Retrieves measurements for a specific animal for the current date.'''
        today_date = str(date.today())
        measurement_names = self.get_measurement_names()
        measurement_slots = max(len(measurement_names), 1)

        values_for_day = self.database.get_data_for_date(today_date)
        values_by_animal = {str(aid): val for aid, val in values_for_day}
        measurement_value = values_by_animal.get(str(animal_id))

        if measurement_value is None:
            return [None] * measurement_slots

        if isinstance(measurement_value, (list, tuple)):
            values = list(measurement_value)
            return (values + ([None] * measurement_slots))[:measurement_slots]

        return [measurement_value] + ([None] * (measurement_slots - 1))
    
    def handle_export_csv(self):
        '''Handles exporting the current data to a CSV file.'''
        file_path = self.showSaveFileDialog()
        if not file_path:
            return  # User canceled export
        
        headers = ["Animal ID"] + self.get_measurement_names()
        data_rows = [headers]

        for animal in self.database.get_animals():
            animal_id = animal[0]
            measurements = self.get_measurements_for_animal_today(animal_id)
            row = [animal_id] + measurements
            data_rows.append(row)

        try:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(data_rows)

            self.export_notification.configure(
                text="CSV exported successfully!",
                text_color="green",
                fg_color="#d1fae5",  
                padx=12,
                pady=6,
                corner_radius=10
            )

        except Exception as e:
            print(f"Error exporting CSV: {e}")
            self.export_notification.configure(
                text="CSV export failed. Please try again.",
                text_color="#b91c1c",  
                fg_color="#fee2e2",    
                padx=12,
                pady=6,
                corner_radius=10
            )

    def raise_warning(self, warning_message='An error occurred'):
        '''Raises a popup warning message.'''
        CTkMessagebox(
            title="Warning",
            message=warning_message,
            icon="warning"
        )
        AudioManager.play(ERROR_SOUND)

    def item_selected(self, _):
        '''On item selection.

        Records the currently selected table row.'''
        self.auto_inc_id = -1
        selected = self.table.selection()
        if selected:
            self.changing_value = selected[0]

    def _on_table_click(self, event):
        """Handle click for inline edit in manual mode (no popups)."""
        if self.database.get_measurement_type() != 0:
            return

        # If an editor is already open, don't try to open another one.
        if getattr(self, "_inline_editor", None) is not None:
            try:
                if self._inline_editor.winfo_exists():
                    return "break"
            except Exception:
                pass
        
        region = self.table.identify("region", event.x, event.y)
        if region == "cell":
            column_id = self.table.identify_column(event.x)
            row_id = self.table.identify_row(event.y)
            last_column = f"#{len(self.table['columns'] or ())}"
            if not row_id or column_id in {"#1", last_column}:
                return

            values = self.table.item(row_id, "values") or ()
            try:
                column_index = int(str(column_id).lstrip("#")) - 1
            except ValueError:
                return

            if column_index <= 0 or column_index >= len(values):
                return

            # Keep selection behavior, but replace any popup flow with inline edit.
            # Allow editing existing values too (not only None).
            self.table.selection_set(row_id)
            self.changing_value = row_id
            self._enter_inline_edit(row_id, column_id)
            return "break"

    def _enter_inline_edit(self, row_id, column_id):
        # Prevent multiple inline editors from opening
        if hasattr(self, '_inline_editor') and self._inline_editor and self._inline_editor.winfo_exists():
            return
            
        # Get bounding box of the cell
        bbox = self.table.bbox(row_id, column_id)
        if not bbox:
            return
        x, y, width, height = bbox

        # Use a lightweight native tkinter Entry for fast, truly-inline editing (no popup).
        # CTkEntry can look like a separate "box" overlay; a flat Entry blends into the cell.
        style = Style()
        background = style.lookup("DataCollection.Treeview", "fieldbackground") or style.lookup("Treeview", "fieldbackground") or "white"
        foreground = style.lookup("DataCollection.Treeview", "foreground") or style.lookup("Treeview", "foreground") or "black"

        entry = tk.Entry(
            self.table,
            bd=0,
            highlightthickness=0,
            relief="flat",
            justify="center",
            font=("Arial", self._ui.get("table_font_size", 14)),
            background=background,
            foreground=foreground,
            insertbackground=foreground,
        )
        # Pre-fill with the current cell value (blank if None).
        existing_values = self.table.item(row_id, "values") or ()
        try:
            column_index = int(str(column_id).lstrip("#")) - 1
        except ValueError:
            column_index = -1

        initial_text = ""
        if 0 <= column_index < len(existing_values):
            cell_value = existing_values[column_index]
            if cell_value is not None and str(cell_value).strip() not in ("", "None"):
                initial_text = str(cell_value)

        entry.place(x=x, y=y, width=width, height=height)
        if initial_text:
            entry.insert(0, initial_text)
        self._inline_editor = entry

        # Function to save when user presses Enter
        def save_edit(event=None):
            new_val = entry.get()
            if new_val.strip() == "":
                cleanup_editor()
                return

            try:
                # Ensure it is a valid float as expected
                _ = float(new_val)
            except ValueError:
                self.raise_warning("Invalid input. Please enter a valid number.")
                cleanup_editor()
                return

            # Save the value
            animal_id = self.table.item(row_id, "values")[0]
            measurement_index = column_index - 1  # account for animal_id col at index 0
            
            # Clean up editor first to prevent visual issues
            cleanup_editor()
            
            # Then update the value (which will update both DB and table display)
            if self.change_selected_value_at(animal_id, measurement_index, new_val):
                AudioManager.play(SUCCESS_SOUND)

        def cleanup_editor(event=None):
            if hasattr(self, '_inline_editor') and self._inline_editor:
                try:
                    self._inline_editor.destroy()
                except:
                    pass
                self._inline_editor = None

        entry.bind("<Return>", save_edit)
        entry.bind("<Escape>", cleanup_editor)
        entry.bind("<FocusOut>", cleanup_editor)
        
        entry.focus_set()
        try:
            entry.selection_range(0, "end")
        except Exception:
            pass

    def set_status(self, text):
        """Update collection status line."""
        def _update():
            try:
                if hasattr(self, "status_label") and self.status_label and self.status_label.winfo_exists():
                    self.status_label.configure(text=f"Status: {text}")
            except Exception:
                pass

            if hasattr(self, "status_chip_label") and self.status_chip_label:
                chip_text = (text or "").strip() or "Idle"
                color = ("#047857", "#34d399")
                lowered = chip_text.lower()
                if "error" in lowered or "failed" in lowered:
                    color = ("#b91c1c", "#f87171")
                elif "starting" in lowered or "scanning" in lowered or "listening" in lowered:
                    color = ("#92400e", "#fbbf24")
                self.status_chip_label.configure(text=f"● {chip_text}", text_color=color)

        if self.winfo_exists():
            self.after(0, _update)

    def _set_scan_button_state(self, running: bool):
        self._scan_is_running = bool(running)
        if hasattr(self, "scan_button") and self.scan_button and self.scan_button.winfo_exists():
            text = self._scan_stop_text if self._scan_is_running else self._scan_start_text
            style = self._scan_button_style_stop if self._scan_is_running else self._scan_button_style_start
            try:
                self.scan_button.configure(
                    text=text,
                    fg_color=self._pick(style["fg_color"]),
                    hover_color=self._pick(style["hover_color"]),
                    border_width=style["border_width"],
                    text_color=style["text_color"],
                )
            except Exception:  # pylint: disable=broad-exception-caught
                pass

    def _toggle_scanning(self):
        """Single-button start/stop for RFID scanning."""
        # Auto-increment mode has no explicit stop action here.
        if self.database.experiment_uses_rfid() != 1:
            if hasattr(self, "_scan_start_function") and self._scan_start_function:
                self._scan_start_function()
            return

        if getattr(self, "_scan_is_running", False):
            self.stop_listening()
        else:
            if hasattr(self, "_scan_start_function") and self._scan_start_function:
                self._scan_start_function()

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

        if self.database.experiment_uses_rfid() != 1:
            print("This experiment does not use RFID, cancelling threads")
            self.set_status("RFID is disabled for this experiment.")
            return # Prevents looking for nonexistent Serial Devices

        # HID keyboard-wedge mode (no serial COM port).
        if getattr(self, "_rfid_input_mode", None) == "hid":
            if getattr(self, "_scan_is_running", False):
                self.set_status("HID listener already running.")
                return
            self.set_status("Starting HID RFID listener...")
            self._log_activity("Started scanning (HID RFID).")
            self._set_scan_button_state(True)
            self.rfid_stop_event.clear()
            self._start_hid_rfid_listening()
            try:
                self._start_measurement_serial_listeners()
            except Exception:
                pass
            try:
                if hasattr(self, "_refresh_devices_card") and self._refresh_devices_card:
                    self._refresh_devices_card()
            except Exception:
                pass
            self.set_status("HID RFID listener started.")
            return

        if self.rfid_thread and self.rfid_thread.is_alive():
            print("⚠️ RFID listener is already running!")
            self.set_status("RFID listener already running.")
            return  # Prevent multiple listeners
        self.set_status("Starting RFID listener...")
        self._log_activity("Started scanning (serial RFID).")
        self._set_scan_button_state(True)

        # Check if more data for the day needs to be collected
        if not self.database.is_data_collected_for_date(self.current_date):
            if self.database.get_measurement_type() == 1:
                # Create Flash overlay using new Flash Overlay Class
                FlashOverlay(
                    parent=self,
                    message="Data Collection Started",
                    duration=1000,
                    bg_color="#00FF00", #Bright Green
                    text_color="black"
                )
                AudioManager.play(SUCCESS_SOUND)

        print("📡 Starting RFID listener...")
        print("All RFIDs:", self.database.get_all_animals_rfid())
        animals = self.database.get_animals()
        print("Animals:", animals)

        # Check RFIDs directly
        print("RFIDs in database:", self.database.get_all_animals_rfid())

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
                            received_rfid = re.sub(r"[^\w]", "", received_rfid)  # Keep only alphanumeric characters, gets rid of spaces and encrypted greeting messages

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
                                self.after(250, lambda aid=animal_id: self.process_scanned_animal(aid))
                            else:
                                self.raise_warning("No animal found for scanned RFID.")
                                self.set_status("RFID not mapped to any animal.")



                    time.sleep(0.1)  # Shorter sleep time for more responsive stopping
            except Exception as e:
                print(f"Error in RFID listener: {e}")
            finally:
                if hasattr(self, 'rfid_reader') and self.rfid_reader:
                    self.rfid_reader.stop()
                    self.rfid_reader.close()
                    self.rfid_reader = None
                self._set_scan_button_state(False)
                print("🛑 RFID listener thread ended.")

        self.rfid_thread = threading.Thread(target=listen, daemon=True)
        self.rfid_thread.start()
        self.set_status("RFID listener started.")
        try:
            self._start_measurement_serial_listeners()
        except Exception:
            pass

    def stop_listening(self):
        '''Stops the RFID listener and ensures the serial port is released.'''
        print("🛑 Stopping RFID listener...")
        self.set_status("Stopping listener...")
        self._log_activity("Stopped scanning.")

        # Set the stop event first
        self.rfid_stop_event.set()

        # Stop HID wedge listener (if active)
        self._stop_hid_rfid_listening()
        try:
            self._stop_measurement_serial_listeners()
        except Exception:
            pass
        self._active_animal_id = None

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
        self._measurement_in_progress = False
        print("✅ RFID listener cleanup completed.")
        self._set_scan_button_state(False)
        self.set_status("Listener stopped.")

        # Safely stop and close the changer
        if hasattr(self, 'changer'):
            self.changer.stop_thread()  # Stop the changer thread if it's running
            self.changer.close()  # Close the changer dialog if it's open

        try:
            if hasattr(self, "_refresh_devices_card") and self._refresh_devices_card:
                self.after(200, self._refresh_devices_card)
        except Exception:
            pass

    def process_scanned_animal(self, animal_id):
        """Select scanned animal and capture weight for that animal."""
        self._active_animal_id = animal_id
        self.select_animal_by_id(animal_id)
        self._log_activity(f"RFID matched Animal {animal_id}.")

        # Automatic mode: do not block scanning with a single weight-capture thread.
        # Instead, route device readings (balance/caliper/etc.) into the active row as they arrive.
        try:
            if self.database.get_measurement_type() == 1:
                self._measurement_in_progress = False
                self.set_status(f"Animal {animal_id} selected. Waiting for device readings...")
                return
        except Exception:
            pass

        if self._measurement_in_progress:
            self.set_status("Measurement in progress. Waiting...")
            return
        self._measurement_in_progress = True
        self.set_status(f"RFID matched Animal {animal_id}. Capturing weight...")
        threading.Thread(
            target=self._collect_weight_for_animal,
            args=(animal_id,),
            daemon=True,
        ).start()

    def _collect_weight_for_animal(self, animal_id):
        """Read from configured device; fallback to manual entry."""
        weight_value = self._read_weight_from_device(timeout_seconds=3.0)
        if weight_value is None:
            self.after(0, lambda aid=animal_id: self._prompt_manual_weight(aid))
            return
        self.after(0, lambda aid=animal_id, val=weight_value: self._finalize_weight_capture(aid, val))

    def _read_weight_from_device(self, timeout_seconds=3.0):
        """Best-effort weight read from serial weighing device."""
        data_handler = None
        try:
            data_handler = SerialDataHandler("device")
            data_handler.start()
            start_time = time.monotonic()
            while time.monotonic() - start_time < timeout_seconds and not self.rfid_stop_event.is_set():
                raw = data_handler.get_stored_data()
                if raw:
                    match = re.search(r"-?\d+(?:\.\d+)?", str(raw))
                    if match:
                        return float(match.group(0))
                time.sleep(0.1)
        except Exception:
            return None
        finally:
            if data_handler:
                try:
                    data_handler.stop()
                except Exception:
                    pass
        return None

    def _prompt_manual_weight(self, animal_id):
        """Prompt for manual weight when scale is unavailable."""
        self.set_status(f"No scale data. Enter weight for Animal {animal_id}.")
        dialog = CTkInputDialog(
            title="Manual Weight Entry",
            text=f"Enter weight for Animal {animal_id}:",
        )
        user_input = dialog.get_input() if dialog else None
        if user_input is None:
            self._measurement_in_progress = False
            self.set_status("Weight entry cancelled.")
            return
        try:
            weight_value = float(str(user_input).strip())
        except ValueError:
            self._measurement_in_progress = False
            self.raise_warning("Invalid weight. Please enter a number.")
            self.set_status("Invalid manual weight entry.")
            return
        self._finalize_weight_capture(animal_id, weight_value)

    def _finalize_weight_capture(self, animal_id, weight_value):
        """Persist captured weight and release capture state."""
        self.change_selected_value(animal_id, (weight_value,))
        self._measurement_in_progress = False
        self.set_status(f"Saved {weight_value} for Animal {animal_id}.")

    def select_animal_by_id(self, animal_id):
        '''Finds and selects the animal with the given ID in the table.'''
        for child in self.table.get_children():
            item_values = self.table.item(child)["values"]
            if str(item_values[0]) == str(animal_id):  # Ensure IDs match as strings
                self.after(0, lambda: self._select_row_on_main_thread(child))
                return

        print(f"⚠️ Animal ID {animal_id} not found in table.")

    def _select_row_on_main_thread(self, child):
        '''Helper function to safely select a row on the main thread.'''
        self.table.selection_set(child)  # Select row
        self.changing_value = child

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
            def _cell_is_filled(value) -> bool:
                if value is None:
                    return False
                text = str(value).strip()
                return text != "" and text.lower() != "none"

            def _normalize_cell(value):
                if value is None:
                    return None
                text = str(value).strip()
                if text == "" or text.lower() == "none":
                    return None
                return value

            column_ids = self.table["columns"] or ()
            measurement_slots = max(len(column_ids) - 2, 1)

            raw_values = []
            if isinstance(list_of_values, (list, tuple)):
                raw_values = list(list_of_values)
            else:
                raw_values = [list_of_values]

            raw_values = (raw_values + ([None] * measurement_slots))[:measurement_slots]

            parsed_values = []
            for raw in raw_values:
                if raw is None:
                    parsed_values.append(None)
                    continue
                text = str(raw).strip()
                if text == "" or text.lower() == "none":
                    parsed_values.append(None)
                    continue
                parsed_values.append(float(text))

            print(f"Saving data point(s) for animal {animal_id_to_change}: {parsed_values}")

            today = str(date.today())
            for index, value in enumerate(parsed_values):
                # Only write values explicitly provided (None means leave as-is).
                if value is None:
                    continue
                self.database.change_data_entry(today, animal_id_to_change, value, index + 1)
            print("Database entry updated")

            # Update display table
            try:
                updated = False
                for child in self.table.get_children():
                    table_animal_id = self.table.item(child)["values"][0]
                    # Handle type conversions for comparison
                    if str(animal_id_to_change) == str(table_animal_id):
                        existing_row = list(self.table.item(child).get("values") or ())
                        if len(existing_row) >= (2 + measurement_slots):
                            existing_measurements = [
                                _normalize_cell(v) for v in existing_row[1 : 1 + measurement_slots]
                            ]
                        else:
                            existing_measurements = [None] * measurement_slots

                        # Merge: only overwrite slots where parsed_values is not None.
                        merged_measurements = list(existing_measurements)
                        for idx, val in enumerate(parsed_values):
                            if val is not None:
                                merged_measurements[idx] = val

                        merged_measurements = [_normalize_cell(v) for v in merged_measurements]
                        has_any = any(_cell_is_filled(v) for v in merged_measurements)
                        has_all = has_any and all(_cell_is_filled(v) for v in merged_measurements)
                        status = "Done" if has_all else ("In Progress" if has_any else "Pending")
                        tag = "done" if has_all else ("scanning" if has_any else "pending")

                        row_values = [animal_id_to_change] + merged_measurements + [status]
                        self.table.item(child, values=tuple(row_values), tags=(tag,))
                        updated = True
                        # Force table to refresh/redraw
                        self.table.update_idletasks()
                        break
                if updated:
                    print(f"Table display updated for animal {animal_id_to_change}")
                    # Keep summary tiles in sync with the updated table.
                    try:
                        self.get_values_for_date()
                    except Exception:
                        pass
                else:
                    print(f"Warning: Could not find animal {animal_id_to_change} in table")
            except Exception as table_error:
                print(f"Error updating table display: {table_error}")

            # Autosave: Commit and save the database file
            if hasattr(self.database, 'db_file') and self.database.db_file != ":memory:":
                try:
                    # Ensure all changes are committed
                    self.database._conn.commit()
                    print("Changes committed")

                    # Persist temp DB back to the original experiment file when needed.
                    original_path = os.path.abspath(getattr(self, "original_file_path", "") or "")
                    db_path = os.path.abspath(getattr(self.database, "db_file", "") or "")
                    if original_path and db_path and original_path != ":memory:" and db_path != ":memory:" and original_path != db_path:
                        # Do not auto-save into encrypted originals without the password flow.
                        if str(original_path).lower().endswith(".pmouser"):
                            print("Autosave skipped for encrypted experiment; use Save flow.")
                        else:
                            print(f"Autosave backup {db_path} -> {original_path}")
                            if hasattr(self.database, "backup_to_file"):
                                self.database.backup_to_file(original_path)
                            else:
                                save_temp_to_file(db_path, original_path)
                            print("Autosave Success!")
                    else:
                        print("Autosave: committed to SQLite (no backup needed).")

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


                except Exception as save_error:
                    print(f"Autosave failed: {save_error}")
                    print(f"Error type: {type(save_error)}")
                    import traceback
                    print(f"Full traceback: {traceback.format_exc()}")
            return True
        except Exception as e:
            self.raise_warning("Failed to save data for animal.")
            print(f"Top level error: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return False

    def change_selected_value_at(self, animal_id_to_change, measurement_index: int, value):
        """Update a single measurement slot (0-based) for the given animal."""
        try:
            measurement_index = int(measurement_index)
        except Exception:  # pylint: disable=broad-exception-caught
            measurement_index = 0

        if measurement_index < 0:
            measurement_index = 0

        existing = self.get_measurements_for_animal_today(animal_id_to_change)
        if not isinstance(existing, list):
            existing = list(existing) if isinstance(existing, (tuple,)) else [existing]

        if measurement_index >= len(existing):
            existing = existing + ([None] * (measurement_index - len(existing) + 1))

        existing[measurement_index] = value
        ok = self.change_selected_value(animal_id_to_change, existing)
        if ok:
            try:
                measurement_name = None
                if hasattr(self, "measurement_strings") and self.measurement_strings and measurement_index < len(self.measurement_strings):
                    measurement_name = self.measurement_strings[measurement_index]
                measurement_name = str(measurement_name or f"Measurement {measurement_index + 1}")
                self._log_activity(f"Animal {animal_id_to_change}: {measurement_name} = {value}")
            except Exception:
                pass
        return ok

    def get_values_for_date(self):
        '''Gets the data for the current date as a string in YYYY-MM-DD.'''
        self.current_date = str(date.today())
        date_text = "Current Date: " + self.current_date
        try:
            if hasattr(self, "date_label") and self.date_label and self.date_label.winfo_exists():
                self.date_label.configure(text=date_text)
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # Get all measurements for current date
        values = self.database.get_data_for_date(self.current_date)
        values_by_animal = {str(animal_id): measurement_value for animal_id, measurement_value in values}
        column_ids = self.table["columns"] or ()
        measurement_slots = max(len(column_ids) - 2, 1)
        total_count = len(self.table.get_children()) or 0
        done_rows = 0
        remaining_rows = 0
        filled_cells = 0
        total_cells = total_count * measurement_slots

        # Update each row in the table
        for child in self.table.get_children():
            animal_id = self.table.item(child)["values"][0]
            measurement_value = values_by_animal.get(str(animal_id))
            measurement_values = [None] * measurement_slots
            if isinstance(measurement_value, (list, tuple)):
                for index in range(min(measurement_slots, len(measurement_value))):
                    measurement_values[index] = measurement_value[index]
            elif isinstance(measurement_value, str) and measurement_slots > 1 and any(sep in measurement_value for sep in (",", ";", "|")):
                parts = [p.strip() for p in re.split(r"[,\n;/|]+", measurement_value) if p and p.strip()]
                for index in range(min(measurement_slots, len(parts))):
                    measurement_values[index] = parts[index]
            else:
                measurement_values[0] = measurement_value

            def _cell_is_filled(val) -> bool:
                if val is None:
                    return False
                text = str(val).strip()
                return text != "" and text.lower() != "none"

            has_any = any(_cell_is_filled(v) for v in measurement_values)
            has_all = has_any and all(_cell_is_filled(v) for v in measurement_values)
            if has_all:
                done_rows += 1
                status = "Done"
                tag = "done"
            elif has_any:
                status = "In Progress"
                tag = "scanning"
            else:
                status = "Pending"
                tag = "pending"
            if status != "Done":
                remaining_rows += 1
            filled_cells += sum(1 for v in measurement_values if _cell_is_filled(v))

            row_values = [animal_id] + measurement_values + [status]
            self.table.item(child, values=tuple(row_values), tags=(tag,))

        # Update summary tiles (UI only)
        try:
            # Total animals: number of rows
            # Measured today: number of rows that are fully complete ("Done")
            # Remaining: rows that are still Pending or In Progress
            # Completion: percentage of all measurement cells filled across all rows/columns
            completion = int(round((filled_cells / float(total_cells)) * 100)) if total_cells else 0
            if hasattr(self, "total_animals_value") and self.total_animals_value:
                self.total_animals_value.configure(text=str(total_count))
            if hasattr(self, "measured_today_value") and self.measured_today_value:
                self.measured_today_value.configure(text=str(done_rows))
            if hasattr(self, "remaining_value") and self.remaining_value:
                self.remaining_value.configure(text=str(remaining_rows))
            if hasattr(self, "completion_value") and self.completion_value:
                self.completion_value.configure(text=f"{completion}%")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def raise_frame(self):
        '''Raise the frame for this UI'''
        super().raise_frame()
        self.set_status("Ready.")
        self._start_device_polling()


    def press_back_to_menu_button(self):
        '''Navigates back to Experiment Menu.'''
        self.stop_listening()
        self._stop_device_polling()

        # Avoid stacking a new ExperimentMenuUI instance on top of the existing one.
        # The DataCollection page is opened from an ExperimentMenuUI and should return to it directly.
        if getattr(self, "menu_page", None) is not None:
            self.menu_page.raise_frame()
            return

        # Fallback for legacy call-sites that didn't provide a menu_page.
        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
        new_page = ExperimentMenuUI(self.parent, self.current_file_path, None)
        new_page.raise_frame()


    def close_connection(self):
        '''Closes database file.'''
        self.database.close()

class ChangeMeasurementsDialog():
    '''Change Measurement Dialog window.'''
    def __init__(self, parent: CTk, data_collection: DataCollectionUI, measurement_items):
        self.parent = parent
        self.data_collection = data_collection
        # Normalize measurement items to a list of strings.
        if isinstance(measurement_items, (list, tuple)):
            self.measurement_items = [str(m).strip() for m in measurement_items if str(m).strip()]
        else:
            raw = str(measurement_items or "").strip()
            self.measurement_items = [p.strip() for p in re.split(r"[,\n;/|]+", raw) if p and p.strip()]
        if not self.measurement_items:
            self.measurement_items = ["Value"]
        self.database = data_collection.database  # Reference to the updated database
        self.uses_rfid = self.database.experiment_uses_rfid() == 1
        self.auto_animal_ids = data_collection.database.get_all_animals_rfid()  # Get all animal IDs from the database

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
        # Build ordered list of animal ids shown in the table (used for auto-increment).
        self.animal_ids = []
        for child in self.data_collection.table.get_children():
            values = self.data_collection.table.item(child)["values"]
            if values:
                self.animal_ids.append(values[0])

        self.root = root = CTkToplevel(self.parent)
        root.title(f"Modify Measurements for: {animal_id}")
        root.geometry("520x520")
        root.resizable(False, False)
        root.transient(self.parent)
        root.attributes('-topmost', 1)
        root.grid_columnconfigure(0, weight=1)

        CTkLabel(
            root,
            text=f"Animal ID: {animal_id}",
            font=("Segoe UI Semibold", 22),
        ).grid(row=0, column=0, padx=18, pady=(16, 10), sticky="w")

        form = CTkFrame(root, fg_color="transparent")
        form.grid(row=1, column=0, padx=18, pady=(6, 8), sticky="ew")
        form.grid_columnconfigure(1, weight=1)

        self.textboxes = []
        for idx, name in enumerate(self.measurement_items):
            CTkLabel(form, text=f"{name}:", font=("Segoe UI", 16)).grid(
                row=idx, column=0, sticky="w", pady=10
            )
            entry = CTkEntry(form, width=220)
            entry.grid(row=idx, column=1, sticky="ew", padx=(10, 0), pady=10)
            self.textboxes.append(entry)

        if self.textboxes:
            try:
                self.textboxes[0].focus()
            except Exception:
                pass

        actions = CTkFrame(root, fg_color="transparent")
        actions.grid(row=2, column=0, padx=18, pady=(10, 18), sticky="ew")
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        CTkButton(actions, text="Submit", command=lambda: self.finish(animal_id)).grid(
            row=0, column=0, sticky="ew", padx=(0, 8)
        )
        CTkButton(actions, text="Cancel", fg_color="#ef4444", hover_color="#dc2626", command=self.close).grid(
            row=0, column=1, sticky="ew", padx=(8, 0)
        )

        # Automatic collection (legacy): only auto-capture when there is a single measurement.
        if self.data_collection.database.get_measurement_type() == 1 and len(self.measurement_items) == 1:
            self.thread_running = True

            def _auto_capture_once():
                data_handler = None
                try:
                    data_handler = SerialDataHandler("device")
                    data_handler.start()
                    start_time = time.monotonic()
                    while time.monotonic() - start_time < 5.0 and self.thread_running:
                        received_data = data_handler.get_stored_data()
                        if received_data:
                            try:
                                self.textboxes[0].delete(0, END)
                                self.textboxes[0].insert(0, str(received_data).strip())
                            except Exception:
                                pass
                            break
                        time.sleep(0.1)
                except Exception:
                    pass
                finally:
                    if data_handler:
                        try:
                            data_handler.stop()
                        except Exception:
                            pass

                if self.thread_running:
                    self.data_collection.after(0, lambda: self.finish(animal_id))

                    # Non-RFID auto-increment: reopen for next animal automatically.
                    if not self.uses_rfid and animal_id in self.animal_ids:
                        try:
                            current_index = self.animal_ids.index(animal_id)
                        except ValueError:
                            current_index = -1
                        next_index = current_index + 1
                        if 0 <= next_index < len(self.animal_ids):
                            next_animal_id = self.animal_ids[next_index]
                            self.data_collection.after(
                                150,
                                lambda aid=next_animal_id: [
                                    self.data_collection.select_animal_by_id(aid),
                                    self.open(aid),
                                ],
                            )

            threading.Thread(target=_auto_capture_once, daemon=True).start()

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
                value = None
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
