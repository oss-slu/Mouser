"""
Modernized Test Screen UI.

- Redesigned layout using clean section cards and uniform typography
- Preserves full functionality for RFID and Serial device testing
- Uses threading-safe updates for live reading display
- Consistent blue accent theme and adaptive light/dark background
"""

import time
import sqlite3
import threading
import tkinter
from customtkinter import (
    CTkToplevel, CTkFrame, CTkLabel, CTkButton, CTkFont, set_appearance_mode
)
from shared.serial_handler import SerialDataHandler
from shared.serial_port_controller import SerialPortController
from shared.hid_wedge import HIDWedgeListener


class TestScreen(CTkToplevel):
    """Modernized screen for testing RFID readers and serial devices."""

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
        self.hid_listener = None
        self.hid_status_key = None
        self._is_closing = False

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

        # --- Title ---
        CTkLabel(
            self,
            text="Hardware Test Dashboard",
            font=self.title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(24, 6))

        # --- RFID Section ---
        self.rfid_card = self._create_card("RFID Readers", row=1)
        self.setup_rfid_section(self.rfid_card)

        # --- Serial Section ---
        self.device_card = self._create_card("Serial Devices", row=2)
        self.setup_device_section(self.device_card)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _configured_port_for(self, setting_type):
        """Return configured COM/tty port name for a setting type, else None."""
        try:
            controller = SerialPortController(setting_type)
            # retrieve_setting stores the configured serial port in reader_port.
            return controller.reader_port
        except sqlite3.Error:
            return None

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
        configured_port = self._configured_port_for("reader")
        if not configured_port:
            CTkLabel(parent, text="No configured RFID readers found.",
                     font=self.body_font, text_color=("#6b7280", "#a1a1aa")
                     ).grid(row=1, column=0, pady=(4, 6))
            self._create_test_row(parent, com_port="reader", type_label="RFID", row=2)
            return
        self._create_test_row(parent, configured_port, "RFID", row=2)

    # --- Serial Section ---
    def setup_device_section(self, parent):
        """Create Serial device test controls."""
        configured_port = self._configured_port_for("device")
        if not configured_port:
            CTkLabel(parent, text="No configured serial devices found.",
                     font=self.body_font, text_color=("#6b7280", "#a1a1aa")
                     ).grid(row=1, column=0, pady=(4, 6))
            self._create_test_row(parent, com_port="device", type_label="Device", row=2)
            return
        self._create_test_row(parent, configured_port, "Device", row=2)

    # --- Test Row Builder ---
    def _create_test_row(self, parent, com_port, type_label, row):
        """Reusable layout for test rows."""
        device_type = type_label.lower()
        status_key = f"{device_type}:{com_port}"
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
            command=lambda: self._run_test(device_type, com_port, status_key)
        ).grid(row=0, column=1, padx=10, pady=5)

        # Status label
        status = CTkLabel(row_frame, text="Waiting...", font=self.body_font,
                          text_color=("#6b7280", "#a1a1aa"))
        status.grid(row=0, column=2, sticky="e", padx=10, pady=5)
        self.reading_labels[status_key] = status

    # --- Core Logic (unchanged functionality) ---
    def _run_test(self, device_type, com_port, status_key):
        """Runs test for RFID or Serial device using threads."""
        print(f"Testing {device_type} on {com_port}...")
        data_handler = SerialDataHandler("reader" if device_type == "rfid" else "device")
        self._update_status(status_key, "Listening...")

        serial_reader = getattr(data_handler, "reader", None)
        serial_port = getattr(serial_reader, "ser", None)
        if serial_port is None:
            data_handler.stop()
            if device_type == "rfid":
                self._start_hid_fallback(status_key)
            else:
                self._update_status(status_key, "Port unavailable/config mismatch")
            return

        threading.Thread(target=data_handler.start, daemon=True).start()

        def check_for_data():
            retries = 20
            while retries > 0:
                if self._is_closing or not self.winfo_exists():
                    data_handler.stop()
                    return
                time.sleep(0.5)
                if data_handler.received_data:
                    received_data = data_handler.get_stored_data()
                    if not self._is_closing and self.winfo_exists():
                        self.after(0, lambda: self._update_status(status_key, received_data))
                    data_handler.stop()
                    return
                retries -= 1
            data_handler.stop()
            if device_type == "rfid":
                # Some RFID readers present as keyboard-wedge HID even when a COM port exists.
                if not self._is_closing and self.winfo_exists():
                    self.after(0, lambda: self._update_status(
                        status_key, "No serial data; switching to HID fallback..."
                    ))
                    self.after(0, lambda: self._start_hid_fallback(status_key))
            elif not self._is_closing and self.winfo_exists():
                self.after(0, lambda: self._update_status(status_key, "No data received"))

        threading.Thread(target=check_for_data, daemon=True).start()

    def _update_status(self, status_key, message):
        """Safely update label from background thread."""
        if self._is_closing or not self.winfo_exists() or status_key not in self.reading_labels:
            return
        label = self.reading_labels[status_key]
        if not label.winfo_exists():
            return
        try:
            label.configure(text=message, text_color=("#2563eb", "#60a5fa"))
        except tkinter.TclError:
            # The widget can be destroyed between the existence check and configure call.
            return

    def _start_hid_fallback(self, status_key):
        """Enable HID keyboard-wedge fallback for RFID testing."""
        if self.hid_listener:
            self.hid_listener.stop()
            self.hid_listener = None

        self.hid_status_key = status_key
        self._update_status(status_key, "HID fallback: scan tag + Enter")

        def on_tag(tag):
            self._update_status(status_key, f"HID: {tag}")

        self.hid_listener = HIDWedgeListener(self, on_tag=on_tag)
        self.hid_listener.start()
        self.focus_force()

    def _on_close(self):
        """Cleanup listeners on window close."""
        self._is_closing = True
        if self.hid_listener:
            self.hid_listener.stop()
            self.hid_listener = None
        self.destroy()
