'''Data collection ui module.'''
from datetime import date
import re
import csv
import tkinter as tk
from tkinter.ttk import Treeview, Style
from tkinter import dialog, filedialog
import time
import sqlite3
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

#pylint: disable= undefined-variable
class DataCollectionUI(MouserPage):
    '''Page Frame for Data Collection.'''

    def __init__(self, parent: CTk, prev_page: CTkFrame = None, database_name = "", file_path = ""):

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

        self.current_file_path = file_path
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
            # Render units on a second line when written like "Weight (g)".
            match = re.match(r"^(.*)\s+\((.*)\)\s*$", text)
            if match:
                return f"{match.group(1).strip()}\n({match.group(2).strip()})"
            # Normalize common labels used by devices.
            lowered = text.lower()
            if lowered == "caliper":
                return "Length\n(mm)"
            if lowered == "weight":
                return "Weight\n(g)"
            return text

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
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)

        self.left_panel = CTkFrame(body, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.left_panel.grid_columnconfigure(0, weight=1)
        # Layout: header, summary tiles, controls, table, spacer.
        self.left_panel.grid_rowconfigure(0, weight=0)
        self.left_panel.grid_rowconfigure(1, weight=0)
        self.left_panel.grid_rowconfigure(2, weight=0)
        self.left_panel.grid_rowconfigure(3, weight=0)
        self.left_panel.grid_rowconfigure(4, weight=1)

        self.right_panel = CTkFrame(body, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
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
            "Measured\ntoday",
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
        self.table_frame.grid_rowconfigure(0, weight=0)

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

        for i, column in enumerate(columns):
            if column == "animal_id":
                text = "Animal"
                width = 160
            elif column == "status":
                text = "Status"
                width = 120
            else:
                text = _format_measurement_header(str(column))
                width = 130

            print(f"Setting heading for column: {column} with text: {text}")  # Debugging line
            if text:  # Only set heading if text is not empty
                self.table.heading(column, text=text, anchor="center")
            self.table.column(column, anchor="center", width=width, stretch=True)

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

        self.date_label = CTkLabel(self, text="Current Date: --")
        self.date_label.place_forget()

        for animal in self.animals:
            animal_id = animal[0]
            values = [animal_id, *([None] * len(display_measurements)), "Pending"]
            self.table.insert("", END, values=tuple(values), tags=("pending",))

        # Right sidebar (UI-only scaffolding; no device logic wired yet)
        devices_card = CTkFrame(
            self.right_panel,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        devices_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        devices_card.grid_columnconfigure(0, weight=1)

        CTkLabel(
            devices_card,
            text="Devices",
            font=CTkFont("Segoe UI Semibold", 14),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 0))
        CTkLabel(
            devices_card,
            text="4 registered · 2 connected",
            font=CTkFont("Segoe UI", 12),
            text_color=self._palette["muted_text"],
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 10))

        def _device_row(parent_frame, row_index, title, subtitle, state):
            def _parse_com_port(subtitle_text: str):
                if not subtitle_text:
                    return None, ""
                match = re.search(r"\bCOM\d+\b", str(subtitle_text), flags=re.IGNORECASE)
                if not match:
                    return None, str(subtitle_text).strip()
                com_port = match.group(0).upper()
                remainder = (str(subtitle_text)[: match.start()] + str(subtitle_text)[match.end() :]).strip()
                remainder = re.sub(r"^[\s\u00c2\u00b7\u2022·•\-\u2013\u2014|:]+", "", remainder).strip()
                return com_port, remainder

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
            row.grid(row=row_index, column=0, sticky="ew", padx=14, pady=4)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)

            com_port, subtitle_line = _parse_com_port(subtitle)
            title_text = title if not subtitle_line else f"{title} ({subtitle_line})"

            CTkLabel(
                row,
                text=title_text,
                font=CTkFont("Segoe UI Semibold", 13),
                text_color=self._palette["text"],
            ).grid(row=0, column=0, sticky="w", padx=12, pady=8)

            if com_port:
                CTkLabel(
                    row,
                    text=com_port,
                    font=CTkFont("Segoe UI Semibold", 12),
                    text_color=self._palette["muted_text"],
                ).grid(row=0, column=1, sticky="e", padx=(0, 10), pady=8)
            CTkLabel(
                row,
                text="●",
                font=CTkFont("Segoe UI Semibold", 14),
                text_color=_pick(colors["dot"]),
            ).grid(row=0, column=2, sticky="e", padx=12, pady=8)

        _device_row(devices_card, 2, "Balance", "COM3 · g", "ok")
        _device_row(devices_card, 3, "Caliper", "COM5 · mm", "ok")
        _device_row(devices_card, 4, "Glucometer", "COM7 · error", "error")
        _device_row(devices_card, 5, "RFID reader", "COM9 · idle", "idle")

        CTkButton(
            devices_card,
            text="+  Add device",
            height=38,
            corner_radius=12,
            fg_color=self._palette["card_bg"],
            hover_color=_pick(self._palette["table_alt_bg"]),
            border_width=1,
            border_color=_pick(self._palette["card_border"]),
            text_color=_pick(self._palette["text"]),
            font=CTkFont("Segoe UI Semibold", 13),
        ).grid(row=6, column=0, sticky="ew", padx=14, pady=(8, 14))

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

        log_frame = CTkScrollableFrame(
            activity_card, fg_color="transparent", corner_radius=0, border_width=0, height=215
        )
        log_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
        log_frame.grid_columnconfigure(0, weight=1)

        CTkFrame(self.right_panel, fg_color="transparent").grid(row=2, column=0, sticky="nsew")

        for line in [
            ("09:41", "Saved 24.3 g for Mouse 004"),
            ("09:39", "Mouse 003 fully measured"),
            ("09:35", "COM7 error — glucometer lost"),
            ("09:31", "Session started · 8 animals"),
            ("09:30", "Balance COM3 connected"),
        ]:
            CTkLabel(
                log_frame,
                text=f"{line[0]}   {line[1]}",
                font=CTkFont("Segoe UI", 12),
                text_color=self._palette["muted_text"],
                anchor="w",
            ).grid(sticky="w", padx=4, pady=4)


        self.get_values_for_date()

        self.table.bind('<<TreeviewSelect>>', self.item_selected)
        self.table.bind("<1>", self._on_table_click)
        
        # Initialize inline editor tracking
        self._inline_editor = None

        self.changer = ChangeMeasurementsDialog(parent, self, self.measurement_strings)

    def showSaveFileDialog(self):
        '''Opens a file dialog for the user to select where to save the CSV file.'''
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save CSV"
        )
        return file_path
    
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
        all_measurements_today = self.database.get_data_for_date(today_date)
        measurement_names = self.get_measurement_names()
        animal_measurements_dict = {}

        for record in all_measurements_today:
            record_animal_id = record[0]
            # Legacy DB queries may return (animal_id, value) only.
            measurement_name = record[1] if len(record) > 2 else (measurement_names[0] if measurement_names else "Value")
            measurement_value = record[2] if len(record) > 2 else (record[1] if len(record) > 1 else None)

            if str(record_animal_id) == str(animal_id):
                animal_measurements_dict[measurement_name] = measurement_value

        ordered_measurements = []
        for name in measurement_names:
            if name in animal_measurements_dict:
                ordered_measurements.append(animal_measurements_dict[name])
            else:
                ordered_measurements.append(None)  # placeholder if no measurement

        return ordered_measurements
    
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
            
            # Clean up editor first to prevent visual issues
            cleanup_editor()
            
            # Then update the value (which will update both DB and table display)
            if self.change_selected_value(animal_id, [new_val]):
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

        if self.rfid_thread and self.rfid_thread.is_alive():
            print("⚠️ RFID listener is already running!")
            self.set_status("RFID listener already running.")
            return  # Prevent multiple listeners
        self.set_status("Starting RFID listener...")
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

    def stop_listening(self):
        '''Stops the RFID listener and ensures the serial port is released.'''
        print("🛑 Stopping RFID listener...")
        self.set_status("Stopping listener...")

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
        self._measurement_in_progress = False
        print("✅ RFID listener cleanup completed.")
        self._set_scan_button_state(False)
        self.set_status("Listener stopped.")

        # Safely stop and close the changer
        if hasattr(self, 'changer'):
            self.changer.stop_thread()  # Stop the changer thread if it's running
            self.changer.close()  # Close the changer dialog if it's open

    def process_scanned_animal(self, animal_id):
        """Select scanned animal and capture weight for that animal."""
        self.select_animal_by_id(animal_id)
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
            new_value = float(list_of_values[0])
            print(f"Saving data point for animal {animal_id_to_change}: {new_value}")

            # Write change to database
            self.database.change_data_entry(str(date.today()), animal_id_to_change, new_value, 1)
            print("Database entry updated")

            # Update display table
            try:
                updated = False
                for child in self.table.get_children():
                    table_animal_id = self.table.item(child)["values"][0]
                    # Handle type conversions for comparison
                    if str(animal_id_to_change) == str(table_animal_id):
                        column_ids = self.table["columns"] or ()
                        measurement_slots = max(len(column_ids) - 2, 1)
                        measurement_values = list(list_of_values[:measurement_slots]) if isinstance(list_of_values, (list, tuple)) else [new_value]
                        measurement_values = [None if v is None or str(v).strip() == "" else v for v in measurement_values]
                        measurement_values = (measurement_values + ([None] * measurement_slots))[:measurement_slots]
                        row_values = [animal_id_to_change] + measurement_values + ["Done"]
                        self.table.item(child, values=tuple(row_values), tags=("done",))
                        updated = True
                        # Force table to refresh/redraw
                        self.table.update_idletasks()
                        break
                if updated:
                    print(f"Table display updated for animal {animal_id_to_change}")
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
        done_count = 0
        total_count = len(self.table.get_children()) or 0

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
            if measurement_value is not None:
                done_count += 1
                status = "Done"
                tag = "done"
            else:
                status = "Pending"
                tag = "pending"

            row_values = [animal_id] + measurement_values + [status]
            self.table.item(child, values=tuple(row_values), tags=(tag,))

        # Update summary tiles (UI only)
        try:
            remaining = max(total_count - done_count, 0)
            completion = int(round((done_count / float(total_count)) * 100)) if total_count else 0
            if hasattr(self, "total_animals_value") and self.total_animals_value:
                self.total_animals_value.configure(text=str(total_count))
            if hasattr(self, "measured_today_value") and self.measured_today_value:
                self.measured_today_value.configure(text=str(done_count))
            if hasattr(self, "remaining_value") and self.remaining_value:
                self.remaining_value.configure(text=str(remaining))
            if hasattr(self, "completion_value") and self.completion_value:
                self.completion_value.configure(text=f"{completion}%")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def raise_frame(self):
        '''Raise the frame for this UI'''
        super().raise_frame()
        self.set_status("Ready.")


    def press_back_to_menu_button(self):
        '''Navigates back to Experiment Menu.'''
        self.stop_listening()

        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
        new_page = ExperimentMenuUI(self.parent, self.current_file_path, self.menu_page)
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
