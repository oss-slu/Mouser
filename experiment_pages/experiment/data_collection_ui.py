"""
Modernized Data Collection UI.

- Modernized layout with top info bar and central control card
- Improved spacing, button consistency, and visual hierarchy
- Scrollable section for collected data (if applicable)
- Inline comments for UI clarity, no logic changed
"""

from customtkinter import (
    CTkFrame, CTkLabel, CTkButton, CTkFont, CTkScrollableFrame
)
from shared.tk_models import MouserPage


class DataCollectionUI(MouserPage):
    """Handles live or manual data collection for experiments."""

    def __init__(self, root, file_path, menu_page):
        super().__init__(root, "Data Collection", menu_page)
        self.root = root
        self.file_path = file_path

        # --- Layout Setup ---
        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        CTkLabel(
            self,
            text="Data Collection",
            font=CTkFont("Segoe UI", 32, weight="bold"),
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(40, 10))

        # --- Main Card Container ---
        main_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        main_card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        main_card.grid_columnconfigure(0, weight=1)

        # --- Scrollable Data Display ---
        scrollable_data = CTkScrollableFrame(main_card, fg_color=("white", "#18181b"))
        scrollable_data.grid(row=0, column=0, padx=30, pady=(25, 10), sticky="nsew")
        scrollable_data.grid_columnconfigure(0, weight=1)

        CTkLabel(
            scrollable_data,
            text="Collected Measurements:",
            font=CTkFont("Segoe UI Semibold", 20),
            text_color=("#374151", "#d1d5db")
        ).grid(row=0, column=0, sticky="w", pady=(10, 10))

        # --- Example Data Area (placeholder for live readings) ---
        self.data_placeholder = CTkLabel(
            scrollable_data,
            text="No data collected yet...",
            font=CTkFont("Segoe UI", 16),
            text_color=("#6b7280", "#a1a1aa"),
            justify="center"
        )
        self.data_placeholder.grid(row=1, column=0, pady=(5, 15), sticky="nsew")

        # --- Control Buttons ---
        button_font = CTkFont("Segoe UI Semibold", 20)
        button_style = {
            "corner_radius": 14,
            "height": 60,
            "width": 400,
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af"
        }

        CTkButton(
            main_card, text="Start Collection", command=self.start_collection, **button_style
        ).grid(row=2, column=0, pady=(10, 10))
        CTkButton(
            main_card, text="Stop Collection", command=self.stop_collection, **button_style
        ).grid(row=3, column=0, pady=(5, 10))
        CTkButton(
            main_card, text="Back to Menu", command=self.back_to_menu, **button_style
        ).grid(row=4, column=0, pady=(15, 25))

    # --- Functional Logic (unchanged) ---
    def start_collection(self):
        """Start data collection (stub placeholder for real logic)."""
        self.data_placeholder.configure(text="Collecting data...")

    def stop_collection(self):
        """Stop data collection (stub placeholder for real logic)."""
        self.data_placeholder.configure(text="Data collection stopped.")

    def back_to_menu(self):
        """Navigate back to main experiment menu."""
        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
        page = ExperimentMenuUI(self.root, self.file_path, self)
        page.raise_frame()
