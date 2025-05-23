'''SerialPortController provides list of available serial ports in the pc
the writer port is used to write to a given port, and reader port is
used to read from a port. Note that a port can't be writer and reader
port at the same time.

Virtual testing requires two virtual port, one for reading, one for
writing. In order to do so, you must have both port established before
you write to a port, else reading from the reader port will return
nothing even if you write to writer port already
'''
import os
import serial
import serial.tools.list_ports
import threading
from shared.file_utils import get_resource_path

class SerialPortController():
    '''Serial Port control functions.'''
    def __init__(self, setting_type=None):
        self.ports_in_used = []
        self.baud_rate = None
        self.byte_size = None
        self.parity = None
        self.stop_bits = None
        self.flow_control = None
        self.writer_port = None
        self.reader_port = None
        self._lock = threading.Lock()  # Add thread lock
        print(f"🔍 Initializing SerialPortController with setting type: {setting_type}")
        self.retrieve_setting(setting_type)

    def get_available_ports(self):
        '''Returns a list of available system ports.'''
        available_ports = []
        ports = list(serial.tools.list_ports.comports())
        for port_ in ports:
            if port_ in self.ports_in_used:       #prevention
                pass
            else:
                available_ports.append((f'{port_.device}', f'{port_.description}'))
        return available_ports

    def get_available_ports_name(self):
        '''Returns a list of available system ports.'''
        available_ports = []
        ports = list(serial.tools.list_ports.comports())
        for port_ in ports:
            if port_ in self.ports_in_used:       #prevention
                pass
            else:
                available_ports.append(f'{port_.device}')
        return available_ports

    def get_num_ports(self):
        '''Returns the number of available ports.'''
        return len(list(serial.tools.list_ports.comports()))

    def get_virtual_port(self):
        '''Returns a list of available virtual ports.'''
        virtual_ports = []
        ports = list(serial.tools.list_ports.comports())
        for port_ in ports:
            words = port_.description.split(" ")
            if "com0com" in words:
                virtual_ports.append(port_.device)
        return virtual_ports

    def set_writer_port(self, port: str):
        '''Thread-safe method to set the writer port.'''
        with self._lock:
            xonoxoff = False
            rtscts = False
            if self.flow_control == 1:
                xonoxoff = True
            elif self.flow_control == 2:
                rtscts = True

            try:
                self.writer_port = serial.Serial(port, baudrate=self.baud_rate,
                                             bytesize=self.byte_size, parity=self.parity,
                                             stopbits=self.stop_bits,
                                             xonxoff=xonoxoff, rtscts=rtscts, timeout=1)
                self.ports_in_used.append(self.writer_port)
            except serial.SerialException as e:
                print(f"Error setting writer port: {e}")
                raise

    def set_reader_port(self, port: str):
        '''Thread-safe method to set the reader port.'''
        with self._lock:
            xonoxoff = False
            rtscts = False
            if self.flow_control == 1:
                xonoxoff = True
            elif self.flow_control == 2:
                rtscts = True

            try:
                self.reader_port = serial.Serial(port, baudrate=self.baud_rate,
                                             bytesize=self.byte_size, parity=self.parity,
                                             stopbits=self.stop_bits,
                                             xonxoff=xonoxoff, rtscts=rtscts, timeout=1)
                self.ports_in_used.append(self.reader_port)
            except serial.SerialException as e:
                print(f"Error setting reader port: {e}")
                raise

    def close_writer_port(self):
        '''Thread-safe method to close the writer port.'''
        with self._lock:
            if self.writer_port is not None:
                try:
                    self.writer_port.close()
                    if self.writer_port in self.ports_in_used:
                        self.ports_in_used.remove(self.writer_port)
                except Exception as e:
                    print(f"Error closing writer port: {e}")
                finally:
                    self.writer_port = None

    def close_reader_port(self):
        '''Thread-safe method to close the reader port.'''
        with self._lock:
            if self.reader_port is not None:
                try:
                    self.reader_port.close()
                    if self.reader_port in self.ports_in_used:
                        self.ports_in_used.remove(self.reader_port)
                except Exception as e:
                    print(f"Error closing reader port: {e}")
                finally:
                    self.reader_port = None
    def open_reader_port(self, port_name):
        '''Open the reader port with the specified settings.'''
        try:
            self.reader_port = serial.Serial(
                port=port_name,
                baudrate=self.baud_rate,
                bytesize=self.byte_size,
                parity=self.parity,
                stopbits=self.stop_bits,
                timeout=1
            )
            print(f"Reader port {port_name} opened successfully.")
        except serial.SerialException as e:
            print(f"Failed to open reader port {port_name}: {e}")

    def get_port(self, settings_list):
        '''Returns the port from the settings list.'''
        if settings_list[6] is not None:
            return settings_list[6]
        else:
            return None

    def read_data(self):
        '''Thread-safe method to read from the reader port.'''
        with self._lock:
            if self.reader_port is None or not self.reader_port.is_open:
                raise serial.SerialException("Reader port is not open")
            try:
                reader_data = self.reader_port.read(19)
                if reader_data:
                    second_measurement = reader_data[10:20]
                    return second_measurement.decode('ascii')
                return None
            except Exception as e:
                print(f"Error reading from port: {e}")
                raise

    def write_to(self, message: str):
        '''Thread-safe method to write to the writer port.'''
        with self._lock:
            if self.writer_port is None or not self.writer_port.is_open:
                raise serial.SerialException("Writer port is not open")
            try:
                byte_message = message.encode()
                self.writer_port.write(byte_message)
            except Exception as e:
                print(f"Error writing to port: {e}")
                raise

    def close_all_ports(self):
        '''Thread-safe method to close all ports.'''
        with self._lock:
            try:
                for port in self.ports_in_used[:]:  # Create a copy of the list
                    try:
                        port.close()
                    except Exception as e:
                        print(f"Error closing port: {e}")
                self.ports_in_used.clear()
                self.close_reader_port()
                self.close_writer_port()
            except Exception as e:
                print(f"Error in close_all_ports: {e}")

    def get_reader_port(self):
        '''Returns the reader port.'''
        return self.reader_port

    def get_writer_port(self):
        '''Returns the writer port.'''
        return self.writer_port

    def get_set_RFID(self, rfid: int): #pylint: disable= invalid-name
        '''Testing function for map_rfid serial port.'''
        message = rfid.encode()
        self.writer_port.write(message)

    def update_setting(self, port: str):
        ''' updates the setting of the reader port if there's any notable changes'''
        self.close_reader_port()
        try:
            self.set_reader_port(port)
        except Exception as e:
            print(e)

    def retrieve_setting(self, setting_type):
        '''Sets the setting of the serial port opened by converting the
        setting from csv file to actual setting used.'''
        preference_dir = get_resource_path(os.path.join("settings", "serial ports", "preference"))

        if setting_type == "reader":
            setting_file = "rfid_config.txt"
            setting_folder = "reader"
        elif setting_type == "device":
            setting_file = "preferred_config.txt"
            setting_folder = "device"
        else:
            print("Invalid setting type. Must be 'reader' or 'device'.")
            return

        preference_path = get_resource_path(os.path.join(preference_dir, setting_folder, setting_file))
        print(f"🔍 Looking for settings in: {preference_path}")

        if not os.path.exists(preference_path):
            print(f"Preference file {preference_path} not found.")
            return

        try:
            with open(preference_path, "r") as file:
                settings_file_name = file.readline().strip()
                settings_path = get_resource_path(os.path.join("settings", "serial ports", settings_file_name))

                if not os.path.exists(settings_path):
                    print(f"Settings file {settings_path} not found.")
                    return

                with open(settings_path, "r") as settings_file:
                    settings = settings_file.readline().strip().split(',')
                    print("Successfully retrieved settings:", settings)

                    if len(settings) < 7:
                        print("Error: settings must have at least 7 elements.")
                        return

                    self.baud_rate = int(settings[0])
                    self.byte_size = getattr(serial, f"{settings[3].upper()}BITS", serial.EIGHTBITS)
                    self.parity = getattr(serial, f"PARITY_{settings[1].upper()}", serial.PARITY_NONE)
                    self.flow_control = 1 if settings[2] == "Xon/Xoff" else 2 if settings[2] == "Hardware" else None
                    self.stop_bits = getattr(serial, f"STOPBITS_{settings[4].replace('.', '_').upper()}", serial.STOPBITS_ONE)
                    self.reader_port = settings[6]
                    return settings

        except Exception as e:
            print(f"An error occurred while retrieving settings: {e}")