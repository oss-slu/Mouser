# pylint: skip-file
import serial
import threading
from queue import Queue
from shared.serial_port_controller import SerialPortController

class SerialReader:
    def __init__(self, timeout=1):
        '''Initializes the serial reader, opens the connection, and starts the listening thread.'''
        self.timeout = timeout
        self.data_queue = Queue()   # A queue to hold the incoming data from the serial port
        self.running = True         # Flag to control the thread
        self.port_controller = SerialPortController("serial_port_preference.csv")
        self.settings = self.port_controller.retrieve_setting("serial_port_preference.csv")
        
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