import os
from customtkinter import *
from shared.tk_models import *
from shared.serial_handler import SerialDataHandler
import threading

class TestScreen(MouserPage):
    '''Test Screen UI'''
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Test Screen", prev_page)
        
        # Dictionary to track reading labels
        self.reading_labels = {}

        # Create the main frame
        main_frame = CTkFrame(self, corner_radius=15)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.75)

        # Add a title label
        title_label = CTkLabel(
            main_frame, 
            text="Test Screen", 
            font=("Arial", 22, "bold"),  
            pady=20
        )
        title_label.grid(row=0, column=0, columnspan=4, padx=20, pady=20)

        # Header Row
        headers = ["Test", "COM Port", "Device Name", "Reading"]
        for col, header in enumerate(headers):
            header_label = CTkLabel(main_frame, text=header, font=("Arial", 14, "bold"), padx=10, pady=5)
            header_label.grid(row=1, column=col, padx=10, pady=5, sticky="ew")

        # Read preferred devices (COM folders)
        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference")
        preferred_devices = [d for d in os.listdir(preference_dir) if os.path.isdir(os.path.join(preference_dir, d))]

        for index, com_port in enumerate(preferred_devices, start=2):
            config_path = os.path.join(preference_dir, com_port, "preferred_config.txt")
            rfid_path = os.path.join(preference_dir, com_port, "rfid_config.txt")
            device_name = "Unknown"

            if os.path.exists(config_path):
                with open(config_path, "r") as file:
                    device_name = file.readline().strip()

            elif os.path.exists(rfid_path):
                device_name = "RFID Reader"

            # Test Button
            test_button = CTkButton(main_frame, text="Test", command=lambda p=com_port: self.test_serial(p))
            test_button.grid(row=index, column=0, padx=10, pady=5, sticky="ew")

            # COM Port Label
            com_label = CTkLabel(main_frame, text=com_port, padx=10, pady=5)
            com_label.grid(row=index, column=1, sticky="ew")

            # Device Name Label
            device_label = CTkLabel(main_frame, text=device_name, padx=10, pady=5)
            device_label.grid(row=index, column=2, sticky="ew")

            # Default Reading Placeholder
            reading_label = CTkLabel(main_frame, text="-----", padx=10, pady=5)
            reading_label.grid(row=index, column=3, sticky="ew")

            # Store reference to label for later updates
            self.reading_labels[com_port] = reading_label

    def test_serial(self, com_port):
        '''Placeholder function to test serial devices'''
        print(f"Testing serial device on {com_port}...")

        # Placeholder for actual serial reading logic
        test_value = "123.45"  # Replace with actual reading
        data_handler = SerialDataHandler("device")
        data_thread = threading.Thread(target=data_handler.start)
        data_thread.start()

        # Automated handling of data input
        def check_for_data():
            while True:
                if len(data_handler.received_data) >= 2:  # Customize condition
                    received_data = data_handler.get_stored_data()
                    self.reading_labels[com_port].configure(text=received_data)
                    data_handler.stop()
                    self.finish()  # Automatically call the finish method
                    break

        threading.Thread(target=check_for_data, daemon=True).start()

        # Update corresponding label
        if com_port in self.reading_labels:
            self.reading_labels[com_port].configure(text=test_value)
