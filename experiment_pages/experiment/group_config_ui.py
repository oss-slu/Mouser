"""
Modernized Group Configuration UI.

- Card-based layout consistent with the modern theme
- Improved spacing, alignment, and color consistency
- Inline comments for clarity (no functionality changed)
"""

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkFont
from shared.tk_models import MouserPage


class GroupConfigUI(MouserPage):
    """Handles group configuration within an experiment."""

    def __init__(self, root, file_path, menu_page):
        super().__init__(root, "Group Configuration", menu_page)
        self.root = root
        self.file_path = file_path
        self.menu_page = menu_page

        # --- Base Layout ---
        self.configure(fg_color=("white", "#1a1a1a"))
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        title_font = CTkFont(family="Segoe UI", size=32, weight="bold")
        CTkLabel(
            self,
            text="Group Configuration",
            font=title_font,
            text_color=("black", "white")
        ).grid(row=1, column=0, pady=(10, 10))

        # --- Card Container ---
        card = CTkFrame(
            self,
            fg_color=("white", "#2c2c2c"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        card.grid(row=2, column=0, padx=80, pady=(10, 30), sticky="nsew")
        card.grid_rowconfigure((0, 1, 2), weight=1)
        card.grid_columnconfigure(0, weight=1)

        # --- Info Label ---
        info_font = CTkFont(family="Segoe UI", size=18)
        CTkLabel(
            card,
            text="Select and configure experimental groups below:",
            font=info_font,
            text_color=("#4a4a4a", "#b0b0b0")
        ).grid(row=0, column=0, pady=(20, 10), sticky="n")

        # --- Button Styles ---
        button_font = CTkFont(family="Segoe UI Semibold", size=22)
        button_style = {
            "corner_radius": 12,
            "height": 50,
            "width": 350,
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af"
        }

        # --- Action Buttons ---
        CTkButton(
            card,
            text="Add New Group",
            command=self.add_group,
            **button_style
        ).grid(row=1, column=0, pady=(10, 10), padx=40, sticky="n")

        CTkButton(
            card,
            text="View Groups",
            command=self.view_groups,
            **button_style
        ).grid(row=2, column=0, pady=(10, 25), padx=40, sticky="n")
        # Ensure buttons are centered and compact
        card.grid_rowconfigure((1, 2), weight=0)
        card.grid_columnconfigure(0, weight=1)

        # Restyle inherited Back to Menu button for consistency
        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=50,
                width=180,
                font=("Segoe UI Semibold", 18),
                text_color="white",
                fg_color="#2563eb",
                hover_color="#1e40af"
            )
            self.menu_button.place_configure(relx=0.15, rely=0.18, anchor="w")


    # --- Functional Methods (unchanged) ---
    def add_group(self):
        """Open group creation window."""
        from experiment_pages.create_experiment.summary_ui import SummaryUI
        page = SummaryUI(self.root, self.file_path, self)
        page.raise_frame()

    def view_groups(self):
        """Display existing groups."""
        from experiment_pages.experiment.review_ui import ReviewUI
        page = ReviewUI(self.root, self.file_path, self)
        page.raise_frame()