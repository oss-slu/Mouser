"""Experiment Summary UI (Step 3 of 3)."""

from __future__ import annotations

from tkinter import filedialog

from customtkinter import (
    CTk,
    CTkFrame,
    CTkLabel,
    CTkButton,
    CTkTextbox,
    CTkToplevel,
    CTkFont,
    CTkScrollableFrame,
)

from shared.tk_models import MouserPage  # pylint: disable=import-error
from shared.experiment import Experiment  # pylint: disable=import-error
from shared.audio import AudioManager  # pylint: disable=import-error
from shared.file_utils import SUCCESS_SOUND  # pylint: disable=import-error


class SummaryUI(MouserPage):
    """Displays experiment details before final creation."""

    def __init__(
        self,
        experiment: Experiment,
        parent: CTk,
        prev_page: CTkFrame,
        menu_page: CTkFrame,
    ):
        super().__init__(parent, "", prev_page)
        try:
            self.canvas.itemconfigure(self.rectangle, state="hidden")
        except Exception:
            pass

        palette = {
            "bg": ("#f8fafc", "#0b1220"),
            "text_muted": ("#64748b", "#94a3b8"),
            "card_border": ("#e2e8f0", "#223044"),
            "entry_bg": ("#ffffff", "#0b1220"),
            "entry_border": ("#cbd5e1", "#334155"),
            "accent_blue": "#3b82f6",
            "accent_amber": "#f59e0b",
            "accent_green": "#22c55e",
        }
        self.ui_palette = palette
        self.configure(fg_color=palette["bg"])

        self.experiment = experiment
        self.menu_page = menu_page

        # Top actions
        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=36,
                width=150,
                font=("Segoe UI Semibold", 15),
                text_color="white",
                fg_color=palette["accent_amber"],
                hover_color="#d97706",
            )
            self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=8, anchor="nw")

        self.create_button = CTkButton(
            self,
            text="Create",
            corner_radius=12,
            height=36,
            width=150,
            font=("Segoe UI Semibold", 15),
            text_color="white",
            fg_color=palette["accent_green"],
            hover_color="#16a34a",
            command=self.create_experiment,
        )
        self.create_button.place_configure(relx=1.0, rely=0.0, x=-16, y=8, anchor="ne")

        # Main Layout (scrolling)
        body_root = CTkScrollableFrame(self, fg_color="transparent")
        body_root.place(relx=0.5, rely=0.0, y=56, anchor="n", relwidth=0.96, relheight=0.91)
        body_root.grid_columnconfigure(0, weight=1)
        body_root.grid_rowconfigure(1, weight=1)

        title_font = CTkFont(family="Segoe UI Semibold", size=22)
        subtitle_font = CTkFont(family="Segoe UI", size=12)
        section_title_font = CTkFont(family="Segoe UI Semibold", size=14)
        label_font = CTkFont(family="Segoe UI Semibold", size=12)
        value_font = CTkFont(family="Segoe UI", size=13)

        header = CTkFrame(body_root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 6))
        CTkLabel(header, text="Experiment Summary", font=title_font).pack(anchor="w")
        CTkLabel(
            header,
            text="Step 3 of 3 • Review everything before creating the experiment",
            font=subtitle_font,
            text_color=palette["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        content = CTkFrame(body_root, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))
        content.grid_columnconfigure(0, weight=1)

        def section(parent_section: CTkFrame, title: str, *, accent: str, bg_color):
            box = CTkFrame(
                parent_section,
                corner_radius=12,
                fg_color=bg_color,
                border_width=1,
                border_color=palette["card_border"],
            )
            CTkFrame(box, height=4, corner_radius=12, fg_color=accent).pack(fill="x")
            CTkLabel(
                box,
                text=title,
                font=section_title_font,
                text_color=(accent, "#ffffff"),
            ).pack(anchor="w", padx=12, pady=(8, 4))
            body = CTkFrame(box, fg_color="transparent")
            body.pack(fill="x", padx=12, pady=(0, 8))
            body.grid_columnconfigure(0, weight=1)
            return box, body

        details_box, self.details_body = section(
            content,
            "Details",
            accent=palette["accent_blue"],
            bg_color=("#eff6ff", "#0b1b35"),
        )
        details_box.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        notes_box, self.notes_body = section(
            content,
            "Additional Notes",
            accent=palette["accent_amber"],
            bg_color=("#fff7ed", "#2a1605"),
        )
        notes_box.grid(row=1, column=0, sticky="ew")

        self._label_font = label_font
        self._value_font = value_font
        self.display_summary()

    def display_summary(self):
        """Populate the summary UI with experiment details and notes."""
        details = {
            "Experiment Name": self.experiment.get_name(),
            "Investigators": ", ".join(self.experiment.get_investigators()),
            "Species": self.experiment.get_species(),
            "Measurement Items": self.experiment.get_measurement_items(),
            "Number of Animals": self.experiment.get_num_animals(),
            "Animals per Cage": self.experiment.get_max_animals(),
            "Group Names": ", ".join(self.experiment.group_names)
            if hasattr(self.experiment, "group_names")
            else "",
            "Uses RFID": "Yes" if self.experiment.uses_rfid() else "No",
        }

        for widget in self.details_body.winfo_children():
            widget.destroy()
        for widget in self.notes_body.winfo_children():
            widget.destroy()

        grid = CTkFrame(self.details_body, fg_color="transparent")
        grid.pack(fill="x", pady=(6, 6))
        grid.grid_columnconfigure(0, weight=0)
        grid.grid_columnconfigure(1, weight=1)

        for i, (label, value) in enumerate(details.items()):
            CTkLabel(
                grid,
                text=label,
                font=self._label_font,
                text_color=self.ui_palette["text_muted"],
            ).grid(row=i, column=0, sticky="w", padx=(0, 14), pady=4)
            CTkLabel(
                grid,
                text=value or "—",
                font=self._value_font,
                wraplength=720,
                justify="left",
            ).grid(row=i, column=1, sticky="w", pady=4)

        self.notes_entry = CTkTextbox(
            self.notes_body,
            height=120,
            font=("Segoe UI", 13),
            wrap="word",
            corner_radius=10,
        )
        self.notes_entry.pack(fill="x", pady=(6, 6))

        existing_notes = getattr(self.experiment, "notes", "")
        if existing_notes:
            self.notes_entry.insert("1.0", existing_notes)

    def update_page(self):
        """Refresh the summary when experiment data changes."""
        self.display_summary()

    def create_experiment(self):
        """Finalize experiment creation: save DB and return to Home."""
        self.experiment.notes = self.notes_entry.get("1.0", "end-1c").strip()

        save_dir = filedialog.askdirectory(
            title="Select Directory to Save Experiment",
        )
        if not save_dir:
            return

        try:  # pylint: disable=broad-exception-caught
            self.experiment.save_to_database(save_dir)
        except Exception as exc:  # noqa: BLE001
            popup = CTkToplevel(self)
            popup.title("Save Error")
            popup.geometry("360x180")
            popup.resizable(False, False)
            popup.transient(self)
            popup.attributes('-topmost', 1)
            popup.grab_set()

            CTkLabel(
                popup,
                text=f"Failed to save experiment:\n{exc}",
                wraplength=320,
                font=("Segoe UI", 14),
            ).pack(pady=20)

            CTkButton(
                popup,
                text="OK",
                command=popup.destroy,
                corner_radius=8,
                fg_color="#2563eb",
                hover_color="#1e40af",
                text_color="white",
                width=80,
            ).pack(pady=10)
            return

        AudioManager.play(SUCCESS_SOUND)

        popup = CTkToplevel(self)
        popup.title("Experiment Created")
        popup.geometry("320x160")
        popup.resizable(False, False)
        popup.transient(self)
        popup.attributes('-topmost', 1)

        def close_and_go_home():
            popup.destroy()
            if self.menu_page is not None:
                self.menu_page.raise_frame()

        CTkLabel(
            popup,
            text="Experiment successfully created!",
            font=("Segoe UI", 16, "bold"),
        ).pack(pady=20)

        CTkButton(
            popup,
            text="OK",
            command=close_and_go_home,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
            width=80,
        ).pack(pady=10)

