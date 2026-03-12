"""Experiment Investigators editor UI."""

from tkinter import messagebox
from customtkinter import (
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkEntry,
    CTkScrollableFrame,
    CTkFont,
)
from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage

class InvestigatorsUI(MouserPage):
    """Page for viewing and editing experiment investigators."""

    def __init__(self, parent, prev_page=None, file_path: str = ""):
        super().__init__(parent, "Investigators", prev_page)
        self.file_path = file_path
        self.db = ExperimentDatabase(file_path)
        self.investigators = self.db.get_investigators()

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
        card.grid_rowconfigure(1, weight=1)
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

        self.list_frame = CTkScrollableFrame(card, fg_color=("white", "#1f2937"))
        self.list_frame.grid(row=1, column=0, padx=25, pady=10, sticky="nsew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        actions = CTkFrame(card, fg_color="transparent")
        actions.grid(row=2, column=0, padx=25, pady=(10, 20), sticky="e")

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

        self._refresh_list()

    def _refresh_list(self):
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
        '''Add investigator from input field.'''
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
        '''Remove investigator by name.'''
        if name in self.investigators:
            self.investigators.remove(name)
            self._refresh_list()

    def save_investigators(self):
        '''Save investigators to database.'''
        self.db.update_investigators(self.investigators)
        messagebox.showinfo("Saved", "Investigators updated successfully.")

    def go_back(self):
        '''Navigate back to previous page.'''
        if hasattr(self, "menu_button") and self.menu_button:
            prev = getattr(self.menu_button, "previous_page", None)
            if prev is not None and hasattr(prev, "raise_frame"):
                prev.raise_frame()
