"""
Modernized Experiment Menu UI.

- Acts as central hub for navigation between experiment pages
- Updated with responsive layout, consistent font hierarchy, and button palette
- Inline comments explain UI design; all logic preserved
"""

import sqlite3
import os
import platform
from tkinter import messagebox

from customtkinter import CTkFrame, CTkButton, CTkFont, CTkScrollableFrame
from shared.experiment import Experiment  # pylint: disable=import-error
from shared.tk_models import MouserPage  # pylint: disable=import-error
from databases.experiment_database import (  # pylint: disable=import-error
    ExperimentDatabase,
)


class ExperimentMenuUI(MouserPage):
    """Provides navigation options for the selected experiment."""

    @staticmethod
    def _menu_button_metrics():
        """Tune button size by OS to keep visual proportions consistent."""
        system = platform.system()
        if system == "Darwin":
            return {"font_size": 22, "height": 58, "width": 520}
        if system == "Windows":
            return {"font_size": 18, "height": 50, "width": 470}
        return {"font_size": 17, "height": 48, "width": 450}

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
        self.experiment_db = ExperimentDatabase(self.file_path)

        self.configure(fg_color=("white", "#18181b"))

        menu_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db",
        )
        menu_card.place(relx=0.5, rely=0.57, relwidth=0.70, relheight=0.72, anchor="center")

        menu_scroll = CTkScrollableFrame(
            menu_card,
            fg_color=("white", "#27272a"),
            corner_radius=16,
        )
        menu_scroll.pack(fill="both", expand=True, padx=16, pady=16)
        menu_scroll.grid_columnconfigure(0, weight=1)

        metrics = self._menu_button_metrics()
        button_font = CTkFont("Segoe UI Semibold", metrics["font_size"])
        button_style = {
            "corner_radius": 12,
            "height": metrics["height"],
            "width": metrics["width"],
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af",
        }

        self.group_button = CTkButton(
            menu_scroll,
            text="Group Configuration",
            command=self.open_group_config,
            **button_style,
        )
        self.group_button.grid(row=0, column=0, padx=14, pady=(8, 10), sticky="ew")

        self.cage_button = CTkButton(
            menu_scroll,
            text="Cage Configuration",
            command=self.open_cage_config,
            **button_style,
        )
        self.cage_button.grid(row=1, column=0, padx=14, pady=10, sticky="ew")

        self.collection_button = CTkButton(
            menu_scroll,
            text="Data Collection",
            command=self.open_data_collection,
            **button_style,
        )
        self.collection_button.grid(row=2, column=0, padx=14, pady=10, sticky="ew")

        self.analysis_button = CTkButton(
            menu_scroll,
            text="Data Analysis",
            command=self.open_data_analysis,
            **button_style,
        )
        self.analysis_button.grid(row=3, column=0, padx=14, pady=10, sticky="ew")

        self.rfid_button = CTkButton(
            menu_scroll,
            text="Map RFID",
            command=self.open_map_rfid,
            **button_style,
        )
        self.rfid_button.grid(row=4, column=0, padx=14, pady=10, sticky="ew")

        self.summary_button = CTkButton(
            menu_scroll,
            text="Summary View",
            command=self.open_summary,
            **button_style,
        )
        self.summary_button.grid(row=5, column=0, padx=14, pady=10, sticky="ew")

        self.investigators_button = CTkButton(
            menu_scroll,
            text="Investigators",
            command=self.open_investigators,
            **button_style,
        )
        self.investigators_button.grid(row=6, column=0, padx=14, pady=10, sticky="ew")

        delete_style = dict(button_style)
        delete_style["fg_color"] = "#dc2626"
        delete_style["hover_color"] = "#991b1b"
        self.delete_button = CTkButton(
            menu_scroll,
            text="Delete Experiment",
            command=self.delete_warning,
            **delete_style,
        )
        self.delete_button.grid(row=7, column=0, padx=14, pady=10, sticky="ew")

        self.disable_buttons_if_needed()

    def open_group_config(self):
        """Open Group Configuration Page for this experiment."""
        try:
            db = ExperimentDatabase(self.file_path)
        except sqlite3.DatabaseError:
            messagebox.showerror(
                "Open Experiment Error",
                "This experiment file could not be opened as a database.\n"
                "If it is password protected, please use the appropriate "
                "flow to unlock it.",
            )
            return

        exp = Experiment()
        exp.set_name(db.get_experiment_name() or "")
        exp.set_num_groups(str(db.get_number_groups()))
        exp.set_group_names(db.get_groups() or [])

        items = db.get_measurement_items()
        if items:
            if isinstance(items, (tuple, list)):
                exp.set_measurement_item(items[0])
            else:
                exp.set_measurement_item(items)

        exp.group_num_changed = False
        exp.measurement_items_changed = False
        exp.data_collect_type = db.get_measurement_type()

        def save_group_config(updated_experiment):
            group_names = updated_experiment.get_group_names()
            db.update_group_names(group_names)
            db.update_measurement_type(updated_experiment.get_measurement_type())

        from experiment_pages.experiment.group_config_ui import (  # pylint: disable=import-error,import-outside-toplevel
            GroupConfigUI,
        )

        page = GroupConfigUI(
            exp,
            self.root,
            self,
            self,
            edit_mode=True,
            save_callback=save_group_config,
        )
        page.raise_frame()

    def open_cage_config(self):
        """Open Cage Configuration Page."""
        from experiment_pages.experiment.cage_config_ui import (  # pylint: disable=import-error,import-outside-toplevel
            CageConfigUI,
        )

        page = CageConfigUI(self.file_path, self.root, self, self.file_path)
        page.raise_frame()

    def open_data_collection(self):
        """Open Data Collection Page."""
        from experiment_pages.experiment.data_collection_ui import (  # pylint: disable=import-error,import-outside-toplevel
            DataCollectionUI,
        )

        page = DataCollectionUI(self.root, self, self.file_path, self.file_path)
        page.raise_frame()

    def open_data_analysis(self):
        """Open Data Analysis Page."""
        from experiment_pages.experiment.data_analysis_ui import (  # pylint: disable=import-error,import-outside-toplevel
            DataAnalysisUI,
        )

        page = DataAnalysisUI(self.root, self, self.file_path)
        page.raise_frame()

    def open_map_rfid(self):
        """Open Map RFID Page."""
        from experiment_pages.experiment.map_rfid import (  # pylint: disable=import-error,import-outside-toplevel
            MapRFIDPage,
        )

        page = MapRFIDPage(self.file_path, self.root, self, self.file_path)
        page.raise_frame()

    def open_summary(self):
        """Open Experiment Summary Page."""
        from experiment_pages.experiment.review_ui import (  # pylint: disable=import-error,import-outside-toplevel
            ReviewUI,
        )

        page = ReviewUI(self.root, self, self.file_path)
        page.raise_frame()

    def open_investigators(self):
        """Open Investigators Page."""
        from experiment_pages.experiment.experiment_invest_ui import (  # pylint: disable=import-error,import-outside-toplevel
            InvestigatorsUI,
        )

        page = InvestigatorsUI(self.root, self, self.file_path)
        page.raise_frame()

    def all_rfid_mapped(self):
        """Return True if all expected animals have RFID mappings."""
        num_animals = self.experiment_db.get_total_number_animals()
        num_mapped = len(self.experiment_db.get_all_animal_ids())
        return num_animals == num_mapped

    def disable_buttons_if_needed(self):
        """Disable/enable actions based on RFID mapping requirement."""
        self.group_button.configure(state="normal")
        if self.experiment_db.experiment_uses_rfid() == 1:
            if not self.all_rfid_mapped():
                self.collection_button.configure(state="disabled")
                self.analysis_button.configure(state="disabled")
            else:
                self.collection_button.configure(state="normal")
                self.analysis_button.configure(state="normal")
            self.rfid_button.configure(state="normal")
        else:
            self.collection_button.configure(state="normal")
            self.analysis_button.configure(state="normal")
            self.rfid_button.configure(state="disabled")

    def disconnect_database(self):
        """Close experiment DB connection if possible."""
        try:
            self.experiment_db.close()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def delete_warning(self):
        """Ask for confirmation before deleting the experiment file."""
        if not self.file_path:
            messagebox.showerror("Delete Error", "No experiment file is currently loaded.")
            return
        confirmed = messagebox.askyesno(
            "Delete Experiment",
            "This will delete the experiment file and all associated data.\n\n"
            "Are you sure you want to continue?",
        )
        if confirmed:
            self.delete_experiment()

    def delete_experiment(self):
        """Delete the currently opened experiment file and navigate back."""
        self.disconnect_database()
        path = self.file_path
        try:
            if os.path.exists(path):
                os.remove(path)
            else:
                messagebox.showwarning("Delete Warning", f"File not found:\n{path}")
        except OSError as error:
            messagebox.showerror("Delete Error", f"Failed to delete experiment:\n{error}")
            return

        if self.menu_page is not None and hasattr(self.menu_page, "raise_frame"):
            self.menu_page.raise_frame()
        else:
            self.back_to_welcome()

    def raise_frame(self):
        """Refresh button states whenever menu is raised."""
        self.disable_buttons_if_needed()
        super().raise_frame()

    def back_to_welcome(self):
        """Return to the main welcome screen."""
        from ui.welcome_screen import (  # pylint: disable=import-outside-toplevel
            setup_welcome_screen,
        )

        setup_welcome_screen(self.root, self)
