"""
Modernized Experiment Menu UI.

- Acts as central hub for navigation between experiment pages
- Updated with responsive layout, consistent font hierarchy, and button palette
- Inline comments explain UI design; all logic preserved
"""
from shared.experiment import Experiment
from databases.experiment_database import ExperimentDatabase
import sqlite3
from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkFont
from shared.tk_models import MouserPage


class ExperimentMenuUI(MouserPage):
    """Provides navigation options for the selected experiment."""

    def __init__(self, root, file_path, menu_page=None):
        super().__init__(root, "Experiment Menu", menu_page)
        if hasattr(self, "menu_button") and self.menu_button:
            def safe_nav():
                prev = getattr(self.menu_button, "previous_page", None)
                if prev is not None and hasattr(prev, "raise_frame"):
                    prev.raise_frame()
                else:
                    self.back_to_welcome()

            self.menu_button.configure(
                text="Back to Menu",
                corner_radius=12,
                height=50,
                width=180,
                font=CTkFont("Segoe UI Semibold", 18),
                text_color="white",
                fg_color="#2563eb",
                hover_color="#1e40af",
                command=safe_nav,
            )
            self.menu_button.place_configure(relx=0.05, rely=0.13, anchor="w")
        self.root = root
        self.file_path = file_path
        self.menu_page = menu_page

        # --- Page Styling ---
        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Section ---
        CTkLabel(
            self,
            text="Experiment Dashboard",
            font=CTkFont("Segoe UI", 34, weight="bold"),
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(40, 15))

        # --- Info Subtitle ---
        CTkLabel(
            self,
            text="Select an option below to manage your experiment:",
            font=CTkFont("Segoe UI", 18),
            text_color=("#4b5563", "#a1a1aa")
        ).grid(row=1, column=0, pady=(0, 15))

        # --- Card Container for Buttons ---
        menu_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        menu_card.grid(row=2, column=0, padx=80, pady=30, sticky="nsew")
        menu_card.grid_columnconfigure(0, weight=1)

        # --- Buttons Section ---
        button_font = CTkFont("Segoe UI Semibold", 22)
        button_style = {
            "corner_radius": 12,
            "height": 50,
            "width": 350,
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af"
        }


        CTkButton(
            menu_card, text="Group Configuration", command=self.open_group_config, **button_style
        ).grid(row=0, column=0, pady=(15, 10))

        CTkButton(
            menu_card, text="Cage Configuration", command=self.open_cage_config, **button_style
        ).grid(row=1, column=0, pady=(15, 10))

        CTkButton(
            menu_card, text="Data Collection", command=self.open_data_collection, **button_style
        ).grid(row=2, column=0, pady=(15, 10))

        CTkButton(
            menu_card, text="Data Analysis", command=self.open_data_analysis, **button_style
        ).grid(row=3, column=0, pady=(15, 10))

        CTkButton(
            menu_card, text="Back to Welcome Screen", command=self.back_to_welcome, **button_style
        ).grid(row=4, column=0, pady=(25, 20))

    def open_group_config(self):
        """Open Group Configuration Page for this experiment."""
        try:
            db = ExperimentDatabase(self.file_path)
        except sqlite3.DatabaseError:
            messagebox.showerror(
                "Open Experiment Error",
                "This experiment file could not be opened as a database.\n"
                "If it is password protected, please use the appropriate flow to unlock it."
            )
            return

        # Build a minimal Experiment object for the GroupConfigUI
        exp = Experiment()
        exp.set_name(db.get_experiment_name() or "")
        exp.set_num_groups(str(db.get_number_groups()))
        exp.set_group_names(db.get_groups() or [])

        items = db.get_measurement_items()
        if items:
            exp.set_measurement_item(items[0] if isinstance(items, (tuple, list)) else items)

        # Reasonable defaults for flags
        exp.group_num_changed = False
        exp.measurement_items_changed = False
        exp.data_collect_type = 0  # manual by default

        from experiment_pages.experiment.group_config_ui import GroupConfigUI
        page = GroupConfigUI(exp, self.root, self, self.menu_page)
        page.raise_frame()


    def open_cage_config(self):
        """Open Cage Configuration Page."""
        from experiment_pages.experiment.cage_config_ui import CageConfigUI
        page = CageConfigUI(self.root, self.file_path, self)
        page.raise_frame()

    def open_data_collection(self):
        """Open Data Collection Page."""
        from experiment_pages.experiment.data_collection_ui import DataCollectionUI
        page = DataCollectionUI(self.root, self.file_path, self)
        page.raise_frame()

    def open_data_analysis(self):
        """Open Data Analysis Page."""
        from experiment_pages.experiment.data_analysis_ui import DataAnalysisUI
        page = DataAnalysisUI(self.root, self.file_path, self)
        page.raise_frame()

    def back_to_welcome(self):
        """Return to the main welcome screen."""
        from ui.welcome_screen import setup_welcome_screen
        setup_welcome_screen(self.root, self)
