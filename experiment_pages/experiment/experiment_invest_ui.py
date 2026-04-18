"""Experiment Investigators editor UI."""

from customtkinter import (
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkScrollableFrame,
    CTkFont,
)
from tkinter import messagebox
from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage
from shared.tk_models import get_ui_metrics


class InvestigatorsUI(MouserPage):
    """Page for viewing and editing experiment investigators."""

    def __init__(self, parent, prev_page=None, file_path: str = ""):
        super().__init__(parent, "Investigators", prev_page)
        self.file_path = file_path
        self.db = ExperimentDatabase(file_path)
        self.investigators = self.db.get_investigators()

        ui = get_ui_metrics()
        is_dark = self._get_is_dark()

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
            "input_bg": ("#ffffff", "#0b1220"),
            "input_border": ("#cbd5e1", "#334155"),
            "accent": "#2563eb",
            "accent_hover": "#1e40af",
            "danger": "#dc2626",
            "danger_hover": "#991b1b",
            "neutral": "#64748b",
            "neutral_hover": "#475569",
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

        title_font = CTkFont(family="Segoe UI Semibold", size=26)
        subtitle_font = CTkFont(family="Segoe UI", size=14)
        section_title_font = CTkFont(family="Segoe UI Semibold", size=14)
        list_item_font = CTkFont(family="Segoe UI", size=14)

        header = CTkFrame(self, fg_color="transparent")
        header.place(relx=0.0, rely=0.0, x=64, y=72, anchor="nw")

        title_row = CTkFrame(header, fg_color="transparent")
        title_row.pack(anchor="w")
        CTkLabel(
            title_row,
            text="\U0001f465",
            font=title_font,
            text_color=self._palette["text"],
            width=0,
        ).pack(side="left", padx=(0, 8))
        CTkLabel(
            title_row,
            text="Investigators",
            font=title_font,
            text_color=self._palette["text"],
        ).pack(side="left")
        CTkLabel(
            header,
            text="Add, remove, and save investigators for this experiment.",
            font=subtitle_font,
            text_color=self._palette["muted_text"],
        ).pack(anchor="w", pady=(2, 0))

        card = CTkFrame(
            self,
            fg_color=self._palette["card_bg"],
            corner_radius=18,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        card.place(relx=0.5, rely=0.0, y=150, anchor="n", relwidth=0.90, relheight=0.74)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        input_row = CTkFrame(card, fg_color="transparent")
        input_row.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))
        input_row.grid_columnconfigure(0, weight=1)

        self.input_entry = CTkEntry(
            input_row,
            placeholder_text="Enter investigator name",
            fg_color=self._palette["input_bg"],
            border_color=self._palette["input_border"],
            text_color=("black", "white"),
            placeholder_text_color=self._palette["muted_text"],
            height=max(38, ui["nav_height"] - 8),
            font=list_item_font,
        )
        self.input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.input_entry.bind("<Return>", lambda _event: self.add_investigator())

        CTkButton(
            input_row,
            text="+ Add",
            width=110,
            height=max(38, ui["nav_height"] - 8),
            font=CTkFont("Segoe UI Semibold", 14),
            command=self.add_investigator,
            fg_color=self._palette["accent"],
            hover_color=self._palette["accent_hover"],
            text_color="white",
        ).grid(row=0, column=1)

        CTkLabel(
            card,
            text="Current investigators",
            font=section_title_font,
            text_color=self._palette["muted_text"],
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 8))

        self.list_frame = CTkScrollableFrame(
            card,
            fg_color=_pick(("#f8fafc", "#0b1220")),
            corner_radius=14,
        )
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.list_frame.grid_columnconfigure(0, weight=1)

        actions = CTkFrame(card, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="e", padx=18, pady=(0, 18))

        CTkButton(
            actions,
            text="\U0001f4be Save",
            width=140,
            height=42,
            font=CTkFont("Segoe UI Semibold", 14),
            command=self.save_investigators,
            fg_color=self._palette["accent"],
            hover_color=self._palette["accent_hover"],
            text_color="white",
        ).grid(row=0, column=0)

        # Bottom "Back" removed (top-left menu button remains the navigation control).

        self._refresh_list()

    def _get_is_dark(self) -> bool:
        try:
            from customtkinter import get_appearance_mode

            return get_appearance_mode().lower() == "dark"
        except Exception:
            return False

    def _refresh_list(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.investigators:
            CTkLabel(
                self.list_frame,
                text="No investigators added yet.",
                text_color=self._palette["muted_text"],
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        for idx, name in enumerate(self.investigators):
            row_bg = ("#ffffff", "#101827") if idx % 2 == 0 else ("#f8fafc", "#0f172a")
            row = CTkFrame(
                self.list_frame,
                fg_color=row_bg,
                corner_radius=12,
                border_width=1,
                border_color=self._palette["card_border"],
            )
            row.grid(row=idx, column=0, sticky="ew", padx=10, pady=6)
            row.grid_columnconfigure(0, weight=1)

            CTkLabel(row, text=name, text_color=self._palette["text"]).grid(
                row=0, column=0, sticky="w", padx=12, pady=10
            )
            CTkButton(
                row,
                text="\U0001f5d1 Remove",
                width=90,
                command=lambda person=name: self.remove_investigator(person),
                fg_color=self._palette["danger"],
                hover_color=self._palette["danger_hover"],
                text_color="white",
            ).grid(row=0, column=1, padx=(8, 10), pady=8)

    def add_investigator(self):
        name = self.input_entry.get().strip()
        if not name:
            return
        if name in self.investigators:
            self.input_entry.delete(0, "end")
            return
        self.investigators.append(name)
        self.input_entry.delete(0, "end")
        self._refresh_list()

    def remove_investigator(self, name):
        if name in self.investigators:
            self.investigators.remove(name)
            self._refresh_list()

    def save_investigators(self):
        self.db.update_investigators(self.investigators)
        messagebox.showinfo("Saved", "Investigators updated successfully.")

    def go_back(self):
        if hasattr(self, "menu_button") and self.menu_button:
            prev = getattr(self.menu_button, "previous_page", None)
            if prev is not None and hasattr(prev, "raise_frame"):
                prev.raise_frame()
