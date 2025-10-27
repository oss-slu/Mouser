"""
Modernized Test Screen UI.

- Redesigned layout using clean section cards and uniform typography
- Preserves full functionality for RFID and Serial device testing
- Uses threading-safe updates for live reading display
- Consistent blue accent theme and adaptive light/dark background
"""

import os
import time
import threading
from customtkinter import (
    CTkToplevel, CTkFrame, CTkLabel, CTkButton, CTkFont, set_appearance_mode
)
from shared.serial_handler import SerialDataHandler
from shared.tk_models import get_resource_path


class TestScreen(CTkToplevel):
    """Modernized screen for testing RFID readers and serial devices."""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("Device Test Console")
        self.geometry("700x500")
        self.configure(fg_color=("white", "#18181b"))
        set_appearance_mode("System")

        self.reading_labels = {}

        # --- Fonts ---
        self.title_font = CTkFont("Segoe UI", 32, weight="bold")
        self.section_font = CTkFont("Segoe UI", 20, weight="bold")
        self.body_font = CTkFont("Segoe UI", 16)
        self.button_font = CTkFont("Segoe UI Semibold", 18)

        # --- Page Layout ---
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        CTkLabel(
            self,
            text="Hardware Test Dashboard",
            font=self.title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(30, 10))

        # --- RFID Section ---
        self.rfid_card = self._create_card("RFID Readers", row=1)
        self.setup_rfid_section(self.rfid_card)

        # --- Serial Section ---
        self.device_card = self._create_card("Serial Devices", row=2)
        self.setup_device_section(self.device_card)

    # --- Card Builder ---
    def _create_card(self, title, row):
        """Helper: Create consistent card container for each section."""
        card = CTkFrame(
            self,
            fg_color=("white", "#27272a"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        card.grid(row=row, column=0, padx=80, pady=20, sticky="nsew")
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
        # Resolve the settings preference directory using get_resource_path so
        # the path works both during development and when bundled by
        # PyInstaller (which uses a temporary _MEIPASS base directory).
        preference_dir = get_resource_path(os.path.join("settings", "serial ports", "preference"))
        rfid_readers = [
            d for d in os.listdir(preference_dir)
            if os.path.exists(os.path.join(preference_dir, d, "rfid_config.txt"))
        ]

        if not rfid_readers:
            CTkLabel(parent, text="No RFID readers found.", font=self.body_font,
                     text_color=("#6b7280", "#a1a1aa")).grid(row=1, column=0, pady=10)
            return

        for index, com_port in enumerate(rfid_readers, start=1):
            self._create_test_row(parent, com_port, "RFID", row=index + 1)

    # --- Serial Section ---
    def setup_device_section(self, parent):
        """Create Serial device test controls."""
        # Use get_resource_path here as well for bundled execution.
        preference_dir = get_resource_path(os.path.join("settings", "serial ports", "preference"))
        serial_devices = [
            d for d in os.listdir(preference_dir)
            if os.path.exists(os.path.join(preference_dir, d, "preferred_config.txt"))
        ]

        if not serial_devices:
            CTkLabel(parent, text="No serial devices found.", font=self.body_font,
                     text_color=("#6b7280", "#a1a1aa")).grid(row=1, column=0, pady=10)
            return

        for index, com_port in enumerate(serial_devices, start=1):
            self._create_test_row(parent, com_port, "Device", row=index + 1)

    # --- Test Row Builder ---
    def _create_test_row(self, parent, com_port, type_label, row):
        """Reusable layout for test rows."""
        row_frame = CTkFrame(parent, fg_color=("white", "#323232"), corner_radius=12)
        row_frame.grid(row=row, column=0, padx=25, pady=8, sticky="ew")
        row_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Port label
        CTkLabel(row_frame, text=f"{type_label}: {com_port}", font=self.body_font,
                 text_color=("#111827", "#e5e7eb")).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # Test button
        CTkButton(
            row_frame,
            text=f"Test {type_label}",
            width=180,
            height=40,
            corner_radius=10,
            fg_color="#2563eb",
            hover_color="#1e40af",
            font=self.button_font,
            text_color="white",
            command=lambda: self._run_test(type_label.lower(), com_port)
        ).grid(row=0, column=1, padx=10, pady=5)

        # Status label
        status = CTkLabel(row_frame, text="Waiting...", font=self.body_font,
                          text_color=("#6b7280", "#a1a1aa"))
        status.grid(row=0, column=2, sticky="e", padx=10, pady=5)
        self.reading_labels[com_port] = status

    # --- Core Logic (unchanged functionality) ---
    def _run_test(self, device_type, com_port):
        """Runs test for RFID or Serial device using threads."""
        print(f"Testing {device_type} on {com_port}...")
        data_handler = SerialDataHandler("reader" if device_type == "rfid" else "device")

        # Start handler thread
        threading.Thread(target=data_handler.start, daemon=True).start()

        def check_for_data():
            retries = 10
            while retries > 0:
                time.sleep(0.5)
                if data_handler.received_data:
                    received_data = data_handler.get_stored_data()
                    self.after(0, lambda: self._update_status(com_port, received_data))
                    data_handler.stop()
                    return
                retries -= 1
            self.after(0, lambda: self._update_status(com_port, "No data received"))

        threading.Thread(target=check_for_data, daemon=True).start()

    def _update_status(self, com_port, message):
        """Safely update label from background thread."""
        if com_port in self.reading_labels:
            self.reading_labels[com_port].configure(
                text=message, text_color=("#2563eb", "#60a5fa")
            )
