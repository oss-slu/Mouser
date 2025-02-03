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

class SerialPortController():
    '''Serial Port control functions.'''
    def __init__(self, setting_file=None):
        self.ports_in_used = []
        self.baud_rate = None
        self.byte_size = None
        self.parity = None
        self.stop_bits = None
        self.flow_control = None
        self.writer_port = None
        self.reader_port = None
        self.retrieve_setting(setting_file)

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
            except Exception as e:
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
        except Exception as e:
            print(e)

    def retrieve_setting(self, setting_file):
        '''Sets the setting of the serial port opened by converting the 
        setting from csv file to actual setting used.'''
        if setting_file:
            preference_dir = os.path.join(os.getcwd(), "settings", "serial ports", "preference")
            preference_path = os.path.join(preference_dir, setting_file)

            if not os.path.exists(preference_path):
                print(f"Preference file {preference_path} not found.")
                return

            try:
                with open(preference_path, "r") as file:
                    for line in file:
                        settings_file_name = line.strip()
                        print("file name: ", file, "line name: ", line)
                        print(f"Settings file name: {settings_file_name}")
                        settings_path = os.path.join(os.getcwd(), "settings", "serial ports", setting_file)
                        print(f"Settings path: {settings_path}")
                        
                        if not os.path.exists(settings_path):
                            print(f"Settings file {settings_path} not found.")
                            continue
                        
                        with open(settings_path, "r") as settings_file:
                            line = settings_file.readline().strip()
                            settings = line.split(',')
                            print("Successfully retrieved settings.")

                            if len(settings) < 7:
                                print("Error: settings must have at least 7 elements.")
                                continue

                            self.baud_rate = int(settings[0])

                            match settings[3]:
                                case "Five":
                                    self.byte_size = serial.FIVEBITS
                                case "Six":
                                    self.byte_size = serial.SIXBITS
                                case "Seven":
                                    self.byte_size = serial.SEVENBITS
                                case "Eight":
                                    self.byte_size = serial.EIGHTBITS
                                case _:
                                    self.byte_size = serial.EIGHTBITS

                            match settings[1]:
                                case "Space":
                                    self.parity = serial.PARITY_SPACE
                                case "Odd":
                                    self.parity = serial.PARITY_ODD
                                case "Even":
                                    self.parity = serial.PARITY_EVEN
                                case "Mark":
                                    self.parity = serial.PARITY_MARK
                                case _:
                                    self.parity = serial.PARITY_NONE

                            match settings[2]:
                                case "Xon/Xoff":
                                    self.flow_control = 1
                                case "Hardware":
                                    self.flow_control = 2
                                case _:
                                    self.flow_control = None

                            match settings[4]:
                                case "1":
                                    self.stop_bits = serial.STOPBITS_ONE
                                case "1.5":
                                    self.stop_bits = serial.STOPBITS_ONE_POINT_FIVE
                                case "2":
                                    self.stop_bits = serial.STOPBITS_TWO
                                case _:
                                    self.stop_bits = serial.STOPBITS_ONE

                            self.reader_port = settings[6]
            except Exception as e:
                print(f"An error occurred while retrieving settings: {e}")


if __name__ == "__main__":
    controller = SerialPortController('serial_port_preference.csv')
    
    # settings = controller.retrieve_setting('serial_port_preference.csv')
    # print(controller.get_port(settings))

    # data = controller.read_data()
    # print(data)

    available_ports = controller.get_available_ports_name()
    number_of_ports = controller.get_num_ports()
    print("Available system ports:")
    for port in available_ports:
        print(f"{port}")
    print(f"Number of ports: {number_of_ports}")


