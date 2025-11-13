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
import glob
import platform
import serial
import serial.tools.list_ports
import sqlite3 as sql
from shared.file_utils import get_resource_path

class SerialPortController():
    '''Serial Port control functions.'''
    def __init__(self, setting_type=None, comports_fn=None):
        self.ports_in_used = []
        self.baud_rate = None
        self.byte_size = None
        self.parity = None
        self.stop_bits = None
        self.flow_control = None
        self.writer_port = None
        self.reader_port = None
        self.comports_fn = comports_fn or serial.tools.list_ports.comports
        print(f"🔍 Initializing SerialPortController with setting type: {setting_type}")
        self.retrieve_setting(setting_type)

    def get_available_ports(self):
        '''Returns a list of available system ports.
        Linux-specific note: Some USB serial devices (e.g. RFID readers / balances) intermittently fail to appear in
        pyserial.tools.list_ports results on certain distributions (udev timing or driver latency). As a fallback on
        Linux we manually glob common device patterns if the primary enumeration returns nothing. This has no impact
        on Windows/macOS because the fallback only runs when platform.system() == 'Linux'.'''
        ports = list(self.comports_fn())
        available_ports = []
        # Linux fallback if pyserial returns nothing
        if not ports and platform.system() == 'Linux':
            # fallback addresses intermittent pyserial empty list issue
            for pattern in ("/dev/ttyUSB*", "/dev/ttyACM*"):
                for dev in glob.glob(pattern):
                    # Avoid duplicates if device somehow also in ports later
                    if dev not in [p.device for p in ports]:
                        # Create a lightweight shim with .device and .description attributes
                        class _Shim:  # noqa: D401 short-lived internal helper
                            def __init__(self, device):
                                self.device = device
                                self.description = "Unknown (glob fallback)"
                        ports.append(_Shim(dev))
        for port_ in ports:
            if port_ in self.ports_in_used:
                continue
            available_ports.append((port_.device, getattr(port_, 'description', '')))  # robust attribute access
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
        '''Sets the specified port as the writing port.'''
        xonoxoff = False
        rtscts = False
        if self.flow_control == 1:
            xonoxoff = True
        elif self.flow_control == 2:
            rtscts = True

        self.writer_port = serial.Serial(port, baudrate=self.baud_rate,
                                         bytesize=self.byte_size, parity=self.parity, stopbits=self.stop_bits
                                         ,xonxoff=xonoxoff, rtscts=rtscts, timeout = 1 )
        self.ports_in_used.append(self.writer_port)

    def set_reader_port(self, port: str):
        '''Sets the specified port as the reading port.'''
        xonoxoff = False
        rtscts = False
        if self.flow_control == 1:
            xonoxoff = True
        elif self.flow_control == 2:
            rtscts = True

        self.reader_port = serial.Serial(port, baudrate=self.baud_rate,
                                         bytesize=self.byte_size, parity=self.parity, stopbits=self.stop_bits
                                         ,xonxoff=xonoxoff, rtscts=rtscts, timeout = 1 )
        self.ports_in_used.append(self.reader_port)

    def close_writer_port(self):
        '''Closes the writer port if it exists.'''
        if self.writer_port is not None:
            self.writer_port.close()

    def close_reader_port(self):
        '''Closes the reader port if it exists.'''
        if self.reader_port is not None:
            self.reader_port.close()

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
        '''Returns the data read from the reader port as a string.'''
        port = self.reader_port
        baudrate = self.baud_rate
        bytesize = self.byte_size
        parity = self.parity
        stopbits = self.stop_bits
        ser = serial.Serial(port, baudrate, bytesize, parity, stopbits)

        if self.reader_port:
            try:
                reader_data = ser.read(19)
                second_measurement = reader_data[10:20]
                decoded_second_measurement = second_measurement.decode('ascii')
                print(reader_data)
                print(second_measurement)
                print(decoded_second_measurement)
                return decoded_second_measurement
            except sql.Error as e:
                print(f"Error reading from serial port: {e}")
                return None
            finally:
                ser.close()

    def write_to(self, message: str):
        '''Writes message to the writer port as bytes.'''
        byte_message = message.encode()
        self.writer_port.write(byte_message)

    def close_all_ports(self):
        '''Closes all ports in use.'''
        hold = self.ports_in_used
        for port_ in hold:
            port_.close()
            self.ports_in_used.remove(port_)
        self.close_reader_port()
        self.close_writer_port()

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
        except sql.Error as e:
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
            with open(preference_path, "r", encoding="utf-8") as file:
                settings_file_name = file.readline().strip()
                settings_path = get_resource_path(os.path.join("settings", "serial ports", settings_file_name))

                if not os.path.exists(settings_path):
                    print(f"Settings file {settings_path} not found.")
                    return

                with open(settings_path, "r", encoding="utf-8") as settings_file:
                    settings = settings_file.readline().strip().split(',')
                    print("Successfully retrieved settings:", settings)

                    if len(settings) < 7:
                        print("Error: settings must have at least 7 elements.")
                        return

                    self.baud_rate = int(settings[0])
                    self.byte_size = getattr(serial, f"{settings[3].upper()}BITS", serial.EIGHTBITS)
                    self.parity = getattr(serial, f"PARITY_{settings[1].upper()}", serial.PARITY_NONE)
                    self.flow_control = 1 if settings[2] == "Xon/Xoff" else 2 if settings[2] == "Hardware" else None
                    self.stop_bits = getattr(serial, 
                                f"STOPBITS_{settings[4].replace('.', '_').upper()}", serial.STOPBITS_ONE)
                    self.reader_port = settings[6]
                    return settings

<<<<<<< HEAD
        except FileNotFoundError as e:
            print(f"An error occurred while retrieving settings: {e}")
=======
        except Exception as e:
            print(f"An error occurred while retrieving settings: {e}")

    def classify_ports(self):
        '''Classifies available ports into categories: rfid, balance, unknown.
        Heuristics are based on description keywords. Safe on all OS; adds no side effects.'''
        categories = {"rfid": [], "balance": [], "unknown": []}
        for device, desc in self.get_available_ports():
            d_upper = desc.upper()
            if any(k in d_upper for k in ["RFID"]):
                categories["rfid"].append((device, desc))
            elif any(k in d_upper for k in ["BALANCE", "SCALE", "METTLER"]):
                categories["balance"].append((device, desc))
            else:
                categories["unknown"].append((device, desc))
        return categories
>>>>>>> 39b8b7cc08d1c1faaaf16a0d9768f0bf52363670
