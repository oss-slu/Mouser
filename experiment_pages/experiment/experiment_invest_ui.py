"""Experiment Investigators editor UI."""

from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    CTkScrollableFrame,
    CTkTextbox,
    CTkFont,
)
from tkinter import messagebox
from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage


class InvestigatorsUI(MouserPage):
    """Page for viewing and editing experiment investigators."""

    def __init__(self, parent, prev_page=None, file_path: str = ""):
        super().__init__(parent, "Investigators", prev_page)
        self.file_path = file_path
        self.db = ExperimentDatabase(file_path)
        self.investigators = []

        self.configure(fg_color=("white", "#18181b"))
        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure(0, weight=1)

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

        CTkLabel(
            self,
            text="Investigators",
            font=CTkFont("Segoe UI", 32, weight="bold"),
            text_color=("black", "white"),
        ).grid(row=0, column=0, pady=(40, 10))

        card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db",
        )
        card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        card.grid_rowconfigure(2, weight=1)
        card.grid_columnconfigure(0, weight=1)

        input_row = CTkFrame(card, fg_color="transparent")
        input_row.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="ew")
        input_row.grid_columnconfigure(0, weight=1)

        self.input_entry = CTkEntry(input_row, placeholder_text="Enter investigator name")
        self.input_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_entry.bind("<Return>", lambda _event: self.add_investigator())

        CTkButton(
            input_row,
            text="Add",
            width=100,
            command=self.add_investigator,
            fg_color="#2563eb",
            hover_color="#1e40af",
        ).grid(row=0, column=1)

        CTkLabel(
            card,
            text="Current Investigators",
            font=CTkFont("Segoe UI", 16, weight="bold"),
            text_color=("#111827", "#e5e7eb"),
        ).grid(row=1, column=0, padx=25, pady=(0, 4), sticky="w")

        self.investigator_textbox = CTkTextbox(card, height=100, wrap="word")
        self.investigator_textbox.grid(row=2, column=0, padx=25, pady=(0, 10), sticky="nsew")
        self.investigator_textbox.configure(state="disabled")

        self.list_frame = CTkScrollableFrame(card, fg_color=("white", "#1f2937"), height=170)
        self.list_frame.grid(row=3, column=0, padx=25, pady=10, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        actions = CTkFrame(card, fg_color="transparent")
        actions.grid(row=4, column=0, padx=25, pady=(10, 20), sticky="e")

        CTkButton(
            actions,
            text="Save",
            width=120,
            command=self.save_investigators,
            fg_color="#2563eb",
            hover_color="#1e40af",
        ).grid(row=0, column=0, padx=(0, 10))

        CTkButton(
            actions,
            text="Back",
            width=120,
            command=self.go_back,
            fg_color="#4b5563",
            hover_color="#374151",
        ).grid(row=0, column=1)

        self._load_investigators()

    def _load_investigators(self):
        self.investigators = self.db.get_investigators()
        self._refresh_list()

    def _persist_investigators(self):
        self.db.update_investigators(self.investigators)
        self.investigators = self.db.get_investigators()
        self._refresh_list()

    def _refresh_list(self):
        self.investigator_textbox.configure(state="normal")
        self.investigator_textbox.delete("1.0", "end")
        if self.investigators:
            self.investigator_textbox.insert("1.0", "\n".join(self.investigators))
        else:
            self.investigator_textbox.insert("1.0", "No investigators added yet.")
        self.investigator_textbox.configure(state="disabled")

        for widget in self.list_frame.winfo_children():
            widget.destroy()

        if not self.investigators:
            CTkLabel(
                self.list_frame,
                text="No investigators added yet.",
                text_color=("#6b7280", "#a1a1aa"),
            ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
            return

        for idx, name in enumerate(self.investigators):
            row = CTkFrame(self.list_frame, fg_color="transparent")
            row.grid(row=idx, column=0, sticky="ew", padx=10, pady=6)
            row.grid_columnconfigure(0, weight=1)

            CTkLabel(row, text=name).grid(row=0, column=0, sticky="w")
            CTkButton(
                row,
                text="Remove",
                width=90,
                command=lambda person=name: self.remove_investigator(person),
                fg_color="#dc2626",
                hover_color="#991b1b",
            ).grid(row=0, column=1, padx=(8, 0))

    def add_investigator(self):
        name = self.input_entry.get().strip()
        if not name:
            return
        if name in self.investigators:
            self.input_entry.delete(0, "end")
            return
        self.investigators.append(name)
        self.input_entry.delete(0, "end")
        self._persist_investigators()

    def remove_investigator(self, name):
        if name in self.investigators:
            self.investigators.remove(name)
            self._persist_investigators()

    def save_investigators(self):
        self._persist_investigators()
        messagebox.showinfo("Saved", "Investigators updated successfully.")

    def go_back(self):
        if hasattr(self, "menu_button") and self.menu_button:
            prev = getattr(self.menu_button, "previous_page", None)
            if prev is not None and hasattr(prev, "raise_frame"):
                prev.raise_frame()

    def raise_frame(self):
        self._load_investigators()
        super().raise_frame()
