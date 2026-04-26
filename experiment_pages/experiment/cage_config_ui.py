'''Contains cage configuration page and behaviour.'''
from customtkinter import *
from shared.tk_models import *
from tkinter import messagebox
from databases.database_controller import DatabaseController
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND, ERROR_SOUND
from shared.file_utils import save_temp_to_file
from shared.hid_wedge import HIDWedgeListener

class CageConfigurationUI(MouserPage):
    '''The Frame that allows user to configure the cages.'''
    def __init__(self, database, parent: CTk, prev_page: CTkFrame = None, file_path = ''):
        super().__init__(parent, "Cage Configuration", prev_page)
        try:
            self.canvas.itemconfigure(self.rectangle, state="hidden")
        except Exception:
            pass

        self._hid_listener = None
        self._rfid_enabled_var = BooleanVar(value=True)
        self._rfid_entry_var = StringVar(value="")
        self._rfid_status_label = None
        self._rfid_entry = None
        self._uses_rfid = False
        self.bind("<Destroy>", self._on_destroy, add="+")

        # Match the Experiment Menu palette for a consistent look across pages.
        # (See: experiment_pages/experiment/experiment_menu_ui.py)
        palette = {
            # Backgrounds
            "bg": ("#f1f5f9", "#0b1220"),
            "surface": ("#ffffff", "#0b1220"),
            "surface_alt": ("#ffffff", "#0b1220"),
            "card_border": ("#e2e8f0", "#223044"),
            # Text
            "text": ("#0f172a", "#e5e7eb"),
            "text_muted": ("#64748b", "#94a3b8"),
            # Accents
            "accent_blue": "#3b82f6",
            "accent_violet": "#8b5cf6",
            "accent_teal": "#14b8a6",
            "accent_amber": "#f59e0b",
            "accent_green": "#22c55e",
            "danger": "#ef4444",
            # Selection
            "selected": ("#dbeafe", "#1e3a8a"),  # blue highlight
            # Legacy (kept for compatibility if older code paths reference these)
            "entry_bg": DEFAULT_ENTRY_BG,
            "entry_border": DEFAULT_ENTRY_BORDER,
            # Quick-action tile colors (pulled from Experiment Menu tile styles)
            "tile_analyze_bg": "#eff6ff",
            "tile_analyze_hover": "#dbeafe",
            "tile_summary_bg": "#f5f3ff",
            "tile_summary_hover": "#ede9fe",
            "tile_invest_bg": "#ecfeff",
            "tile_invest_hover": "#cffafe",
            "tile_cage_bg": "#fffbeb",
            "tile_cage_hover": "#fef3c7",
        }
        self.ui_palette = palette
        self.configure(fg_color=palette["bg"])
        self._cage_button_default_fg = palette["accent_blue"]
        self._animal_button_default_fg = ("#eff6ff", "#0b1220")

        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=21,
                height=42,
                width=54,
                font=("Segoe UI Semibold", 15),
                text_color="white",
                fg_color=palette["accent_amber"],
                hover_color="#d97706",
                command=self.press_back_to_menu_button,
            )
            self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=12, anchor="nw")

        # ----------------------------
        # Main Layout (with scrolling)
        # ----------------------------
        body_root = CTkScrollableFrame(self, fg_color="transparent")
        body_root.place(relx=0.5, rely=0.0, y=78, anchor="n", relwidth=0.96, relheight=0.88)
        body_root.grid_columnconfigure(0, weight=1)
        body_root.grid_rowconfigure(1, weight=1)

        title_font = CTkFont(family="Segoe UI Semibold", size=24)
        subtitle_font = CTkFont(family="Segoe UI", size=13)
        section_title_font = CTkFont(family="Segoe UI Semibold", size=15)
        action_font = CTkFont(family="Segoe UI Semibold", size=13)
        entry_font = CTkFont(family="Segoe UI", size=13)

        header = CTkFrame(body_root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(0, 10))
        CTkLabel(
            header,
            text="Cage Configuration",
            font=title_font,
            text_color=palette["text"],
        ).pack(anchor="w")
        CTkLabel(
            header,
            text="Assign animals to groups with smart actions and polished cards.",
            font=subtitle_font,
            text_color=palette["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        content = CTkFrame(body_root, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)

        def section(parent_section: CTkFrame, title: str, *, accent: str, bg_color):
            box = CTkFrame(
                parent_section,
                corner_radius=18,
                fg_color=bg_color,
                border_width=1,
                border_color=palette["card_border"],
            )
            CTkFrame(box, height=6, corner_radius=18, fg_color=accent).pack(fill="x")
            CTkLabel(
                box,
                text=title,
                font=section_title_font,
                text_color=(accent, "#ffffff"),
            ).pack(anchor="w", padx=16, pady=(10, 6))
            body = CTkFrame(box, fg_color="transparent")
            body.pack(fill="both", expand=True, padx=16, pady=(0, 14))
            body.grid_columnconfigure(0, weight=1)
            return box, body

        control_card, control_body = section(
            content,
            "Quick actions",
            accent=palette["accent_blue"],
            bg_color=palette["surface"],
        )
        control_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        control_body.grid_columnconfigure(0, weight=1)

        button_frame = CTkFrame(control_body, fg_color="transparent")
        button_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        button_frame.grid_columnconfigure(2, weight=1)
        button_frame.grid_columnconfigure(3, weight=1)

        auto_button = CTkButton(
            button_frame,
            text='AutoSort',
            fg_color=palette["tile_analyze_bg"],
            hover_color=palette["tile_analyze_hover"],
            text_color=palette["text"],
            border_width=1,
            border_color=palette["accent_blue"],
            corner_radius=14,
            font=action_font,
            command=self.autosort,
        )
        random_button = CTkButton(
            button_frame,
            text='Randomize',
            fg_color=palette["tile_summary_bg"],
            hover_color=palette["tile_summary_hover"],
            text_color=palette["text"],
            border_width=1,
            border_color=palette["accent_violet"],
            corner_radius=14,
            font=action_font,
            command=self.randomize,
        )
        swap_button = CTkButton(
            button_frame,
            text='Swap',
            fg_color=palette["tile_invest_bg"],
            hover_color=palette["tile_invest_hover"],
            text_color=palette["text"],
            border_width=1,
            border_color=palette["accent_teal"],
            corner_radius=14,
            font=action_font,
            command=self.perform_swap,
        )
        move_button = CTkButton(
            button_frame,
            text='Move Selected',
            fg_color=palette["tile_cage_bg"],
            hover_color=palette["tile_cage_hover"],
            text_color=palette["text"],
            border_width=1,
            border_color=palette["accent_amber"],
            corner_radius=14,
            font=action_font,
            command=self.move_animal,
        )

        auto_button.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=4)
        random_button.grid(row=0, column=1, sticky="ew", padx=8, pady=4)
        swap_button.grid(row=0, column=2, sticky="ew", padx=8, pady=4)
        move_button.grid(row=0, column=3, sticky="ew", padx=(8, 0), pady=4)

        self.file_path = file_path
        self.prev_page = prev_page
        self.db = DatabaseController(database)
        try:
            self._uses_rfid = self.db.db.experiment_uses_rfid() == 1
        except Exception:
            self._uses_rfid = False

        self._build_rfid_scan_ui(control_body, entry_font=entry_font, accent=palette["accent_teal"])
        self._init_hid_scan_listener()

        layout_card, layout_body = section(
            content,
            "Cage layout",
            accent=palette["accent_violet"],
            bg_color=palette["surface_alt"],
        )
        layout_card.grid(row=1, column=0, sticky="nsew")
        layout_body.grid_rowconfigure(0, weight=1)
        layout_body.grid_columnconfigure(0, weight=1)

        self.config_frame = CTkFrame(layout_body, corner_radius=18, fg_color="transparent")
        self.config_frame.grid(row=0, column=0, sticky="nsew")
        self.config_frame.grid_columnconfigure(0, weight=1)

        self.animal_buttons = {}
        self.cage_buttons = {}
        self.selected_animals = set()
        self.selected_cage = None

        self.update_config_frame()

    def _build_rfid_scan_ui(self, parent: CTkFrame, *, entry_font: CTkFont, accent: str):
        scan_row = CTkFrame(parent, fg_color="transparent")
        scan_row.grid(row=1, column=0, sticky="ew")
        scan_row.grid_columnconfigure(1, weight=1)

        label = "RFID scan" if self._uses_rfid else "Scan animal ID"
        CTkLabel(
            scan_row,
            text=label,
            font=CTkFont(family="Segoe UI Semibold", size=12),
            text_color=self.ui_palette["text"],
        ).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(2, 0))

        self._rfid_entry = CTkEntry(
            scan_row,
            textvariable=self._rfid_entry_var,
            placeholder_text="Scan tag and press Enter",
            font=entry_font,
            fg_color=self.ui_palette["entry_bg"],
            border_color=self.ui_palette["entry_border"],
            text_color=self.ui_palette["text"],
            placeholder_text_color=self.ui_palette["text_muted"],
        )
        self._rfid_entry.grid(row=0, column=1, sticky="ew", pady=(2, 0))
        self._rfid_entry.bind("<Return>", self._on_scan_entry_return, add="+")
        self._rfid_entry.bind("<KP_Enter>", self._on_scan_entry_return, add="+")

        CTkSwitch(
            scan_row,
            text="Enable",
            variable=self._rfid_enabled_var,
            onvalue=True,
            offvalue=False,
            command=self._on_toggle_rfid_enabled,
            fg_color=accent,
            progress_color=accent,
        ).grid(row=0, column=2, sticky="e", padx=(10, 0), pady=(2, 0))

        self._rfid_status_label = CTkLabel(
            parent,
            text="RFID scanning enabled (HID keyboard-wedge)."
            if self._uses_rfid
            else "Scanning enabled (HID keyboard-wedge).",
            font=CTkFont(family="Segoe UI", size=12),
            text_color=self.ui_palette["text_muted"],
        )
        self._rfid_status_label.grid(row=2, column=0, sticky="w", pady=(8, 0))

    def _init_hid_scan_listener(self):
        if self._hid_listener:
            try:
                self._hid_listener.stop()
            except Exception:
                pass
            self._hid_listener = None

        def on_tag(tag: str):
            # Ignore global key-capture tags unless this page currently owns focus.
            # Prevents cross-page leakage when this frame remains in memory.
            if not self._is_page_active_for_hid():
                return
            self._handle_scan_value(tag, source="hid")

        self._hid_listener = HIDWedgeListener(self, on_tag=on_tag, capture_all=True)
        self.after(50, self._start_or_stop_hid_listener)

    def _is_page_active_for_hid(self) -> bool:
        """Return True only when focus is inside this page."""
        try:
            focus_widget = self.winfo_toplevel().focus_get()
        except Exception:
            return False
        widget = focus_widget
        while widget is not None:
            if widget is self:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_toggle_rfid_enabled(self):
        self._start_or_stop_hid_listener()

    def _start_or_stop_hid_listener(self):
        if not self._hid_listener:
            return
        enabled = bool(self._rfid_enabled_var.get())
        try:
            if enabled:
                self._hid_listener.start()
                try:
                    self.focus_force()
                except Exception:
                    pass
                self._set_rfid_status(
                    "RFID scanning enabled (Scan Tag)."
                    if self._uses_rfid
                    else "Scanning enabled (scan animal ID)."
                )
            else:
                self._hid_listener.stop()
                self._set_rfid_status("RFID scanning disabled." if self._uses_rfid else "Scanning disabled.")
        except Exception as e:
            self._set_rfid_status(f"RFID listener error: {e}")

    def _stop_hid_scan_listener(self):
        """Stop HID listener safely when navigating away from this page."""
        if not self._hid_listener:
            return
        try:
            self._hid_listener.stop()
        except Exception:
            pass

    def _set_rfid_status(self, message: str):
        if not self._rfid_status_label or not self._rfid_status_label.winfo_exists():
            return
        try:
            self._rfid_status_label.configure(text=message)
        except Exception:
            return

    def _on_scan_entry_return(self, _event=None):
        value = (self._rfid_entry_var.get() or "").strip()
        self._rfid_entry_var.set("")
        if value:
            self._handle_scan_value(value, source="entry")
        return "break"

    def _handle_scan_value(self, scan_value: str, *, source: str):
        scan_value = (scan_value or "").strip()
        if not scan_value:
            return
        if not bool(self._rfid_enabled_var.get()):
            return

        animal_id = None
        try:
            if self._uses_rfid:
                animal_id = self.db.db.get_animal_id(scan_value)
        except Exception:
            animal_id = None

        # Fallback: treat the scanned value as an animal id (useful for non-RFID experiments,
        # or if the reader is configured as a keyboard wedge but tags aren't mapped yet).
        if animal_id is None:
            candidate = scan_value
            if candidate.isdigit():
                try:
                    candidate = str(int(candidate))
                except Exception:
                    pass
            if candidate in getattr(self.db, "valid_ids", []):
                animal_id = candidate

        if animal_id is None:
            if self._uses_rfid:
                self.raise_warning(f"RFID '{scan_value}' is not mapped to an active animal.")
            else:
                self.raise_warning(f"Animal '{scan_value}' was not found.")
            self._set_rfid_status(f"No match for '{scan_value}' ({source}).")
            return

        animal_id = str(animal_id)
        if animal_id not in self.animal_buttons:
            # UI might be stale; refresh once.
            self.update_config_frame()

        if animal_id not in self.animal_buttons:
            self.raise_warning(f"Animal '{animal_id}' is not present on this page.")
            self._set_rfid_status(f"Matched {animal_id}, but not visible ({source}).")
            return

        if animal_id not in self.selected_animals:
            self.selected_animals.add(animal_id)
            self.animal_buttons[animal_id].configure(fg_color=self.ui_palette["selected"])
            self._set_rfid_status(f"Selected animal {animal_id} ({source}).")
        else:
            # Already selected: keep selection and just update status.
            self.animal_buttons[animal_id].configure(fg_color=self.ui_palette["selected"])
            self._set_rfid_status(f"Animal {animal_id} already selected ({source}).")

    def _on_destroy(self, event=None):
        # Avoid stopping the listener for descendant widget destroys.
        if event is not None and getattr(event, "widget", None) is not self:
            return
        self._stop_hid_scan_listener()
        self._hid_listener = None

    def press_back_to_menu_button(self):
        """Stop HID scanning and navigate back to experiment menu."""
        self._stop_hid_scan_listener()
        if getattr(self, "prev_page", None) is not None:
            self.prev_page.raise_frame()

    def raise_frame(self):
        """Resume page-scoped HID scanning only when this page is active."""
        super().raise_frame()
        self._start_or_stop_hid_listener()

    def update_config_frame(self):
        '''Updates the config frame to reflect new information.'''
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.animal_buttons = {}
        self.cage_buttons = {}
        self.create_cage_layout()

    def create_cage_layout(self):
        '''Creates the layout of all cages and their animals.'''
        cages = self.db.get_groups()  # Each group represents a cage
        label_style = CTkFont("Segoe UI Semibold", 13)
        tile_style = CTkFont("Segoe UI", 12)

        self.config_frame.grid_rowconfigure(0, weight=1)
        max_columns = 3

        if not cages:
            empty_state = CTkFrame(
                self.config_frame,
                corner_radius=18,
                fg_color=self.ui_palette["surface"],
                border_width=1,
                border_color=self.ui_palette["card_border"],
            )
            empty_state.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
            CTkLabel(
                empty_state,
                text="No groups configured yet.",
                font=label_style,
                text_color=self.ui_palette["text"],
            ).pack(fill="x", padx=16, pady=(16, 6), anchor="w")
            CTkLabel(
                empty_state,
                text="Go back and set up groups in Group Configuration.",
                font=tile_style,
                text_color=self.ui_palette["text_muted"],
            ).pack(fill="x", padx=16, pady=(0, 16), anchor="w")
            return

        for index, cage_name in enumerate(cages):
            row = index // max_columns
            col = index % max_columns
            cage_frame = CTkFrame(
                self.config_frame,
                corner_radius=18,
                fg_color=self.ui_palette["surface"],
                border_width=1,
                border_color=self.ui_palette["card_border"],
            )
            cage_frame.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
            self.config_frame.grid_columnconfigure(col, weight=1)

            header_bar = CTkFrame(cage_frame, fg_color="transparent")
            header_bar.pack(fill="x", padx=14, pady=(14, 0))
            CTkLabel(
                header_bar,
                text=f"Group {cage_name}",
                font=label_style,
                text_color=self.ui_palette["accent_blue"],
            ).pack(side="left", anchor="w")
            select_label = CTkLabel(
                header_bar,
                text="Select a cage to move animals",
                font=tile_style,
                text_color=self.ui_palette["text_muted"],
            )
            select_label.pack(side="right", anchor="e")

            cage_button = CTkButton(
                cage_frame,
                text=f"{cage_name}",
                command=lambda c=cage_name: self.select_cage(c),
                fg_color=self.ui_palette["accent_blue"],
                hover_color="#2563eb",
                text_color="white",
                font=label_style,
                corner_radius=14,
            )
            cage_button.pack(fill="x", padx=14, pady=(10, 12))
            self.cage_buttons[cage_name] = cage_button

            animals = self.db.get_animals_in_group(cage_name)
            if not animals:
                CTkLabel(
                    cage_frame,
                    text="No animals assigned",
                    text_color=self.ui_palette["text_muted"],
                    font=tile_style,
                ).pack(fill="x", padx=14, pady=(0, 14), anchor="w")
            else:
                for animal in animals:
                    animal_id = str(animal[0])
                    animal_button = CTkButton(
                        cage_frame,
                        text=animal_id,
                        command=lambda a=animal_id: self.toggle_animal_selection(a),
                        fg_color=self._animal_button_default_fg,
                        hover_color="#93c5fd",
                        text_color=self.ui_palette["text"],
                        font=tile_style,
                        corner_radius=12,
                    )
                    animal_button.pack(fill="x", padx=14, pady=4)
                    self.animal_buttons[animal_id] = animal_button

    def select_cage(self, cage_name):
        '''Handles cage selection by updating visual feedback.'''
        button = self.cage_buttons.get(cage_name)
        if button:
            if self.selected_cage == cage_name:
                # Deselect current cage
                self.selected_cage = None
                button.configure(fg_color=self._cage_button_default_fg)
                print(f"Deselected Group: {cage_name}")
            else:
                # Deselect previous cage if any
                if self.selected_cage and self.selected_cage in self.cage_buttons:
                    self.cage_buttons[self.selected_cage].configure(fg_color=self._cage_button_default_fg)

                # Select new cage
                self.selected_cage = cage_name
                button.configure(fg_color=self.ui_palette["selected"])
                print(f"Selected group: {cage_name}")

    def toggle_animal_selection(self, animal_id):
        '''Toggles the selection state of an animal.'''
        button = self.animal_buttons.get(animal_id)
        if button:
            if animal_id in self.selected_animals:
                self.selected_animals.remove(animal_id)
                button.configure(fg_color=self._animal_button_default_fg)
                print(f"Deselected animal: {animal_id}")
            else:
                self.selected_animals.add(animal_id)
                button.configure(fg_color=self.ui_palette["selected"])
                print(f"Selected animal: {animal_id}")
            print(f"Currently selected animals: {self.selected_animals}")
        else:
            print(f"Error: No button found for Animal ID: {animal_id}")

    def randomize(self):
        '''Autosorts the animals into cages.'''
        self.db.randomize_cages()
        self.update_config_frame()
        self.save()
        AudioManager.play(SUCCESS_SOUND)

    def autosort(self):
        '''Calls database's autosort function after user confirmation.'''
        confirmed = messagebox.askyesno(
            title="Confirm AutoSort",
            message="Are you sure you want to AutoSort?\nThis will remove measurements used to sort from the database.",
        )
        if confirmed:
            self.db.autosort()
            self.update_config_frame()
            self.save()
            AudioManager.play(SUCCESS_SOUND)

    def perform_swap(self):
        '''Swaps two selected animals between cages.'''
        if len(self.selected_animals) != 2:
            self.raise_warning("Please select exactly two animals to swap.")
            return

        animal_id1, animal_id2 = self.selected_animals

        # Get the current cages through the database controller
        cage1 = self.db.get_animal_current_cage(animal_id1)
        cage2 = self.db.get_animal_current_cage(animal_id2)

        if cage1 == cage2:
            self.raise_warning("Both animals are in the same cage.")
            return

        # Perform the swap using the database controller
        self.db.update_animal_cage(animal_id1, cage2)  # Move animal 1 to cage 2
        self.db.update_animal_cage(animal_id2, cage1)  # Move animal 2 to cage 1

        self.selected_animals.clear()
        self.update_config_frame()
        self.save()
        AudioManager.play(SUCCESS_SOUND)

    def move_animal(self):
        '''Moves selected animals to a specified cage.'''
        # Check if any animals are selected
        if not self.selected_animals:
            self.raise_warning("Please select at least one animal to move.")
            return

        # Check if exactly one cage is selected
        if not self.selected_cage:
            self.raise_warning("Please select a target cage.")
            return

        target_cage = self.selected_cage  # The display name
        target_group = self.db.get_cage_number(target_cage)  # The internal number

        # Check if moving would exceed cage maximum
        target_cage_count = len(self.db.get_animals_in_group(target_cage))
        if target_cage_count + len(self.selected_animals) > self.db.get_cage_max():
            self.raise_warning(f"Moving these animals would exceed the maximum capacity of {self.db.get_cage_max()}.")
            return

        # Track if any animals were actually moved
        animals_moved = False

        # Move each selected animal
        for animal_id in list(self.selected_animals):  # Convert to list to avoid modifying set during iteration
            # Get current cage of the animal
            current_cage = self.db.get_animal_current_cage(animal_id)

            # Skip if animal is already in target cage
            if current_cage == target_group:
                continue

            # Perform the move using the database controller with internal group number
            self.db.update_animal_cage(animal_id, target_group)
            animals_moved = True

        if not animals_moved:
            self.raise_warning("No animals were moved. They might already be in the target cage.")
            return

        # Clear selections and update the UI
        self.selected_animals.clear()
        self.selected_cage = None
        if target_cage in self.cage_buttons:  # Use display name for button lookup
            self.cage_buttons[target_cage].configure(fg_color=self._cage_button_default_fg)  # Reset cage button color
        self.update_config_frame()
        self.save()
        AudioManager.play(SUCCESS_SOUND)

    def raise_warning(self, message):
        '''Raises a warning dialog with the given message.'''
        palette = getattr(self, "ui_palette", None) or {
            "bg": ("#f8fafc", "#0b1220"),
            "text": ("#0f172a", "#e2e8f0"),
            "text_muted": ("#64748b", "#94a3b8"),
            "accent_amber": "#f59e0b",
        }
        message_window = CTkToplevel(self)
        message_window.title("Warning")
        message_window.geometry('360x140')
        message_window.resizable(False, False)
        message_window.configure(fg_color=palette["bg"])
        message_window.transient(self)
        message_window.attributes('-topmost', 1)
        message_window.grab_set()

        CTkLabel(
            message_window,
            text=message,
            wraplength=320,
            justify=LEFT,
            text_color=palette["text"],
            font=CTkFont("Segoe UI", 12),
        ).pack(fill="x", padx=20, pady=(20, 10))

        ok_button = CTkButton(
            message_window,
            text="OK",
            width=100,
            corner_radius=12,
            fg_color=palette["accent_amber"],
            hover_color="#d97706",
            text_color="white",
            command=message_window.destroy,
        )
        ok_button.pack(pady=(0, 16))

        AudioManager.play(ERROR_SOUND)
        message_window.grab_set()
        message_window.wait_window()

    def save_to_database(self):
        '''Saves updated values to database.'''
        if self.check_num_in_cage_allowed():
            self.db.update_experiment()
            self._stop_hid_scan_listener()
            raise_frame(self.prev_page)
        else:
            self.raise_warning(f'Number of animals in a group must not exceed {self.db.get_cage_max()}')

    def save(self):
        '''Saves current database state to permanent file'''
        try:
            current_file = self.db.db.db_file

            # Ensure all changes are committed
            self.db.commit()
            print("Changes committed")

            # Save back to original file location
            print(f"Saving {current_file} to {self.file_path}")
            save_temp_to_file(current_file, self.file_path)
            print("Save successful!")

        except Exception as e:
            print(f"Error during save: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")

    def check_num_in_cage_allowed(self):
        '''Checks if the number of animals in a group is allowed.'''
        return self.db.check_num_in_cage_allowed()

    def close_connection(self):
        '''Closes database file.'''
        self.db.close()


# Backward-compatible alias used by newer navigation code.
CageConfigUI = CageConfigurationUI
