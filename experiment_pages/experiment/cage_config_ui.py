"""
Modernized Cage Configuration UI.

- Consistent with app-wide design (blue-accent buttons, card layout)
- Improved spacing, font hierarchy, and responsive layout
- Inline comments explaining UI changes; no logic altered
"""

from tkinter import messagebox
from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkFont, CTkEntry
from shared.tk_models import MouserPage  # pylint: disable=import-error
from databases.experiment_database import ExperimentDatabase  # pylint: disable=import-error
import sqlite3


class CageConfigUI(MouserPage):
    """Allows configuration of cage groups and animal assignments."""

    def __init__(self, root, file_path, menu_page):
        super().__init__(root, "Cage Configuration", menu_page)

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

        self.root = root
        self.file_path = file_path

        self.configure(fg_color=("white", "#18181b"))
        self.grid_columnconfigure(0, weight=1)

        title_font = CTkFont(family="Segoe UI", size=30, weight="bold")
        CTkLabel(
            self,
            text="Cage Configuration",
            font=title_font,
            text_color=("black", "white"),
        ).grid(row=0, column=0, pady=(40, 10))

        cage_card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db",
        )
        cage_card.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.9)
        cage_card.grid_columnconfigure(0, weight=1)

        CTkLabel(
            cage_card,
            text="Enter cage configuration details below:",
            font=CTkFont("Segoe UI", 18),
            text_color=("#4b5563", "#d4d4d8"),
        ).grid(row=0, column=0, pady=(20, 10))

        form_font = CTkFont("Segoe UI", 18)
        label_cfg = {
            "font": form_font,
            "text_color": ("#1f2937", "#e5e7eb"),
            "anchor": "w",
        }

        self.group_name = CTkEntry(cage_card, width=300)
        self.num_animals = CTkEntry(cage_card, width=300)

        group_label = CTkLabel(cage_card, text="Group Name:", **label_cfg)
        group_label.grid(row=1, column=0, sticky="w", padx=40, pady=5)
        self.group_name.grid(row=2, column=0, padx=40, pady=5, sticky="w")

        CTkLabel(cage_card, text="Number of Animals per Cage:", **label_cfg).grid(
            row=3,
            column=0,
            sticky="w",
            padx=40,
            pady=5,
        )
        self.num_animals.grid(row=4, column=0, padx=40, pady=5, sticky="w")

        button_font = CTkFont("Segoe UI Semibold", 20)
        button_style = {
            "corner_radius": 12,
            "height": 48,
            "width": 220,
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af",
        }

        CTkButton(
            cage_card,
            text="Add Cage",
            command=self.add_cage,
            **button_style,
        ).grid(row=5, column=0, pady=(15, 10))
        CTkButton(
            cage_card,
            text="View Summary",
            command=self.view_summary,
            **button_style,
        ).grid(row=6, column=0, pady=(5, 25))

    def add_cage(self):
        """Update cage capacity for a group and randomize cage assignments."""
        name = self.group_name.get().strip()
        num = self.num_animals.get().strip()

        if not name or not num:
            messagebox.showwarning(
                "Missing Data",
                "Please enter both a group name and the number of animals per cage.",
            )
            return

        try:
            capacity = int(num)
            if capacity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Value",
                "Number of animals per cage must be a positive whole number.",
            )
            return

        try:
            db = ExperimentDatabase(self.file_path)

            db._c.execute(  
                "UPDATE groups SET cage_capacity = ? WHERE name = ?",
                (capacity, name),
            )
            db._conn.commit()  

            db.randomize_cages()

        except sqlite3.Error as exc:
            messagebox.showerror(
                "Database Error",
                f"Unable to update cage configuration:\n{exc}",
            )
            return

        messagebox.showinfo(
            "Cage Configuration Updated",
            f"Cage capacity for group '{name}' has been set to {capacity}.\n"
            "Animals have been re-assigned to cages using this capacity.",
        )

    def view_summary(self):
        """Open experiment summary page."""
        from experiment_pages.experiment.review_ui import (  
            ReviewUI,
        )

        page = ReviewUI(self.root, self, self.file_path)
        page.raise_frame()

    def back_to_menu(self):
        """Return to experiment menu."""
        from experiment_pages.experiment.experiment_menu_ui import (  
            ExperimentMenuUI,
        )

        page = ExperimentMenuUI(self.root, self.file_path, self)
        page.raise_frame()
