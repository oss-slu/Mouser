"""
Modernized Test Screen UI.

- Clean layout using consistent card sections
- Fully functional RFID + Serial Device test console
- Safe multithreading for live serial reads
- Pylint-clean structure and import ordering
"""

import os
import threading
import time

from customtkinter import (
    CTkButton, CTkFont, CTkFrame, CTkLabel, CTkToplevel, set_appearance_mode
)

from shared.serial_handler import SerialDataHandler


class TestScreen(CTkToplevel):
    """Modernized interface for testing RFID readers and serial devices."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Device Test Console")
        self.geometry("750x600")
        self.configure(fg_color=("white", "#18181b"))
        set_appearance_mode("System")

        self.reading_labels = {}

        # ----------- Fonts -----------
        self.title_font = CTkFont("Segoe UI", 34, weight="bold")
        self.section_font = CTkFont("Segoe UI", 20, weight="bold")
        self.body_font = CTkFont("Segoe UI", 16)
        self.button_font = CTkFont("Segoe UI Semibold", 18)

        # ----------- Layout -----------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Title
        CTkLabel(
            self,
            text="Hardware Test Dashboard",
            font=self.title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(25, 5))

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

    # ------------------------ RFID Section ------------------------
    def _setup_rfid_section(self, parent):
        """Lists and tests RFID readers."""
        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference")
        rfid_readers = [
            d for d in os.listdir(preference_dir)
            if os.path.exists(os.path.join(preference_dir, d, "rfid_config.txt"))
        ]

        for index, com_port in enumerate(rfid_readers, start=1):
            self._create_test_row(parent, com_port, "RFID", row=index)

    # ------------------------ Serial Device Section ------------------------
    def _setup_device_section(self, parent):
        """Lists and tests serial devices."""
        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference")

        self.serial_devices = [
            d for d in os.listdir(preference_dir)
            if os.path.exists(os.path.join(preference_dir, d, "preferred_config.txt"))
        ]

        for index, com_port in enumerate(self.serial_devices, start=1):
            self._create_test_row(parent, com_port, "Device", row=index)

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

        handler_type = "reader" if device_type == "rfid" else "device"
        data_handler = SerialDataHandler(handler_type)

        # Start serial listener thread
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
