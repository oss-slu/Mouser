import serial.tools.list_ports
import serial


#this file has nothing to do with main Mouser, just as a test file for different things
data = []
ports = list(serial.tools.list_ports.comports())
print(len(ports))
for port_ in ports:
    print("device: ", port_.device, "description: ", port_.description)

ser = serial.Serial(ports[1].device, 9600, timeout = 1)
message = "Hello whoever you are\n"
ser.write(message.encode('ascii'))
word = ser.readline().decode('ascii')
print(word)

print('hello')