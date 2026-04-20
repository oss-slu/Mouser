"""
Review Experiment Summary UI (UI refresh only).

- Keeps the same data/DB calls and behavior
- Updates layout to match the newer Mouser pages (header + card styling)
- Light/dark adaptive colors via CustomTkinter appearance mode
"""

from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage, get_ui_metrics
from customtkinter import (
    CTkScrollableFrame,
    CTkLabel,
    CTkFont,
    CTkFrame,
    get_appearance_mode,
)


class ReviewUI(MouserPage):  # pylint: disable=too-few-public-methods
    """Displays a detailed experiment summary pulled from the database."""

    def __init__(self, parent, prev_page, database_name: str = ""):
        super().__init__(parent, "Experiment Summary", prev_page)

        ui = get_ui_metrics()
        is_dark = get_appearance_mode().lower() == "dark"

        def _pick(color_value):
            if isinstance(color_value, (tuple, list)) and len(color_value) >= 2:
                return color_value[1] if is_dark else color_value[0]
            return color_value

        self._palette = {
            "page_bg": ("#eef2ff", "#0b1220"),
            "card_bg": ("#ffffff", "#101827"),
            "card_border": ("#c7d2fe", "#22304a"),
            "text": ("#0f172a", "#e5e7eb"),
            "muted_text": ("#334155", "#cbd5e1"),
            "row_bg": ("#f8fafc", "#0f172a"),
        }
        self.configure(fg_color=self._palette["page_bg"])

        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=40,
                width=54,
                text="\u2B05",
                font=("Segoe UI Semibold", 20),
                text_color="white",
                fg_color="#f59e0b",
                hover_color="#d97706",
            )
            self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=8, anchor="nw")

        self.database = ExperimentDatabase(database_name)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        title_font = CTkFont(family="Segoe UI Semibold", size=26)
        subtitle_font = CTkFont(family="Segoe UI", size=14)
        label_font = CTkFont(family="Segoe UI Semibold", size=max(12, ui["label_font_size"]))
        value_font = CTkFont(family="Segoe UI", size=max(12, ui["label_font_size"]))

        header = CTkFrame(self, fg_color="transparent")
        header.place(relx=0.0, rely=0.0, x=64, y=72, anchor="nw")

        title_row = CTkFrame(header, fg_color="transparent")
        title_row.pack(anchor="w")
        CTkLabel(
            title_row,
            text="\U0001f4cb",
            font=title_font,
            text_color=self._palette["text"],
            width=0,
        ).pack(side="left", padx=(0, 8))
        CTkLabel(
            title_row,
            text="Experiment Summary",
            font=title_font,
            text_color=self._palette["text"],
        ).pack(side="left")
        CTkLabel(
            header,
            text="Review details before saving your configuration.",
            font=subtitle_font,
            text_color=self._palette["muted_text"],
        ).pack(anchor="w", pady=(2, 0))

        scrollable = CTkScrollableFrame(
            self,
            fg_color=self._palette["card_bg"],
            corner_radius=18,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        scrollable.place(relx=0.5, rely=0.0, y=150, anchor="n", relwidth=0.60, relheight=0.70)
        scrollable.grid_columnconfigure(0, weight=1)

        investigators_row = self.database._c.execute(  # pylint: disable=protected-access
            "SELECT investigators FROM experiment"
        ).fetchone()
        if investigators_row:
            investigators_value = "\n".join(investigators_row[0].split(","))
        else:
            investigators_value = "N/A"

        groups = self.database.get_groups()
        data = [
            ("Experiment Name", self.database.get_experiment_name()),
            ("Investigators", investigators_value),
            (
                "Species",
                self.database._c.execute(  # pylint: disable=protected-access
                    "SELECT species FROM experiment"
                ).fetchone()[0],
            ),
            ("Measurement Item", self.database.get_measurement_name()),
            ("Number of Animals", str(self.database.get_total_number_animals())),
            ("Animals per Group", str(self.database.get_cage_capacity(1))),
            ("Group Names", groups),
            ("Uses RFID", "Yes" if self.database.experiment_uses_rfid() else "No"),
            (
                "Measurement Type",
                "Automatic" if self.database.get_measurement_type() == 1 else "Manual",
            ),
        ]

        # Wider label column so values start closer to the visual center (matches reference layout).
        label_col_width = 300
        value_wrap = 680

        for idx, (key, value) in enumerate(data):
            row_bg = self._palette["row_bg"] if idx % 2 == 1 else self._palette["card_bg"]
            row = CTkFrame(scrollable, fg_color=row_bg, corner_radius=12)
            row.grid(row=idx, column=0, sticky="ew", padx=18, pady=(14 if idx == 0 else 6, 0))
            row.grid_columnconfigure(0, minsize=label_col_width)
            row.grid_columnconfigure(1, weight=1)

            CTkLabel(
                row,
                text=key,
                font=label_font,
                text_color=self._palette["muted_text"],
                anchor="w",
            ).grid(row=0, column=0, sticky="nw", padx=(14, 10), pady=12)

            if key in {"Investigators", "Group Names", "Measurement Item"}:
                if key == "Investigators":
                    raw_items = []
                    if isinstance(value, str):
                        raw_items = [item.strip() for item in value.replace(",", "\n").splitlines()]
                    items = [item for item in raw_items if item and item.upper() != "N/A"]
                elif key == "Measurement Item":
                    raw_items = []
                    if isinstance(value, str):
                        raw_items = [item.strip() for item in value.replace(",", "\n").splitlines()]
                    items = [item for item in raw_items if item and item.upper() != "N/A"]
                else:
                    if isinstance(value, (list, tuple)):
                        items = [str(item).strip() for item in value if str(item).strip()]
                    else:
                        items = []

                value_frame = CTkFrame(row, fg_color="transparent")
                value_frame.grid(row=0, column=1, sticky="ew", padx=(24, 14), pady=12)

                if not items:
                    CTkLabel(
                        value_frame,
                        text="N/A",
                        font=value_font,
                        text_color=self._palette["text"],
                        justify="left",
                        anchor="w",
                        wraplength=value_wrap,
                    ).grid(row=0, column=0, sticky="w")
                else:
                    chip_bg = ("#e0f2fe", "#0b1b35")
                    chip_border = self._palette["card_border"]
                    chip_text = self._palette["text"]
                    chip_font = CTkFont(family="Segoe UI", size=max(12, ui["label_font_size"] - 1))

                    max_len = max((len(text) for text in items), default=0)
                    if max_len <= 18:
                        columns = 4
                        chip_wrap = 180
                    elif max_len <= 28:
                        columns = 3
                        chip_wrap = 230
                    else:
                        columns = 2
                        chip_wrap = 320

                    value_frame.grid_columnconfigure(tuple(range(columns)), weight=1, uniform=f"{key}_chips")

                    for item_index, item_text in enumerate(items, start=1):
                        row_i = (item_index - 1) // columns
                        col_i = (item_index - 1) % columns
                        prefix = f"{item_index}. " if key == "Group Names" else ""

                        chip = CTkFrame(
                            value_frame,
                            fg_color=_pick(chip_bg),
                            corner_radius=12,
                            border_width=1,
                            border_color=_pick(chip_border),
                        )
                        chip.grid(row=row_i, column=col_i, sticky="ew", padx=4, pady=4)

                        CTkLabel(
                            chip,
                            text=f"{prefix}{item_text}",
                            font=chip_font,
                            text_color=_pick(chip_text),
                            justify="left",
                            anchor="w",
                            wraplength=chip_wrap,
                        ).pack(anchor="w", padx=8, pady=6)
            else:
                display_value = value or "N/A"
                CTkLabel(
                    row,
                    text=str(display_value),
                    font=value_font,
                    text_color=self._palette["text"],
                    justify="left",
                    anchor="w",
                    wraplength=value_wrap,
                ).grid(row=0, column=1, sticky="w", padx=(24, 14), pady=12)

            CTkFrame(row, height=1, fg_color=_pick(self._palette["card_border"])).grid(
                row=1, column=0, columnspan=2, sticky="ew", padx=10
            )

