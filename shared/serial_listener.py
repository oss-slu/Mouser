# pylint: skip-file
import os
import threading
from queue import Queue

import serial

from shared.serial_port_controller import SerialPortController


class SerialReader:
    def __init__(self, timeout=1, port=None):
        '''Initializes the serial reader, opens the connection, and starts the listening thread.'''
        print(f"Initializing SerialReader with port: {port}")
        self.timeout = timeout
        self.data_queue = Queue()
        self.running = False  # Start as False until explicitly started
        self.port_controller = SerialPortController(port)
        self.settings = self.port_controller.retrieve_setting(port)
        self.thread = None
        self.ser = None
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
                self.running = True  # Set to True before starting thread
                self.thread = threading.Thread(target=self.read_from_serial)
                self.thread.daemon = True
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
                if self.ser and self.ser.is_open:
                    line = self.ser.readline()
                    if line:
                        self.data_queue.put(line)
                else:
                    print("Serial port is not open, stopping reader thread")
                    break
            except serial.SerialException as e:
                print(f"Error reading from serial port: {e}")
                break  # Exit the thread on serial error
            except Exception as e:
                print(f"Unexpected error in read_from_serial: {e}")
                break
        print("Serial reader thread stopped")

    def get_data(self):
        '''Checks if there's data in the queue and returns it.'''
        try:
            if not self.data_queue.empty():
                return self.data_queue.get_nowait()
        except Exception as e:
            print(f"Error getting data from queue: {e}")
        return None

    def close(self):
        '''Stops the serial reader and closes the connection.'''
        print("Closing serial reader...")
        self.running = False  # Signal thread to stop

        # Close serial port
        if self.ser:
            try:
                if self.ser.is_open:
                    self.ser.close()
            except Exception as e:
                print(f"Error closing serial port: {e}")
            finally:
                self.ser = None

        # Wait for thread to finish
        if self.thread and self.thread.is_alive():
            try:
                self.thread.join(timeout=2)  # Wait up to 2 seconds
                if self.thread.is_alive():
                    print("Warning: Serial reader thread did not stop cleanly")
            except Exception as e:
                print(f"Error joining thread: {e}")
        
        # Clear any remaining data
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except:
                pass

        self.thread = None
        print("Serial reader closed")

    def get_settings(self):
        return self.settings

if __name__ == "__main__":
    handle = SerialReader
    print(handle.get_data())