'''SerialPortController provides list of available serial ports in the pc
the writer port is used to write to a given port, and reader port is
used to read from a port. Note that a port can't be writer and reader
port at the same time.

Virtual testing requires two virtual port, one for reading, one for
writing. In order to do so, you must have both port established before
you write to a port, else reading from the reader port will return
nothing even if you write to writer port already
'''
import glob
import os
import platform
import sqlite3 as sql

import serial
import serial.tools.list_ports

from shared.file_utils import get_resource_path


class SerialPortController:
    '''Serial Port control functions.'''

    def __init__(self, setting_type=None, comports_fn=None):
        '''Initialize controller and load stored serial settings.'''
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
        '''
        Return list of available system ports.

        On Linux: If pyserial returns an empty list (rare udev latency issue),
        we fallback to manual globbing under /dev/.
        '''
        ports = list(self.comports_fn())
        available_ports = []

        # Linux fallback
        if not ports and platform.system() == 'Linux':
            for pattern in ("/dev/ttyUSB*", "/dev/ttyACM*"):
                for dev in glob.glob(pattern):
                    if dev not in [p.device for p in ports]:
                        class _Shim:  # internal helper
                            def __init__(self, device):
                                self.device = device
                                self.description = "Unknown (glob fallback)"
                        ports.append(_Shim(dev))

        for port_ in ports:
            if port_ in self.ports_in_used:
                continue
            available_ports.append(
                (port_.device, getattr(port_, 'description', ''))
            )

        return available_ports

    def get_available_ports_name(self):
        '''Return only device names for available ports.'''
        available_ports = []
        for port_ in serial.tools.list_ports.comports():
            if port_ not in self.ports_in_used:
                available_ports.append(f'{port_.device}')
        return available_ports

    def get_num_ports(self):
        '''Return number of available system ports.'''
        return len(list(serial.tools.list_ports.comports()))

    def get_virtual_port(self):
        '''Return list of com0com virtual ports.'''
        virtual_ports = []
        for port_ in serial.tools.list_ports.comports():
            if "com0com" in port_.description.split(" "):
                virtual_ports.append(port_.device)
        return virtual_ports

    def _resolve_flow_control(self):
        '''Internal helper to map flow control setting.'''
        xonxoff = False
        rtscts = False
        if self.flow_control == 1:
            xonxoff = True
        elif self.flow_control == 2:
            rtscts = True
        return xonxoff, rtscts

    def set_writer_port(self, port: str):
        '''Open writer (TX) port.'''
        xonxoff, rtscts = self._resolve_flow_control()
        self.writer_port = serial.Serial(
            port, baudrate=self.baud_rate, bytesize=self.byte_size,
            parity=self.parity, stopbits=self.stop_bits,
            xonxoff=xonxoff, rtscts=rtscts, timeout=1
        )
        self.ports_in_used.append(self.writer_port)

    def set_reader_port(self, port: str):
        '''Open reader (RX) port.'''
        xonxoff, rtscts = self._resolve_flow_control()
        self.reader_port = serial.Serial(
            port, baudrate=self.baud_rate, bytesize=self.byte_size,
            parity=self.parity, stopbits=self.stop_bits,
            xonxoff=xonxoff, rtscts=rtscts, timeout=1
        )
        self.ports_in_used.append(self.reader_port)

    def close_writer_port(self):
        '''Close writer port safely.'''
        if self.writer_port is not None:
            self.writer_port.close()

    def close_reader_port(self):
        '''Close reader port safely.'''
        if self.reader_port is not None:
            self.reader_port.close()

    def open_reader_port(self, port_name):
        '''Open reader port with stored settings.'''
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
        except serial.SerialException as exc:
            print(f"Failed to open reader port {port_name}: {exc}")

    def read_data(self):
        '''Read and decode 2nd measurement segment from RFID stream.'''
        port = self.reader_port
        ser = serial.Serial(
            port, self.baud_rate, self.byte_size,
            self.parity, self.stop_bits
        )

        if self.reader_port:
            try:
                reader_data = ser.read(19)
                second_measurement = reader_data[10:20]
                decoded_second_measurement = second_measurement.decode('ascii')
                print(reader_data)
                print(second_measurement)
                print(decoded_second_measurement)
                return decoded_second_measurement
            except sql.Error as exc:
                print(f"Error reading from serial port: {exc}")
            finally:
                ser.close()
        return None

    def write_to(self, message: str):
        '''Write given string to writer port as bytes.'''
        self.writer_port.write(message.encode())

    def close_all_ports(self):
        '''Close all active ports + reader + writer safely.'''
        for port_ in self.ports_in_used[:]:
            port_.close()
            self.ports_in_used.remove(port_)
        self.close_reader_port()
        self.close_writer_port()

    def get_reader_port(self):
        '''Return active reader port object.'''
        return self.reader_port

    def get_writer_port(self):
        '''Return active writer port object.'''
        return self.writer_port

    def get_set_RFID(self, rfid: int):  # pylint: disable=invalid-name
        '''Write RFID value (testing helper).'''
        self.writer_port.write(str(rfid).encode())

    def update_setting(self, port: str):
        '''Re-open reader port if settings changed.'''
        self.close_reader_port()
        try:
            self.set_reader_port(port)
        except sql.Error as exc:
            print(exc)

    def retrieve_setting(self, setting_type):
        '''Sets the setting of the serial port opened by converting the
        setting from csv file to actual setting used.'''
        # Base preference directory inside the project or the PyInstaller bundle
        base_preference_dir = get_resource_path(os.path.join("settings", "serial ports", "preference"))

        if setting_type == "reader":
            setting_file = "rfid_config.txt"
            setting_folder = "reader"
        elif setting_type == "device":
            setting_file = "preferred_config.txt"
            setting_folder = "device"
        else:
            print("Invalid setting type. Must be 'reader' or 'device'.")
            return

        # Build the full path to the preference file using the already-resolved.
        # base_preference_dir to avoid double-wrapping the path with
        # get_resource_path (which would produce incorrect paths).
        preference_path = os.path.join(base_preference_dir, setting_folder, setting_file)
        print(f"🔍 Looking for settings in: {preference_path}")

        if not os.path.exists(preference_path):
            print(f"Preference file {preference_path} not found.")
            return

        try:
            with open(preference_path, "r", encoding="utf-8") as file:
                settings_file_name = file.readline().strip()
                # settings_file_name is relative to 'settings/serial ports', so
                # resolve it via get_resource_path to support bundled execution.
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
                self.byte_size = getattr(
                    serial, f"{settings[3].upper()}BITS", serial.EIGHTBITS
                )
                self.parity = getattr(
                    serial, f"PARITY_{settings[1].upper()}", serial.PARITY_NONE
                )
                self.flow_control = (
                    1 if settings[2] == "Xon/Xoff"
                    else 2 if settings[2] == "Hardware"
                    else None
                )
                self.stop_bits = getattr(
                    serial,
                    f"STOPBITS_{settings[4].replace('.', '_').upper()}",
                    serial.STOPBITS_ONE
                )
                self.reader_port = settings[6]
                return settings

        except Exception as exc:  # pylint: disable=broad-except
            print(f"An error occurred while retrieving settings: {exc}")

    def classify_ports(self):
        '''Classify ports by device description keywords.'''
        categories = {"rfid": [], "balance": [], "unknown": []}

        for device, desc in self.get_available_ports():
            upper_desc = desc.upper()
            if "RFID" in upper_desc:
                categories["rfid"].append((device, desc))
            elif any(k in upper_desc for k in ["BALANCE", "SCALE", "METTLER"]):
                categories["balance"].append((device, desc))
            else:
                categories["unknown"].append((device, desc))

        return categories

    def close_port(self):
        """Close the serial port safely."""
        if self.serial and self.serial.is_open:
            self.serial.close()

    def write_data(self, data: bytes):
        """Write bytes to the serial port."""
        if self.serial and self.serial.is_open:
            self.serial.write(data)
