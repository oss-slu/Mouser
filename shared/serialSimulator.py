'''Serial Simulatior.'''
import shutil

from customtkinter import CTk, CTkToplevel, CTkEntry, CTkButton  # explicit imports recommended

from shared.serial_port_controller import SerialPortController


class SerialSimulator:
    """Serial Simulator User Interface."""

    def __init__(self, parent: CTk):
        self.parent = parent
        self.controller = SerialPortController()
        self.input_entry = None
        self.sent_button = None

    def open(self):
        """Opens Serial Simulator user interface."""

        root = CTkToplevel(self.parent)
        root.title("Serial Port Selection")
        root.geometry("400x700")

        # Use root, not self ― you tried placing widgets onto the SerialSimulator object
        self.input_entry = CTkEntry(root, width=140)
        self.input_entry.place(relx=0.50, rely=0.90, anchor="center")

        self.sent_button = CTkButton(
            root,
            text="Send",
            width=100,
            command=self.write
        )
        self.sent_button.place(relx=0.80, rely=0.90, anchor="center")

    def write(self):
        """Writes to simulated serial output."""
        message = self.input_entry.get()
        print(f"Simulated send: {message}")

    @staticmethod
    def check_installed(name):
        """Checks if a given executable is installed."""
        return shutil.which(name) is not None
