# pylint: skip-file
import os
import serial
import threading
from queue import Queue
from shared.serial_port_controller import SerialPortController

class SerialReader:
    def __init__(self, timeout=1, port=None):
        '''Initializes the serial reader, opens the connection, and starts the listening thread.'''
        print(f"Initializing SerialReader with port: {port}")
        self.timeout = timeout
        self.data_queue = Queue()   # A queue to hold the incoming data from the serial port
        self.running = True         # Flag to control the thread
        self.port_controller = SerialPortController(port)
        self.settings = self.port_controller.retrieve_setting(port)
        print(f"Settings: {self.settings}")
        
        if self.settings:
            try:
                # Set up serial port based on retrieved settings
                self.ser = serial.Serial(
                    baudrate=self.port_controller.baud_rate,
                    port=self.port_controller.reader_port,
                    bytesize=self.port_controller.byte_size,
                    parity=self.port_controller.parity,
                    stopbits=self.port_controller.stop_bits,
                    timeout=timeout
                )
                
                # Start the listener thread
                self.thread = threading.Thread(target=self.read_from_serial)
                self.thread.daemon = True  # Daemonize thread to close with the main program
                self.thread.start()

            except serial.SerialException as e:
                print(f"Failed to initialize serial port: {e}")
                self.ser = None
        else:
            print("Error: Serial settings could not be loaded.")
            self.ser = None
        
    def find_device_config(self, port):
        '''Find the corresponding .csv file for the given port.'''
        preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference", port)
        
        if not os.path.exists(preference_dir):
            print(f"ERROR: Preference folder for {port} not found.")
            return None

        try:
            # Read the preferred configuration file
            config_path = os.path.join(preference_dir, "preferred_config.txt")
            rfid_path = os.path.join(preference_dir, "rfid_config.txt")
            if os.path.exists(config_path):
                with open(config_path, "r") as file:
                    device_file_name = file.readline().strip()
                    print(f"Meaurement Device config file found: {device_file_name}")

                    csv_path = os.path.join(os.getcwd(), "settings", "serial ports", device_file_name)
                    if os.path.exists(csv_path):
                        print(f"Device config file found: {device_file_name}")
                        return csv_path
                    else:
                        print(f"ERROR: Device config file {device_file_name} not found.")
                        return None
                    
            elif os.path.exists(rfid_path):
                with open(rfid_path, "r") as file:
                    device_file_name = file.readline().strip()
                    print(f"RFID Device config file found: {device_file_name}")
                    
                    csv_path = os.path.join(os.getcwd(), "settings", "serial ports", device_file_name)
                    if os.path.exists(csv_path):
                        print(f"Device config file found: {device_file_name}")
                        return csv_path
                    else:
                        print(f"ERROR: Device config file {device_file_name} not found.")

            else:
                print(f"ERROR: preferred_config.txt missing for {port}.")
                return None
        except Exception as e:
            print(f"Error reading device config: {e}")
            return None


    def read_from_serial(self):
        '''Runs in a background thread to read from the serial port.'''
        while self.running:
            try:
                # Read a line from the serial device
                if self.ser.is_open:
                    line = self.ser.readline()
                    if line:
                        # Put the read line in the queue
                        self.data_queue.put(line)
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                self.running = False  # Stop running if there's a serial error

    def get_data(self):
        '''Checks if there's data in the queue and returns it.'''
        if not self.data_queue.empty():
            return self.data_queue.get()
        return None

    def close(self):
        '''Stops the serial reader and closes the connection.'''
        self.running = False
        self.thread.join()  # Wait for the thread to finish
        if self.ser.is_open:
            self.ser.close()

    def get_settings(self):
        return self.settings

if __name__ == "__main__":
    handle = SerialReader
    print(handle.get_data())