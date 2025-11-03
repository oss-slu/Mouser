'''Screen for testing functionality of RFID Readers and Serial Devices.'''
import os
import time
import threading
from customtkinter import *
from shared.tk_models import *
from shared.serial_handler import SerialDataHandler


class TestScreen(CTkToplevel):
    '''Screen for testing functionality of RFID Readers and Serial Devices.'''
    def __init__(self, parent: CTk):
        super().__init__(parent)

        self.title("Test Screen")
        self.geometry("600x500")

        # Dictionary to track reading labels
        self.reading_labels = {}

        # Add a title label
        title_label = CTkLabel(
            self,
            text="Test Screen",
            font=("Arial", 22, "bold"),
            pady=20
        )
        title_label.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

        # Separate sections for RFID Readers and Serial Devices
        self.setup_rfid_section()
        self.setup_device_section()

    def setup_rfid_section(self):
        '''Set up RFID Reader testing section.'''
        rfid_label = CTkLabel(self, text="RFID Reader", font=("Arial", 16, "bold"))
        rfid_label.grid(row=1, column=0, columnspan=2, pady=10)

        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference")
        rfid_readers = [d for d in os.listdir(preference_dir)
                        if os.path.exists(os.path.join(preference_dir, d, "rfid_config.txt"))]

        for index, com_port in enumerate(rfid_readers, start=2):
            test_button = CTkButton(self, text="Test RFID", command=lambda p=com_port: self.test_reader(p))
            test_button.grid(row=index, column=0, padx=10, pady=5, sticky="ew")

            com_label = CTkLabel(self, text=com_port, padx=10, pady=5)
            com_label.grid(row=index, column=1, sticky="ew")

            reading_label = CTkLabel(self, text="-----", padx=10, pady=5)
            reading_label.grid(row=index, column=2, sticky="ew")

            self.reading_labels[com_port] = reading_label

    def setup_device_section(self):
        '''Set up Serial Device testing section.'''
        device_label = CTkLabel(self, text="Serial Device", font=("Arial", 16, "bold"))
        device_label.grid(row=10, column=0, columnspan=2, pady=10)

        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference")
        serial_devices = [d for d in os.listdir(preference_dir)
                          if os.path.exists(os.path.join(preference_dir, d, "preferred_config.txt"))]

        for index, com_port in enumerate(serial_devices, start=11):
            test_button = CTkButton(self, text="Test Device", command=lambda p=com_port: self.test_device(p))
            test_button.grid(row=index, column=0, padx=10, pady=5, sticky="ew")

            com_label = CTkLabel(self, text=com_port, padx=10, pady=5)
            com_label.grid(row=index, column=1, sticky="ew")

            reading_label = CTkLabel(self, text="-----", padx=10, pady=5)
            reading_label.grid(row=index, column=2, sticky="ew")

            self.reading_labels[com_port] = reading_label

    def test_device(self, com_port):
        '''Placeholder function to test serial devices'''
        print(f"Testing serial device on {com_port}...")

        # Start the serial data handler
        data_handler = SerialDataHandler("device")
        data_thread = threading.Thread(target=data_handler.start, daemon=True)
        data_thread.start()

        def check_for_data():
            retries = 10  # Limit retries to prevent infinite loops
            while retries > 0:
                time.sleep(0.5)  # Wait a bit for data to arrive
                if len(data_handler.received_data) > 0:
                    received_data = data_handler.get_stored_data()

                    # Ensure UI update runs in the main thread
                    self.after(0, lambda: self.reading_labels[com_port].configure(text=received_data))

                    data_handler.stop()
                    print(f"Received data: {received_data}")
                    return

                retries -= 1  # Decrease retries count

            print("No data received after retries. Stopping.")

        # Run in a background thread
        threading.Thread(target=check_for_data, daemon=True).start()

    def test_reader(self, com_port):
        '''Function to test serial device reading.'''
        print(f"Testing serial device on {com_port}...")

        # Start the serial data handler
        data_handler = SerialDataHandler("reader")
        data_thread = threading.Thread(target=data_handler.start, daemon=True)
        data_thread.start()

        def check_for_data():
            retries = 10  # Limit retries to prevent infinite loops
            while retries > 0:
                time.sleep(0.5)  # Wait a bit for data to arrive
                if len(data_handler.received_data) > 0:
                    received_data = data_handler.get_stored_data()

                    # Ensure UI update runs in the main thread
                    self.after(0, lambda: self.reading_labels[com_port].configure(text=received_data))

                    data_handler.stop()
                    print(f"Received data: {received_data}")
                    return

                retries -= 1  # Decrease retries count

            print("No data received after retries. Stopping.")

        # Run in a background thread
        threading.Thread(target=check_for_data, daemon=True).start()
