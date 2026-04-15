"""Group configuration UI (Step 2 of 3)."""
# pylint: disable=too-many-instance-attributes, import-error

from __future__ import annotations

from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkRadioButton,
    CTkScrollableFrame,
    CTkFont,
    BooleanVar,
    W,
)

from shared.tk_models import MouserPage, ChangePageButton  # pylint: disable=import-error
from shared.experiment import Experiment  # pylint: disable=import-error
from experiment_pages.create_experiment.summary_ui import SummaryUI  # pylint: disable=import-error


class GroupConfigUI(MouserPage):
    """Configure groups and input method for a new or existing experiment."""

    def __init__(
        self,
        experiment: Experiment,
        parent: CTk,
        prev_page: CTkFrame,
        menu_page: CTkFrame,
        edit_mode: bool = False,
        save_callback=None,
    ):
        super().__init__(parent, "", prev_page)
        try:
            self.canvas.itemconfigure(self.rectangle, state="hidden")
        except Exception:
            pass

        palette = {
            "bg": ("#f8fafc", "#0b1220"),
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

        self.experiment = experiment
        self.menu_page = menu_page
        self.next_button = None
        self.edit_mode = edit_mode
        self.save_callback = save_callback

        # ----------------------------
        # Top Navigation Buttons
        # ----------------------------
        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=36,
                width=54,
                font=("Segoe UI Semibold", 15),
                text_color="white",
                fg_color=palette["accent_amber"],
                hover_color="#d97706",
            )
            self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=8, anchor="nw")

        if self.edit_mode:
            self.create_save_button()
        else:
            self.next_page = SummaryUI(self.experiment, parent, self, menu_page)
            self.create_next_button()

        # ----------------------------
        # Main Layout (scrolling)
        # ----------------------------
        body_root = CTkScrollableFrame(self, fg_color="transparent")
        # Offset content below the top navigation buttons so the title is never covered.
        body_root.place(relx=0.5, rely=0.0, y=78, anchor="n", relwidth=0.96, relheight=0.88)
        body_root.grid_columnconfigure(0, weight=1)
        body_root.grid_rowconfigure(1, weight=1)

        title_font = CTkFont(family="Segoe UI Semibold", size=22)
        subtitle_font = CTkFont(family="Segoe UI", size=12)
        section_title_font = CTkFont(family="Segoe UI Semibold", size=14)
        label_font = CTkFont(family="Segoe UI Semibold", size=12)
        entry_font = CTkFont(family="Segoe UI", size=13)

        header = CTkFrame(body_root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 6))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        header_left = CTkFrame(header, fg_color="transparent")
        header_left.grid(row=0, column=0, sticky="w")
        CTkLabel(header_left, text="Group Configuration", font=title_font).pack(anchor="w")
        CTkLabel(
            header_left,
            text="Step 2 of 3 • Name your groups and choose input method",
            font=subtitle_font,
            text_color=palette["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Step pills removed per UI preference.

        content = CTkFrame(body_root, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        content.grid_columnconfigure(0, weight=1)

        def section(parent_section: CTkFrame, title: str, *, accent: str, bg_color):
            box = CTkFrame(
                parent_section,
                corner_radius=12,
                fg_color=bg_color,
                border_width=1,
                border_color=palette["card_border"],
            )
            CTkFrame(box, height=4, corner_radius=12, fg_color=accent).pack(fill="x")
            CTkLabel(
                box,
                text=title,
                font=section_title_font,
                text_color=(accent, "#ffffff"),
            ).pack(anchor="w", padx=12, pady=(8, 4))
            body = CTkFrame(box, fg_color="transparent")
            body.pack(fill="x", padx=12, pady=(0, 8))
            body.grid_columnconfigure(0, weight=1)
            return box, body

        groups_box, groups_body = section(
            content,
            "Group Names",
            accent=palette["accent_violet"],
            bg_color=("#f5f3ff", "#1b1133"),
        )
        groups_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        self.group_frame = CTkFrame(groups_body, fg_color="transparent")
        self.group_frame.grid(row=0, column=0, sticky="ew")
        self.group_frame.grid_columnconfigure(0, weight=1)
        self.group_frame.grid_columnconfigure(1, weight=1)
        self._label_font = label_font
        self._entry_font = entry_font
        self.create_group_entries(int(self.experiment.get_num_groups()))

        method_box, method_body = section(
            content,
            "Input Method",
            accent=palette["accent_teal"],
            bg_color=("#ecfeff", "#042f2e"),
        )
        method_box.grid(row=1, column=0, sticky="ew")

        self.item_frame = CTkFrame(method_body, fg_color="transparent")
        self.item_frame.grid(row=0, column=0, sticky="ew")
        self.item_frame.grid_columnconfigure(0, weight=1)
        self.item_frame.grid_columnconfigure(1, weight=0)
        self.item_frame.grid_columnconfigure(2, weight=0)
        self.create_item_frame(self.experiment.get_measurement_items())

    # ------------------------------------------------------------
    # Navigation / Buttons
    # ------------------------------------------------------------
    def create_next_button(self):
        """Creates a Continue button aligned top-right."""
        if self.next_button:
            self.next_button.destroy()

        self.next_button = ChangePageButton(self, self.next_page, previous=False)
        self.next_button.configure(
            corner_radius=12,
            height=36,
            width=150,
            font=("Segoe UI Semibold", 15),
            text_color="white",
            fg_color=self.ui_palette["accent_green"],
            hover_color="#16a34a",
            text="Continue",
            command=lambda: [self.save_experiment(), self.next_button.navigate()],
        )
        self.next_button.place_configure(relx=1.0, rely=0.0, x=-16, y=8, anchor="ne")

    def create_save_button(self):
        """Creates a Save & Return button for existing experiment edit flow."""
        if self.next_button:
            self.next_button.destroy()

        self.next_button = CTkButton(
            self,
            text="Save & Return",
            corner_radius=12,
            height=36,
            width=150,
            font=("Segoe UI Semibold", 15),
            text_color="white",
            fg_color=self.ui_palette["accent_green"],
            hover_color="#16a34a",
            command=lambda: [self.save_experiment(), self.menu_page.raise_frame()],
        )
        self.next_button.place_configure(relx=1.0, rely=0.0, x=-16, y=8, anchor="ne")

    # ------------------------------------------------------------
    # Core Functionality
    # ------------------------------------------------------------
    def create_group_entries(self, num):
        """Creates widgets for group entries."""
        self.group_input = []
        existing_names = self.experiment.get_group_names() if hasattr(self.experiment, "get_group_names") else []

        for i in range(num):
            col = 0 if i % 2 == 0 else 1
            row = i // 2

            wrapper = CTkFrame(self.group_frame, fg_color="transparent")
            wrapper.grid(
                row=row,
                column=col,
                sticky="ew",
                padx=(0, 8) if col == 0 else (8, 0),
                pady=(0, 8),
            )
            wrapper.grid_columnconfigure(0, weight=1)

            CTkLabel(
                wrapper,
                text=f"Group {i + 1}",
                font=self._label_font,
            ).grid(row=0, column=0, sticky="w", pady=(0, 2))

            entry = CTkEntry(wrapper, font=self._entry_font, placeholder_text="e.g., Control")
            entry.configure(
                fg_color=self.ui_palette["entry_bg"],
                border_color=self.ui_palette["entry_border"],
                text_color=("black", "white"),
                placeholder_text_color=self.ui_palette["text_muted"],
            )
            entry.grid(row=1, column=0, sticky="ew")
            if i < len(existing_names):
                entry.insert(0, str(existing_names[i]))
            self.group_input.append(entry)

    def create_item_frame(self, item):
        """Creates a radio-button group for input method selection."""
        self.button_vars = []
        self.item_auto_buttons = []
        self.item_man_buttons = []

        initial_value = self.experiment.get_measurement_type()
        self.type = BooleanVar(value=(initial_value != 0))
        self.button_vars.append(self.type)

        CTkLabel(
            self.item_frame,
            text=f"Measurement: {item}",
            font=self._entry_font,
            text_color=self.ui_palette["text_muted"],
        ).grid(row=0, column=0, sticky=W, padx=(0, 10))

        auto = CTkRadioButton(
            self.item_frame,
            text="Automatic",
            variable=self.type,
            value=True,
            font=self._entry_font,
            fg_color=self.ui_palette["accent_teal"],
            hover_color="#0d9488",
        )
        man = CTkRadioButton(
            self.item_frame,
            text="Manual",
            variable=self.type,
            value=False,
            font=self._entry_font,
            fg_color=self.ui_palette["accent_teal"],
            hover_color="#0d9488",
        )

        auto.grid(row=0, column=1, padx=(10, 10), sticky="e")
        man.grid(row=0, column=2, sticky="e")

        self.item_auto_buttons.append(auto)
        self.item_man_buttons.append(man)

    def update_page(self):
        """Updates the UI when experiment data changes."""
        if self.experiment.check_num_groups_change():
            for widget in self.group_frame.winfo_children():
                widget.destroy()
            self.create_group_entries(int(self.experiment.get_num_groups()))
            self.experiment.set_group_num_changed_false()

        if self.experiment.check_measurement_items_changed():
            for widget in self.item_frame.winfo_children():
                widget.destroy()
            self.create_item_frame(self.experiment.get_measurement_items())
            self.experiment.set_measurement_items_changed_false()

    def save_experiment(self):
        """Saves all entered group names and input method."""
        group_names = [entry.get().strip() for entry in self.group_input]
        self.experiment.group_names = group_names
        self.experiment.data_collect_type = 1 if self.button_vars[0].get() else 0
        if callable(self.save_callback):
            self.save_callback(self.experiment)
        if hasattr(self, "next_page") and self.next_page is not None:
            self.next_page.update_page()
