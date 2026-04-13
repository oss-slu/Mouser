"""New Experiment Module — full functional version with redesigned layout."""

from typing import Optional, List

from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkEntry,
    CTkRadioButton,
    CTkButton,
    CTkFont,
    CTkToplevel,
    StringVar,
    BooleanVar,
    END,
)

from shared.tk_models import MouserPage, ChangePageButton  # pylint: disable=import-error
from experiment_pages.experiment.group_config_ui import (  # pylint: disable=import-error
    GroupConfigUI,
)
from shared.experiment import Experiment  # pylint: disable=import-error
from shared.audio import AudioManager  # pylint: disable=import-error
from shared.file_utils import (  # pylint: disable=import-error
    SUCCESS_SOUND,
    ERROR_SOUND,
)


class NewExperimentUI(  # pylint: disable=too-many-instance-attributes
    MouserPage
):
    """New Experiment user interface (full logic preserved, modern layout)."""

    def __init__(self, parent: CTk, menu_page: Optional[CTkFrame] = None):
        """Initialize the New Experiment form layout and bindings."""
        super().__init__(parent, "", menu_page)
        try:
            self.canvas.itemconfigure(self.rectangle, state="hidden")
        except Exception:
            pass

        palette = {
            "bg": ("#f8fafc", "#0b1220"),
            "header": "#0f172a",
            "text_muted": ("#64748b", "#94a3b8"),
            "card_border": ("#e2e8f0", "#223044"),
            "entry_bg": ("#ffffff", "#0b1220"),
            "entry_border": ("#cbd5e1", "#334155"),
            "accent_blue": "#3b82f6",
            "accent_violet": "#8b5cf6",
            "accent_teal": "#14b8a6",
            "accent_amber": "#f59e0b",
            "accent_green": "#22c55e",
            "danger": "#ef4444",
        }

        self.ui_palette = palette
        self.configure(fg_color=palette["bg"])

        # Page-specific header styling (keeps global MouserPage behavior intact).
        try:
            self.canvas.itemconfig(self.rectangle, fill=palette["header"])
            self.canvas.itemconfig(
                self.title_label,
                fill="white",
                font=("Segoe UI Semibold", 18),
            )
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=40,
                width=160,
                font=("Segoe UI Semibold", 16),
                text_color="white",
                fg_color=palette["accent_amber"],
                hover_color="#d97706",
            )
            self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=8, anchor="nw")

        self.input = Experiment()
        self.menu_page = menu_page
        self.next_button = None
        self.added_invest: List[str] = []

        # ----------------------------
        # Main Layout (no page-level scrolling)
        # ----------------------------
        body_root = CTkFrame(self, fg_color="transparent")
        body_root.place(relx=0.5, rely=0.0, y=66, anchor="n", relwidth=0.96, relheight=0.88)
        body_root.grid_columnconfigure(0, weight=1)
        body_root.grid_rowconfigure(1, weight=1)

        title_font = CTkFont(family="Segoe UI Semibold", size=26)
        subtitle_font = CTkFont(family="Segoe UI", size=14)
        section_title_font = CTkFont(family="Segoe UI Semibold", size=16)
        label_font = CTkFont(family="Segoe UI Semibold", size=13)
        entry_font = CTkFont(family="Segoe UI", size=14)

        header = CTkFrame(body_root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(0, 10))
        CTkLabel(header, text="Create Experiment", font=title_font).pack(anchor="w")
        CTkLabel(
            header,
            text="Step 1 of 3 • Enter core details",
            font=subtitle_font,
            text_color=palette["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        content = CTkFrame(body_root, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 10))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(1, weight=1)

        def section(parent, title: str, *, accent: str, bg_color):
            box = CTkFrame(
                parent,
                corner_radius=14,
                fg_color=bg_color,
                border_width=1,
                border_color=palette["card_border"],
            )
            CTkFrame(box, height=6, corner_radius=14, fg_color=accent).pack(fill="x")
            CTkLabel(
                box,
                text=title,
                font=section_title_font,
                text_color=(accent, "#ffffff"),
            ).pack(anchor="w", padx=14, pady=(8, 6))
            body = CTkFrame(box, fg_color="transparent")
            body.pack(fill="x", padx=14, pady=(0, 10))
            body.grid_columnconfigure(0, weight=1)
            return box, body

        left_box, left = section(
            content,
            "Basics",
            accent=palette["accent_blue"],
            bg_color=("#eff6ff", "#0b1b35"),
        )
        left_box.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))

        right_box, right = section(
            content,
            "Subjects & Data",
            accent=palette["accent_violet"],
            bg_color=("#f5f3ff", "#1b1133"),
        )
        right_box.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 8))

        bottom_box, bottom = section(
            content,
            "Allocation",
            accent=palette["accent_teal"],
            bg_color=("#ecfeff", "#042f2e"),
        )
        bottom_box.grid(row=1, column=0, columnspan=2, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_columnconfigure(2, weight=1)

        def labeled_entry(parent, label: str, required: bool = False, **entry_kwargs) -> CTkEntry:
            label_text = f"{label} *" if required else label
            CTkLabel(parent, text=label_text, font=label_font).grid(
                row=labeled_entry.row, column=0, sticky="w", pady=(0, 4)
            )
            entry = CTkEntry(parent, font=entry_font, **entry_kwargs)
            entry.configure(
                fg_color=palette["entry_bg"],
                border_color=palette["entry_border"],
                text_color=("black", "white"),
                placeholder_text_color=palette["text_muted"],
            )
            entry.grid(row=labeled_entry.row + 1, column=0, sticky="ew", pady=(0, 10))
            labeled_entry.row += 2
            return entry

        labeled_entry.row = 0

        self.exper_name = labeled_entry(
            left,
            "Experiment Name",
            required=True,
            placeholder_text="e.g., Dose Response A",
        )

        self.password = labeled_entry(
            left,
            "Password (optional)",
            show="*",
            placeholder_text="Leave blank for none",
        )

        # Investigators field with an add button and chip list
        CTkLabel(left, text="Investigators", font=label_font).grid(
            row=labeled_entry.row, column=0, sticky="w", pady=(0, 6)
        )
        invest_row = CTkFrame(left, fg_color="transparent")
        invest_row.grid(row=labeled_entry.row + 1, column=0, sticky="ew", pady=(0, 6))
        invest_row.grid_columnconfigure(0, weight=1)

        self.investigators = CTkEntry(
            invest_row,
            font=entry_font,
            placeholder_text="Type a name and press Enter",
        )
        self.investigators.configure(
            fg_color=palette["entry_bg"],
            border_color=palette["entry_border"],
            text_color=("black", "white"),
            placeholder_text_color=palette["text_muted"],
        )
        self.investigators.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        add_invest_button = CTkButton(
            invest_row,
            text="Add",
            width=64,
            height=32,
            corner_radius=10,
            fg_color=palette["accent_violet"],
            hover_color="#6d28d9",
            text_color="white",
            font=CTkFont(family="Segoe UI Semibold", size=13),
            command=lambda: [
                self.add_investigator(),
                self.investigators.delete(0, END),
            ],
        )
        add_invest_button.grid(row=0, column=1, sticky="e")

        self.invest_frame = CTkFrame(left, fg_color="transparent")
        self.invest_frame.grid(row=labeled_entry.row + 2, column=0, sticky="ew", pady=(0, 8))
        left.grid_columnconfigure(0, weight=1)
        labeled_entry.row += 3

        labeled_entry.row = 0
        self.species = labeled_entry(
            right,
            "Species",
            required=True,
            placeholder_text="e.g., Mouse",
        )

        self.measure_items = labeled_entry(
            right,
            "Measurement Item",
            required=False,
            placeholder_text="e.g., Weight",
            textvariable=StringVar(value="Weight"),
        )

        CTkLabel(right, text="RFID", font=label_font).grid(
            row=labeled_entry.row, column=0, sticky="w", pady=(0, 6)
        )
        self.rfid = BooleanVar(value=True)
        self.rfid_frame = CTkFrame(right, fg_color="transparent")
        self.rfid_frame.grid(row=labeled_entry.row + 1, column=0, sticky="w", pady=(0, 12))
        CTkRadioButton(
            self.rfid_frame,
            text="Yes",
            variable=self.rfid,
            value=1,
            font=entry_font,
            fg_color=palette["accent_teal"],
            hover_color="#0d9488",
        ).grid(row=0, column=0, padx=(0, 12), pady=0)
        CTkRadioButton(
            self.rfid_frame,
            text="No",
            variable=self.rfid,
            value=0,
            font=entry_font,
            fg_color=palette["accent_teal"],
            hover_color="#0d9488",
        ).grid(row=0, column=1, padx=(0, 0), pady=0)

        CTkLabel(bottom, text="Number of Animals *", font=label_font).grid(
            row=0, column=0, sticky="w", pady=(0, 6)
        )
        CTkLabel(bottom, text="Number of Groups *", font=label_font).grid(
            row=0, column=1, sticky="w", pady=(0, 6), padx=(12, 0)
        )
        CTkLabel(bottom, text="Max Animals per Cage *", font=label_font).grid(
            row=0, column=2, sticky="w", pady=(0, 6), padx=(12, 0)
        )

        self.animal_num = CTkEntry(bottom, font=entry_font, placeholder_text="e.g., 24")
        self.group_num = CTkEntry(bottom, font=entry_font, placeholder_text="e.g., 3")
        self.num_per_cage = CTkEntry(bottom, font=entry_font, placeholder_text="e.g., 8")
        for entry in (self.animal_num, self.group_num, self.num_per_cage):
            entry.configure(
                fg_color=palette["entry_bg"],
                border_color=palette["entry_border"],
                text_color=("black", "white"),
                placeholder_text_color=palette["text_muted"],
            )

        self.animal_num.grid(row=1, column=0, sticky="ew")
        self.group_num.grid(row=1, column=1, sticky="ew", padx=(12, 0))
        self.num_per_cage.grid(row=1, column=2, sticky="ew", padx=(12, 0))

        self.required_hint = CTkLabel(
            body_root,
            text="Fields marked * are required.",
            font=subtitle_font,
            text_color=palette["text_muted"],
        )
        self.required_hint.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 0))

        # Next button and field tracking
        self.create_next_button()
        self.bind_all_entries()

    # ------------------------------------------------------------
    # Navigation + Buttons
    # ------------------------------------------------------------
    def create_next_button(self):
        """Create the Next button that validates and navigates."""
        if self.next_button:
            self.next_button.destroy()

        self.next_button = ChangePageButton(
            self,
            next_page=None,
            previous=False,
        )
        self.next_button.configure(
            corner_radius=12,
            height=40,
            width=160,
            font=("Segoe UI Semibold", 16),
            text_color="white",
            fg_color=self.ui_palette["accent_green"],
            hover_color="#16a34a",
            text="Continue",
            command=lambda: [
                self.check_animals_divisible(),
                self._go_next(),
            ],
            state="disabled",
        )
        self.next_button.place_configure(relx=1.0, rely=0.0, x=-16, y=8, anchor="ne")

    def bind_all_entries(self):
        """Bind entry changes to enable/disable the Next button."""
        fields = [
            self.exper_name,
            self.password,
            self.species,
            self.measure_items,
            self.animal_num,
            self.group_num,
            self.num_per_cage,
        ]
        for entry in fields:
            entry.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.investigators.bind(
            "<Return>",
            lambda event: [
                self.add_investigator(),
                self.investigators.delete(0, END),
            ],
        )

    def enable_next_button(self):
        """Enable Next only when all required fields are filled."""
        required = [
            self.exper_name.get().strip(),
            self.species.get().strip(),
            self.animal_num.get().strip(),
            self.group_num.get().strip(),
            self.num_per_cage.get().strip(),
        ]
        if all(required):
            self.next_button.configure(state="normal")
        else:
            self.next_button.configure(state="disabled")

    # ------------------------------------------------------------
    # Investigator Logic
    # ------------------------------------------------------------
    def update_invest_frame(self):
        """Refresh the investigator list in the UI."""
        for widget in self.invest_frame.winfo_children():
            widget.destroy()

        for i, investigator in enumerate(self.added_invest):
            chip = CTkFrame(
                self.invest_frame,
                fg_color=("#f3f4f6", "#111827"),
                corner_radius=999,
                border_width=1,
                border_color=("#e5e7eb", "#374151"),
            )
            chip.grid(row=i // 3, column=i % 3, sticky="w", padx=(0, 10), pady=(0, 10))

            CTkLabel(
                chip,
                text=investigator,
                font=CTkFont(family="Segoe UI", size=13),
            ).pack(side="left", padx=(12, 6), pady=6)

            CTkButton(
                chip,
                text="×",
                width=28,
                height=28,
                corner_radius=999,
                fg_color="#ef4444",
                hover_color="#b91c1c",
                text_color="white",
                font=CTkFont(family="Segoe UI Semibold", size=14),
                command=lambda x=investigator: self.remove_investigator(x),
            ).pack(side="left", padx=(0, 8), pady=6)

    def add_investigator(self):
        """Add an investigator to the list if not already present."""
        val = self.investigators.get().strip()
        if val and val not in self.added_invest:
            self.added_invest.append(val)
            self.update_invest_frame()

    def remove_investigator(self, person: str):
        """Remove an investigator from the list."""
        if person in self.added_invest:
            self.added_invest.remove(person)
            self.update_invest_frame()

    # ------------------------------------------------------------
    # Validation / Warnings
    # ------------------------------------------------------------
    def raise_warning(self, message: str, title: str = "Warning"):
        """Display a modal warning dialog."""

        dialog = CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x190")
        dialog.resizable(False, False)

        def dismiss(_event=None):  # pylint: disable=unused-argument
            try:
                dialog.grab_release()
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            dialog.destroy()

        CTkLabel(
            dialog,
            text=message,
            wraplength=380,
            font=("Segoe UI", 14),
            justify="left",
        ).pack(padx=16, pady=(18, 10), anchor="w")

        CTkButton(
            dialog,
            text="OK",
            width=90,
            height=34,
            corner_radius=10,
            fg_color=self.ui_palette["accent_blue"],
            hover_color="#1d4ed8",
            text_color="white",
            font=("Segoe UI Semibold", 14),
            command=dismiss,
        ).pack(pady=(0, 16))

        AudioManager.play(ERROR_SOUND)
        dialog.bind("<Escape>", dismiss)
        dialog.bind("<Return>", dismiss)
        dialog.focus_force()
        dialog.grab_set()

    def check_animals_divisible(self):
        """Validate animal counts vs. groups and cage capacity."""
        raw_animals = self.animal_num.get().strip()
        raw_groups = self.group_num.get().strip()
        raw_max = self.num_per_cage.get().strip()

        if not all([raw_animals, raw_groups, raw_max]):
            self.raise_warning("Please fill out all required allocation fields.")
            return

        try:
            animals = int(raw_animals)
            groups = int(raw_groups)
            max_per_cage = int(raw_max)
        except ValueError:
            self.raise_warning("Allocation fields must be whole numbers (e.g., 24, 3, 8).")
            return

        if animals <= 0 or groups <= 0 or max_per_cage <= 0:
            self.raise_warning(
                "Number of animals, groups, and max animals per cage must be greater than 0."
            )
            return

        if animals > (groups * max_per_cage):
            self.raise_warning(
                "Unequal Group Size: Please ensure total animals are less than or equal to group capacity."
            )
            return

        self.save_input()

    # ------------------------------------------------------------
    # Save + Navigation
    # ------------------------------------------------------------
    def save_input(self):
        """Persist the form values into the Experiment model."""
        self.input.set_name(self.exper_name.get())
        if self.password.get():
            self.input.set_password(self.password.get())
        self.input.set_unique_id()

        investigators = self.added_invest.copy()
        if self.investigators.get().strip():
            investigators.append(self.investigators.get().strip())
        self.input.set_investigators(investigators)

        self.input.set_species(self.species.get())
        self.input.set_measurement_item(self.measure_items.get())
        self.input.set_uses_rfid(self.rfid.get())
        self.input.set_num_animals(self.animal_num.get())
        self.input.set_num_groups(self.group_num.get())
        self.input.set_max_animals(self.num_per_cage.get())
        AudioManager.play(SUCCESS_SOUND)

    def _go_next(self):
        """Navigate to Group Configuration with the current Experiment."""
        page = GroupConfigUI(self.input, self.root, self, self.menu_page)
        page.raise_frame()
