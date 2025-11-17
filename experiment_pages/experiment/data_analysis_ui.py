"""
Modernized Data Analysis UI.

- Clean, centered layout using a card-style container
- Consistent typography (Segoe UI)
- Blue accent buttons and adaptive dark/light mode
- Inline comments document visual changes; no logic modified
"""

from customtkinter import CTkButton, CTkFont, CTkFrame, CTkLabel
from shared.tk_models import MouserPage


class DataAnalysisUI(MouserPage):
    """Displays graphs, charts, and insights from collected experiment data."""

    def __init__(self, root, file_path, menu_page):
        super().__init__(root, "Data Analysis", menu_page)

        self.root = root
        self.file_path = file_path

        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

        CTkLabel(
            self,
            text="Data Analysis",
            font=CTkFont("Segoe UI", 32, weight="bold"),
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(40, 10))

        card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0, 1, 2, 3), weight=1)

        desc_font = CTkFont("Segoe UI", 18)
        CTkLabel(
            card,
            text="Analyze and visualize your collected experiment data below.",
            font=desc_font,
            text_color=("#4b5563", "#d4d4d8"),
            wraplength=700,
            justify="center"
        ).grid(row=0, column=0, pady=(20, 10))

        CTkLabel(
            card,
            text="[Charts and Data Visualizations Placeholder]",
            font=CTkFont("Segoe UI Italic", 16),
            text_color=("#6b7280", "#a1a1aa")
        ).grid(row=1, column=0, pady=(20, 10))

        button_font = CTkFont("Segoe UI Semibold", 20)
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
            card,
            text="Export Results",
            command=self.export_data,
            **button_style
        ).grid(row=2, column=0, pady=(10, 15))

        CTkButton(
            card,
            text="Back to menu",
            command=self.back_to_menu,
            **button_style
        ).grid(row=3, column=0, pady=(10, 25))

    def export_data(self):
        """Handles exporting analyzed data to file."""
        print("Exporting analyzed results...")

    def back_to_menu(self):
        """Return to experiment menu."""
        # IMPORT HERE → prevents circular dependency & fixes Pylint E0602
        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI

        page = ExperimentMenuUI(self.root, self.file_path, self)
        page.raise_frame()
