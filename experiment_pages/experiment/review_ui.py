"""
Modernized Review UI.

- Flat, card-based layout consistent with the new design language
- Unified color palette and button styling
- Responsive grid layout with clear text hierarchy
- Inline comments document each visual change
"""

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkFont
from shared.tk_models import MouserPage


class ReviewUI(MouserPage):
    """Displays a summary and allows final review of experiment configuration."""

    def __init__(self, root, file_path, menu_page):
        super().__init__(root, "Review Experiment", menu_page)
        self.root = root
        self.file_path = file_path

        # --- Page Configuration ---
        self.configure(fg_color=("white", "#1a1a1a"))
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title Section ---
        title_font = CTkFont(family="Segoe UI", size=30, weight="bold")
        CTkLabel(
            self,
            text="Review Experiment",
            font=title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(40, 10))

        # --- Main Card Container ---
        review_card = CTkFrame(
            self,
            fg_color=("white", "#2c2c2c"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        review_card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        review_card.grid_columnconfigure(0, weight=1)
        review_card.grid_rowconfigure((0, 1, 2), weight=1)

        # --- Description Label ---
        desc_font = CTkFont(family="Segoe UI", size=18)
        CTkLabel(
            review_card,
            text="Review all experiment settings and configurations before proceeding.",
            font=desc_font,
            text_color=("#4a4a4a", "#b0b0b0"),
            wraplength=700,
            justify="center"
        ).grid(row=0, column=0, pady=(20, 15))

        # --- Buttons Section ---
        button_font = CTkFont(family="Segoe UI Semibold", size=22)
        button_style = {
            "corner_radius": 14,
            "height": 70,
            "width": 420,
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af"
        }

        # --- Action Buttons ---
        CTkButton(
            review_card,
            text="Confirm and Save",
            command=self.confirm_experiment,
            **button_style
        ).grid(row=1, column=0, pady=10)

        CTkButton(
            review_card,
            text="Edit Configuration",
            command=self.edit_configuration,
            **button_style
        ).grid(row=2, column=0, pady=10)

        CTkButton(
            review_card,
            text="Back to Menu",
            command=self.back_to_menu,
            **button_style
        ).grid(row=3, column=0, pady=(20, 30))

    # --- Functionality (Unchanged) ---
    def confirm_experiment(self):
        """Save and finalize the experiment configuration."""
        from experiment_pages.create_experiment.summary_ui import SummaryUI
        page = SummaryUI(self.root, self.file_path, self)
        page.raise_frame()

    def edit_configuration(self):
        """Navigate to group configuration for editing."""
        from experiment_pages.experiment.group_config_ui import GroupConfigUI
        page = GroupConfigUI(self.root, self.file_path, self)
        page.raise_frame()

    def back_to_menu(self):
        """Return to the experiment menu."""
        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
        page = ExperimentMenuUI(self.root, self.file_path, self)
        page.raise_frame()
