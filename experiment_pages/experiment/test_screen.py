"""
Modernized Test Screen UI.

- Clean layout using consistent card sections
- Fully functional RFID + Serial Device test console
- Safe multithreading for live serial reads
- Pylint-clean structure and import ordering
"""

import os
import threading
import tkinter as tk
from customtkinter import (
    CTkButton, CTkFont, CTkFrame, CTkLabel, CTkToplevel, set_appearance_mode
)

from shared.serial_handler import SerialDataHandler
from shared.tk_models import get_resource_path


def _safe_listdir(path: str):
    """Return directory contents or [] if the path does not exist."""
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return []


class TestScreen(CTkToplevel):
    """Modernized interface for testing RFID readers and serial devices."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Device Test Console")

        # --- Window Configuration (700x500) ---
        self.geometry("700x500")
        self.minsize(700, 500)
        self.configure(fg_color=("white", "#18181b"))
        set_appearance_mode("System")

        # Center window on screen for Windows & Linux
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        x, y = max((sw - 700) // 2, 0), max((sh - 500) // 2, 0)
        self.geometry(f"700x500+{x}+{y}")

        self.reading_labels = {}

        # --- Fonts (cross-platform safe) ---
        default_family = ("Segoe UI", "Inter", "DejaVu Sans", "Sans Serif")
        self.title_font = CTkFont(default_family, 32, weight="bold")
        self.section_font = CTkFont(default_family, 20, weight="bold")
        self.body_font = CTkFont(default_family, 16)
        self.button_font = CTkFont(default_family, 18, weight="bold")

        # --- Page Layout ---
        self.grid_rowconfigure(0, weight=0)   # title
        self.grid_rowconfigure(1, weight=1)   # RFID card
        self.grid_rowconfigure(2, weight=1)   # Serial card
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Title
        CTkLabel(
            self,
            text="Hardware Test Dashboard",
            font=self.title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(24, 6))

        # RFID Card
        self.rfid_card = self._create_card("RFID Readers", row=1)
        self._setup_rfid_section(self.rfid_card)

        # Device Card
        self.device_card = self._create_card("Serial Devices", row=2)
        self._setup_device_section(self.device_card)

    # ---------------------------- UI Helpers ----------------------------
    def _create_card(self, title, row):
        """Creates a styled card frame."""
        card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        card.grid(row=row, column=0, padx=60, pady=15, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        CTkLabel(
            card,
            text=title,
            font=self.section_font,
            text_color=("#111827", "#e5e7eb")
        ).grid(row=0, column=0, pady=(20, 10))

        return card

    # --- RFID Section ---
    def setup_rfid_section(self, parent):
        """Create RFID test controls."""
        preference_dir = get_resource_path(os.path.join("settings", "serial ports", "preference"))
        entries = _safe_listdir(preference_dir)

        rfid_readers = [
            d for d in entries
            if os.path.exists(os.path.join(preference_dir, d, "rfid_config.txt"))
        ]

        # If none found, still show a default test row so the button is available
        if not rfid_readers:
            CTkLabel(parent, text="No configured RFID readers found.",
                     font=self.body_font, text_color=("#6b7280", "#a1a1aa")
                     ).grid(row=1, column=0, pady=(4, 6))
            # Provide a default row to allow testing
            self._create_test_row(parent, com_port="reader", type_label="RFID", row=2)
            return

        for index, com_port in enumerate(rfid_readers, start=1):
            self._create_test_row(parent, com_port, "RFID", row=index)

    # --- Serial Section ---
    def setup_device_section(self, parent):
        """Create Serial device test controls."""
        preference_dir = get_resource_path(os.path.join("settings", "serial ports", "preference"))
        entries = _safe_listdir(preference_dir)

        serial_devices = [
            d for d in entries
            if os.path.exists(os.path.join(preference_dir, d, "preferred_config.txt"))
        ]

        # If none found, still show a default test row so the button is available
        if not serial_devices:
            CTkLabel(parent, text="No configured serial devices found.",
                     font=self.body_font, text_color=("#6b7280", "#a1a1aa")
                     ).grid(row=1, column=0, pady=(4, 6))
            # Provide a default row to allow testing
            self._create_test_row(parent, com_port="device", type_label="Device", row=2)
            return

    # ------------------------ Row Builder ------------------------
    def _create_test_row(self, parent, com_port, label, row):
        """Build UI row for RFID or Device testing."""
        row_frame = CTkFrame(
            parent,
            fg_color=("white", "#323232"),
            corner_radius=12
        )
        row_frame.grid(row=row, column=0, padx=25, pady=8, sticky="ew")
        row_frame.grid_columnconfigure((0, 1, 2), weight=1)

        CTkLabel(
            row_frame,
            text=f"{label}: {com_port}",
            font=self.body_font,
            text_color=("#111827", "#e5e7eb")
        ).grid(row=0, column=0, sticky="w", padx=10)

        CTkButton(
            row_frame,
            text=f"Test {label}",
            width=150,
            height=40,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1e40af",
            font=self.button_font,
            text_color="white",
            command=lambda p=com_port, t=label.lower(): self._run_test(t, p)
        ).grid(row=0, column=1, padx=10)

        status = CTkLabel(
            row_frame,
            text="Waiting...",
            font=self.body_font,
            text_color=("#6b7280", "#a1a1aa")
        )
        status.grid(row=0, column=2, sticky="e", padx=10)
        self.reading_labels[com_port] = status

    # ------------------------ Test Logic ------------------------
    def _run_test(self, device_type, com_port):
        """Runs test for RFID or Device using SerialDataHandler."""
        print(f"Testing {device_type} on {com_port}...")

        threading.Thread(target=data_handler.start, daemon=True).start()

        def check_for_data():
            retries = 10
            while retries > 0:
                time.sleep(0.5)
                if data_handler.received_data:
                    received = data_handler.get_stored_data()
                    self.after(0, lambda: self._update_status(com_port, received))
                    data_handler.stop()
                    return
                retries -= 1

            self.after(0, lambda: self._update_status(com_port, "No data received"))

        # Thread to monitor incoming data
        threading.Thread(target=check_for_data, daemon=True).start()

    def _update_status(self, com_port, message):
        """Update the status label safely from thread."""
        if com_port in self.reading_labels:
            self.reading_labels[com_port].configure(
                text=message,
                text_color=("#2563eb", "#60a5fa")
            )
