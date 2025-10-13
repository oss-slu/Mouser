"""
Modernized Experiment Menu UI.

- Flat, card-based layout for improved clarity and visual hierarchy
- Consistent typography and color palette with dark/light theme support
- Inline comments document design updates without altering functionality
"""

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkFont
from shared.tk_models import MouserPage, raise_frame


class ExperimentMenuUI(MouserPage):
    """Main experiment navigation menu — redesigned for clarity and visual polish."""

    def __init__(self, root, file_path, menu_page, original_file=None):
        super().__init__(root, "Experiment Menu", menu_page)
        self.root = root
        self.file_path = file_path
        self.original_file = original_file

        # --- Layout Setup ---
        self.configure(fg_color=("white", "#1a1a1a"))
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Label ---
        title_font = CTkFont(family="Segoe UI", size=34, weight="bold")
        title = CTkLabel(
            self,
            text="Experiment Navigation",
            font=title_font,
            text_color=("black", "white"),
            anchor="center"
        )
        title.grid(row=0, column=0, pady=(40, 20))

        # --- Button Container ---
        button_card = CTkFrame(
            self,
            fg_color=("white", "#2c2c2c"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        button_card.grid(row=1, column=0, padx=80, pady=30, sticky="nsew")
        button_card.grid_columnconfigure(0, weight=1)
        button_card.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # --- Shared button style ---
        button_style = {
            "corner_radius": 16,
            "height": 80,
            "width": 600,
            "font": ("Segoe UI Semibold", 24),
            "text_color": "white",
            "fg_color": "#2563eb",  # Blue primary
            "hover_color": "#1e40af",  # Darker blue on hover
        }

        # --- Buttons for Experiment Sections ---
        CTkButton(
            button_card,
            text="Group Configuration",
            command=self.open_group_config,
            **button_style
        ).grid(row=0, column=0, pady=10, padx=40, sticky="nsew")

        CTkButton(
            button_card,
            text="Cage Configuration",
            command=self.open_cage_config,
            **button_style
        ).grid(row=1, column=0, pady=10, padx=40, sticky="nsew")

        CTkButton(
            button_card,
            text="RFID Mapping",
            command=self.open_rfid_mapping,
            **button_style
        ).grid(row=2, column=0, pady=10, padx=40, sticky="nsew")

        CTkButton(
            button_card,
            text="Data Collection",
            command=self.open_data_collection,
            **button_style
        ).grid(row=3, column=0, pady=10, padx=40, sticky="nsew")

        CTkButton(
            button_card,
            text="Review Experiment",
            command=self.open_review,
            **button_style
        ).grid(row=4, column=0, pady=10, padx=40, sticky="nsew")

    # --- Navigation Logic (imports moved inside to prevent circular dependency) ---
    def open_group_config(self):
        from experiment_pages.experiment.group_config_ui import GroupConfigUI
        page = GroupConfigUI(self.root, self.file_path, self)
        page.raise_frame()

    def open_cage_config(self):
        from experiment_pages.experiment.cage_config_ui import CageConfigUI
        page = CageConfigUI(self.root, self.file_path, self)
        page.raise_frame()

    def open_rfid_mapping(self):
        import experiment_pages.experiment.map_rfid as map_rfid
        # Automatically find RFID UI class
        for attr_name in dir(map_rfid):
            attr = getattr(map_rfid, attr_name)
            if isinstance(attr, type) and attr.__name__.lower().startswith("maprfid"):
                page = attr(self.root, self.file_path, self)
                page.raise_frame()
                return
        print("⚠️ No valid RFID mapping class found in map_rfid.py")

    def open_data_collection(self):
        from experiment_pages.experiment.data_collection_ui import DataCollectionUI
        page = DataCollectionUI(self.root, self.file_path, self)
        page.raise_frame()

    def open_review(self):
        from experiment_pages.experiment.review_ui import ReviewUI
        page = ReviewUI(self.root, self.file_path, self)
        page.raise_frame()
