import serial.tools.list_ports
import serial



# recommendation: use com0com to create virtual serial ports and PuTTy to display the result
# to do so, connect the two serial ports from com0com, one for reading on PuTTy (not with our code) 
# and one for writing (with our code)

class SerialPortController():
    def __init__(self):
        self.ports_in_used = []


    def get_available_ports(self):
        available_ports = []
        ports = list(serial.tools.list_ports.comports())

        for port_ in ports:
            if (port_ in self.ports_in_used):       #prevention
                pass
            else:
                available_ports.append((f'{port_.device}', f'{port_.description}'))
        return available_ports
    
    def close_port(self, ser: serial, port: str):
        if (ser.isOpen()):
            ser.close()
        if ser.name in self.ports_in_used:
            self.ports_in_used.remove(port)
    
    def read_info(self, port: str):
        ser = serial.Serial(port, 9600, timeout = 1)
        self.ports_in_used.append(port)
        if (ser.isOpen()):
            ser.close()
        ser.open()
        while True:         # continue asking for data until the other device closes
            info = ser.readline().decode('ascii')
            print(info)
        self.close_port(ser, port)
        # Todo: read data from the port and store it in database
        # Todo: break out of the loop if the time taken to get data is too long



    #for testing purpose only, this function currently doesn't work well
    def write_info(self, port: str):
        ser = serial.Serial(port, 9600, timeout = 1, write_timeout=1)
        message = ""
        while (message != "q"):
            message = input('type something: ')
            print(message)
            byte_message = message.encode()
            print('1')
            ser.write(byte_message)

        ser.close()