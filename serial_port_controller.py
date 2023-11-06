import serial.tools.list_ports
import serial



#SerialPortController provides list of available serial ports in the pc
#the writer port is used to write to a given port, and reader port is 
#used to read from a port. Note that a port can't be writer and reader
#port at the same time.

#Virtual testing requires two virtual port, one for reading, one for 
#writing. In order to do so, you must have both port established before
#you write to a port, else reading from the reader port will return 
#nothing even if you write to writer port already

class SerialPortController():
    def __init__(self):
        self.ports_in_used = []
        self.writer_port = None
        self.reader_port = None


    def get_available_ports(self):
        available_ports = []
        ports = list(serial.tools.list_ports.comports())

        for port_ in ports:
            if (port_ in self.ports_in_used):       #prevention
                pass
            else:
                available_ports.append((f'{port_.device}', f'{port_.description}'))
        return available_ports
    
    def get_virtual_port(self):
        virtual_ports = []
        ports = list(serial.tools.list_ports.comports())
        for port_ in ports:
            words = port_.description.split(" ")
            if ("com0com" in words):
                virtual_ports.append(port_.device)

        return virtual_ports

    def set_writer_port(self, port: str):
        self.writer_port = serial.Serial(port, 9600, timeout = 1 )
        self.ports_in_used.append(self.writer_port)

    def set_reader_port(self, port: str):
        self.reader_port = serial.Serial(port, 9600, timeout = 1 )
        self.ports_in_used.append(self.reader_port)

    def close_writer_port(self):
        if (self.writer_port != None):
            self.writer_port.close()


    def close_reader_port(self):
        if (self.reader_port != None):
            self.reader_port.close()
    
    def read_info(self):

        info = self.reader_port.readline().decode('ascii')
        return info


    def write_to(self, message: str):

        byte_message = message.encode()
        self.writer_port.write(byte_message)

    def close_all_port(self):
        hold = self.ports_in_used
        for port_ in hold:
            port_.close()
            self.ports_in_used.remove(port_)

        self.close_reader_port()
        self.close_writer_port()

