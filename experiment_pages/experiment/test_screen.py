"""
Modernized Serial Test Screen UI.

- Clean card-style layout with centered content
- Unified blue accent color scheme for consistency
- Clear visual hierarchy for messages and results
- Inline comments document all UI design improvements
"""

from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkButton, CTkFont
from shared.serial_port_controller import SerialPortController


class TestScreen(CTkToplevel):
    """Standalone window for testing connected serial devices."""

    def __init__(self, root):
        super().__init__(root)
        self.title("Serial Test")
        self.geometry("700x500")
        self.resizable(False, False)

        # --- Appearance ---
        self.configure(fg_color=("white", "#1a1a1a"))

        # --- Fonts ---
        title_font = CTkFont(family="Segoe UI", size=28, weight="bold")
        body_font = CTkFont(family="Segoe UI", size=18)
        button_font = CTkFont(family="Segoe UI Semibold", size=20)

        # --- Layout ---
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Title ---
        CTkLabel(
            self,
            text="Serial Connection Test",
            font=title_font,
            text_color=("black", "white")
        ).grid(row=0, column=0, pady=(30, 10))

        # --- Card Container ---
        card = CTkFrame(
            self,
            fg_color=("white", "#2c2c2c"),
            corner_radius=20,
            border_width=1,
            border_color="#d1d5db"
        )
        card.grid(row=1, column=0, padx=60, pady=(10, 20), sticky="nsew")
        card.grid_rowconfigure((0, 1, 2), weight=1)
        card.grid_columnconfigure(0, weight=1)

        # --- Status Label (Dynamic Output) ---
        self.status_label = CTkLabel(
            card,
            text="Click 'Run Test' to check serial connection.",
            font=body_font,
            text_color=("#4a4a4a", "#b0b0b0"),
            wraplength=500,
            justify="center"
        )
        self.status_label.grid(row=0, column=0, pady=(25, 15))

        # --- Test Button ---
        CTkButton(
            card,
            text="Run Test",
            command=self.run_serial_test,
            corner_radius=14,
            height=65,
            width=300,
            font=button_font,
            text_color="white",
            fg_color="#2563eb",
            hover_color="#1e40af"
        ).grid(row=1, column=0, pady=15)

        # --- Close Button ---
        CTkButton(
            card,
            text="Close",
            command=self.destroy,
            corner_radius=14,
            height=60,
            width=250,
            font=button_font,
            text_color="white",
            fg_color="#9ca3af",
            hover_color="#6b7280"
        ).grid(row=2, column=0, pady=(10, 25))

    # --- Functionality (unchanged) ---
    def run_serial_test(self):
        """Attempts to connect and read from a serial device."""
        try:
            controller = SerialPortController("reader")
            ports = controller.list_serial_ports()

            if not ports:
                self.status_label.configure(
                    text="No serial devices detected.\nPlease check your connection.",
                    text_color="#dc2626"  
                )
                return

            # Run a brief connection test
            success = controller.test_connection()
            if success:
                self.status_label.configure(
                    text="✅ Serial connection successful!",
                    text_color="#16a34a"  
                )
            else:
                self.status_label.configure(
                    text="⚠️ Connection failed. Try reconnecting the device.",
                    text_color="#eab308"  
                )

        except Exception as e:  # pylint: disable=broad-exception-caught
            self.status_label.configure(
                text=f"❌ Error during test: {e}",
                text_color="#dc2626"  
            )
