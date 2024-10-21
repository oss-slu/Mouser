import serial
import threading
from queue import Queue

class SerialReader:
    def __init__(self, timeout=1):
        '''Initializes the serial reader, opens the connection, and starts the listening thread.'''
        self.timeout = timeout
        self.ser = serial.Serial(port='COM1', baudrate=4800, bytesize=serial.SEVENBITS, parity=serial.PARITY_EVEN, stopbits=serial.STOPBITS_TWO, timeout=timeout)

        # A queue to hold the incoming data from the serial port
        self.data_queue = Queue()

        # Flag to control the thread
        self.running = True

        # Start the listener thread
        self.thread = threading.Thread(target=self.read_from_serial)
        self.thread.daemon = True  # Daemonize thread to close with the main program
        self.thread.start()

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
