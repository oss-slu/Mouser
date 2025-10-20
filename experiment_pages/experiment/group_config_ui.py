'''Group configuration module (modernized UI, full logic retained).'''
# pylint: disable=too-many-instance-attributes, import-error

from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkEntry,
    CTkButton, CTkRadioButton, BooleanVar, W, LEFT
)
from shared.tk_models import MouserPage, ChangePageButton
from shared.scrollable_frame import ScrolledFrame
from shared.experiment import Experiment
from experiment_pages.create_experiment.summary_ui import SummaryUI


class GroupConfigUI(MouserPage):
    '''Group Configuration user interface (preserves all logic).'''

    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):
        super().__init__(parent, "New Experiment - Group Configuration", prev_page)
        self.experiment = experiment
        self.menu_page = menu_page
        self.next_button = None

        # ----------------------------
        # Top Navigation Buttons
        # ----------------------------
        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=50,
                width=180,
                font=("Segoe UI Semibold", 18),
                text_color="white",
                fg_color="#2563eb",
                hover_color="#1e40af",
            )
            self.menu_button.place_configure(relx=0.05, rely=0.13, anchor="w")

        # Set next page (Summary)
        self.next_page = SummaryUI(self.experiment, parent, self, menu_page)
        self.create_next_button()

        # ----------------------------
        # Scrollable Content Area
        # ----------------------------
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.5, rely=0.58, relheight=0.7, relwidth=0.9, anchor="center")

        # --- Main container card ---
        self.main_frame = CTkFrame(
            scroll_canvas,
            corner_radius=16,
            border_width=1,
            border_color="#d1d5db",
            fg_color=("white", "#2c2c2c"),
        )
        self.main_frame.pack(expand=True, pady=10)

        # Title label
        CTkLabel(
            self.main_frame,
            text="Group Configuration",
            font=("Segoe UI Semibold", 22),
        ).pack(pady=(15, 10))

        # --- Inner content card ---
        content_card = CTkFrame(
            self.main_frame,
            fg_color=("white", "#1f2937"),
            corner_radius=12,
        )
        content_card.pack(padx=40, pady=(5, 15), fill="x")

        # --- Group Name entries ---
        self.group_frame = CTkFrame(content_card, fg_color="transparent")
        self.group_frame.pack(pady=(15, 5))
        self.create_group_entries(int(self.experiment.get_num_groups()))

        # --- Input Method Section ---
        self.item_frame = CTkFrame(content_card, fg_color="transparent")
        self.item_frame.pack(pady=(5, 20))
        self.create_item_frame(self.experiment.get_measurement_items())

    # ------------------------------------------------------------
    # Navigation / Buttons
    # ------------------------------------------------------------
    def create_next_button(self):
        '''Creates a Next button aligned top-right.'''
        if self.next_button:
            self.next_button.destroy()

        self.next_button = ChangePageButton(self, self.next_page, previous=False)
        self.next_button.configure(
            corner_radius=12,
            height=50,
            width=180,
            font=("Segoe UI Semibold", 18),
            text_color="white",
            fg_color="#2563eb",
            hover_color="#1e40af",
            command=lambda: [self.save_experiment(), self.next_button.navigate()],
        )
        self.next_button.place_configure(relx=0.93, rely=0.13, anchor="e")

    # ------------------------------------------------------------
    # Core Functionality
    # ------------------------------------------------------------
    def create_group_entries(self, num):
        '''Creates widgets for group entries.'''
        CTkLabel(
            self.group_frame,
            text="Group Name",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, padx=10, pady=10, sticky=W)

        self.group_input = []
        for i in range(num):
            entry = CTkEntry(self.group_frame, width=220, font=("Segoe UI", 16))
            entry.grid(row=i + 1, column=0, padx=10, pady=8)
            self.group_input.append(entry)

    def create_item_frame(self, item):
        '''Creates a radio-button group for input method selection.'''
        self.button_vars = []
        self.item_auto_buttons = []
        self.item_man_buttons = []

        CTkLabel(
            self.item_frame,
            text="Input Method",
            font=("Segoe UI", 18, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=10)

        self.type = BooleanVar(value=True)
        self.button_vars.append(self.type)

        CTkLabel(
            self.item_frame,
            text=item,
            font=("Segoe UI", 16),
        ).grid(row=1, column=0, padx=10, pady=10, sticky=W)

        auto = CTkRadioButton(
            self.item_frame,
            text='Automatic',
            variable=self.type,
            value=True,
            font=("Segoe UI", 16),
        )
        man = CTkRadioButton(
            self.item_frame,
            text='Manual',
            variable=self.type,
            value=False,
            font=("Segoe UI", 16),
        )

        auto.grid(row=1, column=1, padx=10, pady=10)
        man.grid(row=1, column=2, padx=10, pady=10)

        self.item_auto_buttons.append(auto)
        self.item_man_buttons.append(man)

    def update_page(self):
        '''Updates the UI when experiment data changes.'''
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
        '''Saves all entered group names and input method.'''
        group_names = [entry.get().strip() for entry in self.group_input if entry.get().strip()]
        self.experiment.group_names = group_names
        self.experiment.data_collect_type = 1 if self.button_vars[0].get() else 0
        self.next_page.update_page()
