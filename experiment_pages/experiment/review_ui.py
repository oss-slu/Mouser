"""
Modernized Review Experiment Summary UI.

- Clean, scrollable, card-based layout for readability
- Responsive font sizes and consistent color palette
- Uses light/dark adaptive backgrounds
- Each section separated visually for better hierarchy
- Inline comments document every UI enhancement (no logic changes)
"""

from customtkinter import CTkFont, CTkFrame, CTkLabel, CTkScrollableFrame

from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage


class ReviewUI(MouserPage):
    """Displays a detailed experiment summary pulled from the database."""

    def __init__(self, parent, prev_page, database_name: str = ""):
        super().__init__(parent, "Experiment Summary", prev_page)

        # Initialize database connection
        self.database = ExperimentDatabase(database_name)

        # --- Base Layout ---
        self.configure(fg_color=("white", "#18181b"))  # adaptive theme
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Scrollable Container (replaces CTkFrame) ---
        scrollable = CTkScrollableFrame(
            self,
            fg_color=("white", "#18181b"),
            corner_radius=15,
            border_width=0
        )
        scrollable.grid(row=0, column=0, sticky="nsew", padx=60, pady=40)
        scrollable.grid_columnconfigure(0, weight=1)

        # --- Title Section ---
        title_font = CTkFont(family="Segoe UI", size=32, weight="bold")
        CTkLabel(
            scrollable,
            text="Experiment Summary",
            font=title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(10, 25))

        # --- Content Card ---
        content_card = CTkFrame(
            scrollable,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        content_card.grid(row=1, column=0, sticky="nsew", padx=40, pady=(10, 30))
        content_card.grid_columnconfigure(1, weight=1)

        # Species
        # === Species (placed inside content_card) ===
        species_result = self.database._c.execute("SELECT species FROM experiment").fetchone()
        species = species_result[0] if species_result else "Unknown"

        CTkLabel(
            content_card,
            text="Species:",
            font=CTkFont(size=18, weight="bold"),
            text_color=("#374151", "#d4d4d8"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(25, 20), pady=(8, 6))

        CTkLabel(
            content_card,
            text=species,
            font=CTkFont(size=18),
            text_color=("#111827", "#e5e7eb"),
            justify="left",
            anchor="w",
            wraplength=700
        ).grid(row=0, column=1, sticky="w", padx=(10, 25), pady=(8, 6))


        # === Populate Experiment Data ===
        # Safely fetch species
        species_row = self.database._c.execute("SELECT species FROM experiment").fetchone()
        species_value = species_row[0] if species_row else "Unknown"

        # Safely fetch investigators
        investigators_row = self.database._c.execute("SELECT investigators FROM experiment").fetchone()
        investigators_value = (
            "\n".join(investigators_row[0].split(",")) if investigators_row else "N/A"
        )

        data = [
            ("Experiment Name", self.database.get_experiment_name() or "Unknown"),
            ("Investigators", investigators_value),
            ("Species", species_value),
            ("Measurement Item", self.database.get_measurement_name() or "None"),
            ("Number of Animals", str(self.database.get_total_number_animals())),
            ("Animals per Group", str(self.database.get_cage_capacity(1))),
            ("Group Names", "\n".join(self.database.get_groups())),
            ("Uses RFID", "Yes" if self.database.experiment_uses_rfid() else "No"),
            ("Measurement Type", "Automatic" if self.database.get_measurement_type() == 1 else "Manual"),
        ]


        # --- Generate Labels Dynamically ---
        label_font = CTkFont(size=18, weight="bold")
        value_font = CTkFont(size=18)
        for i, (key, value) in enumerate(data, start=0):
            CTkLabel(
                content_card,
                text=f"{key}:",
                font=label_font,
                text_color=("#374151", "#d4d4d8"),
                anchor="w"
            ).grid(row=i, column=0, sticky="w", padx=(25, 20), pady=(8, 6))

            CTkLabel(
                content_card,
                text=value,
                font=value_font,
                text_color=("#111827", "#e5e7eb"),
                justify="left",
                anchor="w",
                wraplength=700
            ).grid(row=i, column=1, sticky="w", padx=(10, 25), pady=(8, 6))

        # --- Subtle Divider Frame for spacing ---
        CTkFrame(scrollable, fg_color="transparent", height=30).grid(row=2, column=0)

        # --- Footer Note ---
        CTkLabel(
            scrollable,
            text="✅ Review complete — verify details before saving your configuration.",
            font=CTkFont(family="Segoe UI Italic", size=16),
            text_color=("#4b5563", "#9ca3af")
        ).grid(row=3, column=0, pady=(10, 30))
