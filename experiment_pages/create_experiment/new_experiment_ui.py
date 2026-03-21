from typing import Optional, List

from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkEntry,
    CTkRadioButton,
    CTkButton,
    CTkFont,
    StringVar,
    BooleanVar,
    CTkScrollbar
)

from tkinter import W, END

from shared.tk_models import MouserPage  # pylint: disable=import-error
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
    """New Experiment user interface with improved styling."""

    def __init__(self, parent: CTk, menu_page: Optional[CTkFrame] = None):
        """Initialize the New Experiment form layout and bindings."""
        super().__init__(parent, "New Experiment", menu_page)

        self.configure(fg_color="#eef4ff")
        self.canvas.configure(bg="#eef4ff", highlightthickness=0)
        self.canvas.configure(yscrollincrement=24)
        self._scroll_enabled = False
        self.canvas.itemconfig(
            self.rectangle,
            fill="#0f172a",
            outline="#0f172a",
        )
        self.canvas.itemconfig(
            self.title_label,
            text="New Experiment",
            fill="#f8fafc",
            font=("Segoe UI Semibold", 20),
        )
          
        self.scrollbar = CTkScrollbar(
            self,
            orientation="vertical",
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.menu_button_window = None
        self.next_button_window = None

        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.destroy()
            self.menu_button = CTkButton(
                self.canvas,
                text="←",
                corner_radius=18,
                height=42,
                width=42,
                font=("Segoe UI Semibold", 17),
                command=lambda: self.menu_page.raise_frame(),
                text_color="#f8fafc",
                fg_color="#1d4ed8",
                hover_color="#1e3a8a",
                bg_color="transparent",
                border_width=1,
                border_color="#93c5fd",
            )
            self.menu_button_window = self.canvas.create_window(
                24,
                25,
                anchor="w",
                window=self.menu_button,
            )

        self.input = Experiment()
        self.menu_page = menu_page
        self.next_button = None
        self.added_invest: List[str] = []

        self.font_title = CTkFont("Segoe UI Semibold", 26)
        self.font_section = CTkFont("Segoe UI Semibold", 18)
        self.font_label = CTkFont("Segoe UI Semibold", 15)
        self.font_body = CTkFont("Segoe UI", 14)
        self.font_small = CTkFont("Segoe UI", 13)
        self.field_style = {
            "height": 42,
            "corner_radius": 14,
            "border_width": 1,
            "border_color": "#bfdbfe",
            "fg_color": "#f8fbff",
            "text_color": "#0f172a",
            "font": self.font_body,
        }

        self.main_frame = CTkFrame(
            self.canvas,
            fg_color="#eef4ff",
            corner_radius=0,
        )
        self.main_window = self.canvas.create_window(
            24,
            68,
            anchor="nw",
            window=self.main_frame,
        )
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)

        self._build_form_card()
        self.bind_all_entries()
        self.create_next_button()

    def _build_form_card(self):
        """Create the main form card and all sections."""
        form_card = CTkFrame(
            self.main_frame,
            fg_color="#ffffff",
            corner_radius=28,
            border_width=1,
            border_color="#cbd5e1",
        )
        form_card.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 12))
        form_card.grid_columnconfigure(0, weight=1)
        form_card.grid_columnconfigure(1, weight=1)
        form_card.grid_rowconfigure(2, weight=1)
        form_card.grid_rowconfigure(3, weight=1)

        CTkLabel(
            form_card,
            text="Experiment Details",
            font=CTkFont("Segoe UI Semibold", 24),
            text_color="#0f172a",
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=24, pady=(24, 4))

        basics = self._create_section(form_card, 1, 0, "📝 Basics", "#eff6ff", "#bfdbfe")
        team = self._create_section(form_card, 1, 1, "👩‍🔬 Team", "#f8fafc", "#cbd5e1")
        study = self._create_section(form_card, 2, 0, "🐭 Study Setup", "#f8fffb", "#bbf7d0")
        housing = self._create_section(form_card, 2, 1, "🏠 Housing", "#fff7ed", "#fed7aa")

        basics.grid_columnconfigure(0, weight=1)
        basics.grid_columnconfigure(1, weight=1)

        self._add_field_label(basics, 1, 0, "Experiment Name *")
        self.exper_name = CTkEntry(
            basics,
            width=220,
            placeholder_text="Enter a study name",
            **self.field_style,
        )
        self.exper_name.grid(row=2, column=0, sticky="ew", padx=(18, 10), pady=(0, 12))

        self._add_field_label(basics, 1, 1, "Password")
        self.password = CTkEntry(
            basics,
            width=220,
            placeholder_text="Optional access password",
            show="*",
            **self.field_style,
        )
        self.password.grid(row=2, column=1, sticky="ew", padx=(10, 18), pady=(0, 12))

        self._add_field_label(study, 1, 0, "Species *")
        self.species = CTkEntry(
            study,
            width=220,
            placeholder_text="Mouse, rat, etc.",
            **self.field_style,
        )
        self.species.grid(row=2, column=0, sticky="ew", pady=(0, 12), padx=18)

        self._add_field_label(study, 3, 0, "Measurement Items")
        self.measure_items = CTkEntry(
            study,
            width=220,
            textvariable=StringVar(value="Weight"),
            **self.field_style,
        )
        self.measure_items.grid(row=4, column=0, sticky="ew", pady=(0, 12), padx=18)

        self._add_field_label(study, 5, 0, "RFID")
        self.rfid = BooleanVar(value=True)
        self.rfid_frame = CTkFrame(study, fg_color="transparent")
        self.rfid_frame.grid(row=6, column=0, sticky="w", pady=(0, 4), padx=18)
        self._build_rfid_controls()

        team.grid_columnconfigure(0, weight=1)
        team.grid_columnconfigure(1, weight=0)

        self._add_field_label(team, 1, 0, "Investigators")
        self.investigators = CTkEntry(
            team,
            placeholder_text="Type a name and press Enter",
            **self.field_style,
        )
        self.investigators.grid(row=2, column=0, sticky="ew", padx=(18, 10), pady=(0, 12))

        add_invest_button = CTkButton(
            team,
            text="➕ Add",
            width=92,
            height=42,
            command=lambda: [
                self.add_investigator(),
                self.investigators.delete(0, END),
            ],
            corner_radius=14,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            text_color="#eff6ff",
            font=self.font_label,
        )
        add_invest_button.grid(row=2, column=1, sticky="e", padx=(0, 18), pady=(0, 12))

        self.invest_frame = CTkFrame(
            team,
            fg_color="#f8fbff",
            corner_radius=16,
            border_width=1,
            border_color="#dbeafe",
        )
        self.invest_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=18)
        self.invest_frame.grid_propagate(False)
        self.invest_frame.configure(height=56)

        CTkLabel(
            self.invest_frame,
            text="No investigators added yet.",
            font=self.font_small,
            text_color="#64748b",
        ).place(relx=0.04, rely=0.5, anchor="w")

        housing.grid_columnconfigure(0, weight=1)

        self._add_field_label(housing, 1, 0, "Number of Animals *")
        self.animal_num = CTkEntry(
            housing,
            width=220,
            placeholder_text="Total animals",
            **self.field_style,
        )
        self.animal_num.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 12))

        self._add_field_label(housing, 3, 0, "Number of Groups *")
        self.group_num = CTkEntry(
            housing,
            width=220,
            placeholder_text="Group count",
            **self.field_style,
        )
        self.group_num.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))

        self._add_field_label(housing, 5, 0, "Max Animals per Cage *")
        self.num_per_cage = CTkEntry(
            housing,
            width=220,
            placeholder_text="Capacity per cage",
            **self.field_style,
        )
        self.num_per_cage.grid(row=6, column=0, sticky="ew", padx=18, pady=(0, 6))

    def _create_section(
        self,
        parent,
        row,
        column,
        title,
        fg_color,
        border_color,
    ):
        """Create a stylized section card."""
        frame = CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=22,
            border_width=1,
            border_color=border_color,
        )
        frame.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=24,
            pady=(0, 20),
        )
        frame.grid_columnconfigure(0, weight=1)

        CTkLabel(
            frame,
            text=title,
            font=self.font_section,
            text_color="#0f172a",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 14))
        return frame

    def _add_field_label(self, parent, row, column, text):
        """Create a consistent field label."""
        CTkLabel(
            parent,
            text=text,
            font=self.font_label,
            text_color="#1e293b",
            anchor="w",
        ).grid(row=row, column=column, sticky=W, padx=18, pady=(0, 6))

    def _build_rfid_controls(self):
        """Create the RFID choice buttons."""
        yes_radio = CTkRadioButton(
            self.rfid_frame,
            text="📡 Yes",
            variable=self.rfid,
            value=1,
            font=self.font_body,
            text_color="#0f172a",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            border_color="#60a5fa",
        )
        yes_radio.grid(row=0, column=0, padx=(0, 18), pady=2)

        no_radio = CTkRadioButton(
            self.rfid_frame,
            text="🧾 No",
            variable=self.rfid,
            value=0,
            font=self.font_body,
            text_color="#0f172a",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            border_color="#60a5fa",
        )
        no_radio.grid(row=0, column=1, padx=(0, 8), pady=2)


    def _update_scroll_region(self, _event=None):
        """Enable page scrolling only when content exceeds the visible area."""
        self.update_idletasks()

        content_height = self.main_frame.winfo_reqheight() + 80
        canvas_height = max(self.canvas.winfo_height(), 1)
        self._scroll_enabled = content_height > canvas_height

        if self._scroll_enabled:
            self.canvas.configure(
                scrollregion=(0, 0, self.canvas.winfo_width(), content_height)
            )
            self.scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        else:
            self.canvas.configure(
                scrollregion=(0, 0, self.canvas.winfo_width(), canvas_height)
            )
            self.canvas.yview_moveto(0)
            self.scrollbar.place_forget()

    def _on_canvas_configure(self, event):
        """Resize the embedded content area with the window width."""
        content_width = max(event.width - 56, 320)
        self.canvas.coords(self.main_window, 24, 68)
        self.canvas.itemconfigure(self.main_window, width=content_width)
        if self.menu_button_window is not None:
            self.canvas.coords(self.menu_button_window, 24, 25)
        if self.next_button_window is not None:
            self.canvas.coords(self.next_button_window, event.width - 24, 25)
        self._update_scroll_region()

    def _bind_mousewheel(self, _event=None):
        """Enable mousewheel scrolling while the pointer is on this page."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)

    def _unbind_mousewheel(self, _event=None):
        """Disable page-level mousewheel binding when leaving the page."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")

    def _on_mousewheel(self, event):
        """Scroll the page canvas across supported platforms."""
        if not self._scroll_enabled:
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def create_next_button(self):
        """Create the Next button that validates and navigates."""
        if self.next_button:
            self.next_button.destroy()
        if self.next_button_window is not None:
            self.canvas.delete(self.next_button_window)
            self.next_button_window = None

        self.next_button = CTkButton(
            self.canvas,
            text="→",
            corner_radius=18,
            height=42,
            width=42,
            font=("Segoe UI Semibold", 18),
            text_color="#eff6ff",
            fg_color="#ea580c",
            hover_color="#c2410c",
            bg_color="transparent",
            border_width=1,
            border_color="#fdba74",
            command=lambda: [
                self.check_animals_divisible(),
                self._go_next(),
            ],
            state="disabled",
        )
        self.next_button_window = self.canvas.create_window(
            max(self.canvas.winfo_width() - 24, 24),
            25,
            anchor="e",
            window=self.next_button,
        )

    def bind_all_entries(self):
        """Bind entry changes to enable/disable the Next button."""
        fields = [
            self.exper_name,
            self.password,
            self.species,
            self.measure_items,
            self.animal_num,
            self.num_per_cage,
        ]
        for entry in fields:
            entry.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.group_num.bind("<KeyRelease>", lambda event: self.enable_next_button())
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

    def update_invest_frame(self):
        """Refresh the investigator list in the UI."""
        for widget in self.invest_frame.winfo_children():
            widget.destroy()

        funcs: List = []
        buttons: List[CTkButton] = []

        if not self.added_invest:
            self.invest_frame.configure(height=56)
            CTkLabel(
                self.invest_frame,
                text="No investigators added yet.",
                font=self.font_small,
                text_color="#64748b",
            ).place(relx=0.04, rely=0.5, anchor="w")
            return

        for idx, investigator in enumerate(self.added_invest):
            pill = CTkFrame(
                self.invest_frame,
                fg_color="#e0ecff",
                corner_radius=14,
                border_width=1,
                border_color="#bfdbfe",
            )
            pill.grid(row=idx, column=0, sticky="ew", padx=10, pady=6)
            pill.grid_columnconfigure(0, weight=1)

            CTkLabel(
                pill,
                text=f"👤 {investigator}",
                font=self.font_body,
                text_color="#1e3a8a",
                anchor="w",
            ).grid(row=0, column=0, sticky=W, padx=(12, 8), pady=8)

            rem_button = CTkButton(
                pill,
                text="✖",
                width=34,
                height=30,
                corner_radius=10,
                fg_color="#ef4444",
                hover_color="#b91c1c",
                text_color="#ffffff",
                font=self.font_label,
            )
            rem_button.grid(row=0, column=1, padx=(4, 10), pady=8)
            buttons.append(rem_button)
            funcs.append(lambda x=investigator: self.remove_investigator(x))

        for i, func in enumerate(funcs):
            buttons[i].configure(command=func)

        self.invest_frame.configure(
            height=max(len(self.added_invest) * 54, 56),
        )

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

    def raise_warning(self, option: int):
        """Display a warning window based on a validation code."""

        def dismiss(event=None):  # pylint: disable=unused-argument
            message.destroy()

        message = CTk()
        message.title("Warning")
        message.geometry("390x220")
        message.resizable(False, False)
        message.configure(fg_color="#fff7ed")

        texts = {
            2: (
                "Number of animals, groups, or max animals "
                "per cage must be > 0."
            ),
            3: "Experiment name used. Please use another name.",
            4: (
                "Unequal Group Size: Please ensure total animals "
                "<= group capacity."
            ),
        }

        panel = CTkFrame(
            message,
            fg_color="#ffffff",
            corner_radius=22,
            border_width=1,
            border_color="#fed7aa",
        )
        panel.pack(fill="both", expand=True, padx=18, pady=18)

        CTkLabel(
            panel,
            text="⚠️ Please Check Your Entries",
            font=CTkFont("Segoe UI Semibold", 20),
            text_color="#9a3412",
        ).pack(pady=(20, 10), padx=18)
        CTkLabel(
            panel,
            text=texts.get(option, "Warning"),
            font=self.font_body,
            text_color="#7c2d12",
            justify="center",
            wraplength=300,
        ).pack(pady=(0, 18), padx=20)
        CTkButton(
            panel,
            text="OK",
            width=110,
            height=40,
            command=dismiss,
            corner_radius=14,
            fg_color="#ea580c",
            hover_color="#c2410c",
            text_color="#fff7ed",
            font=self.font_label,
        ).pack(pady=(0, 18))

        AudioManager.play(ERROR_SOUND)
        message.bind("<KeyPress>", dismiss)
        message.bind("<Button>", dismiss)
        message.focus_force()
        message.mainloop()

    def check_animals_divisible(self):
        """Validate animal counts vs. groups and cage capacity."""
        if not all(
            [
                self.animal_num.get(),
                self.group_num.get(),
                self.num_per_cage.get(),
            ]
        ):
            self.raise_warning(2)
        elif int(self.animal_num.get()) == 0 or int(self.group_num.get()) == 0:
            self.raise_warning(2)
        elif int(self.animal_num.get()) > (
            int(self.group_num.get()) * int(self.num_per_cage.get())
        ):
            self.raise_warning(4)
        else:
            self.save_input()

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
