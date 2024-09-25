'''SerialPortController provides list of available serial ports in the pc
the writer port is used to write to a given port, and reader port is
used to read from a port. Note that a port can't be writer and reader
port at the same time.

Virtual testing requires two virtual port, one for reading, one for
writing. In order to do so, you must have both port established before
you write to a port, else reading from the reader port will return
nothing even if you write to writer port already
'''

import serial.tools.list_ports
import serial
import os

class SerialPortController():
    def __init__(self, setting_file=None):
        self.ports_in_used = []
        self.baud_rate = 9600
        self.byte_size = None
        self.parity = None
        self.stop_bits = serial.STOPBITS_ONE
        self.flow_control = None

        self.writer_port = None
        self.reader_port = None

        if setting_file:
            file_path = os.path.abspath(setting_file)
            # file = open(file_path, "r")
            file = open('C:\\Users\\User\\Downloads\\Mouser_windows-latest\\_internal\\settings\\serial ports\\serial_port_preference.csv', 'r')

            file_names = []
            for line in file:
                file_names.append(line)
            if os.name == 'posix':
                setting_file_path = os.getcwd() + "/settings/serial ports/" + file_names[0]
            else:
                setting_file_path = os.path.abspath(file_names[0])
            with open(setting_file_path, "r") as file:
                for line in file:
                    self.retrieve_setting([line[0], line[3], line[1], line[4], line[2]])
                    # Whenever automation is implemented, add the serial port here
                    # self.set_reader_port(line[6])

            # settings = [baud rate, data bits/byte size, parity, stop bits, flow control option]
            # file format: baud rate, parity, flow control option, data bits, stop bits, input method (not needed), port




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

    def read_info(self):
        '''Returns the data read from the reader port as a string.'''
        info = self.reader_port.readline().decode('ascii')
        return info


    def write_to(self, message: str):
        '''Writes message to the writer port as bytes.'''
        byte_message = message.encode()
        self.writer_port.write(byte_message)

    def close_all_port(self):
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
        

    def retrieve_setting(self, settings):
        '''set the setting of the serial port opened by converting the 
        setting from csv file to actual setting used'''
        # settings = [baud rate, data bits/byte size, parity, stop bits, flow control option]

        self.baud_rate = settings[0]

        # byte_size = data bits
        match settings[1]:
            case "Five":
                self.byte_size = serial.FIVEBITS
            case "Six":
                self.byte_size = serial.SIXBITS
            case "Seven":
                self.byte_size = serial.SEVENBITS
            case "Eight":
                self.byte_size = serial.EIGHTBITS
            case _:
                self.byte_size = None

        match settings[2]:
            case "Space":
                self.parity = serial.PARITY_SPACE
            case "Odd":
                self.parity = serial.PARITY_ODD
            case "Even":
                self.parity = serial.PARITY_EVEN
            case "Mark":
                self.parity = serial.PARITY_MARK
            case _:
                self.parity = None

        match settings[3]:
            case 1:
                self.stop_bits = serial.STOPBITS_ONE
            case 1.5:
                self.stop_bits = serial.STOPBITS_ONE_POINT_FIVE
            case 2:
                self.stop_bits = serial.STOPBITS_TWO
        
        match settings[4]:
            case "Xon/Xoff":
                self.flow_control = 1
            case "Hardware":
                self.flow_control = 2
            case _:
                self.flow_control = None
    


