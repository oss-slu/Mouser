import serial

# Read from the serial port
def read_serial_data():
    ser = serial.Serial(port = 'COM1', baudrate = 4800, bytesize = serial.SEVENBITS, parity = serial.PARITY_EVEN, stopbits = serial.STOPBITS_TWO)

    try:
        data = ser.read(18)
        print(data.decode('ascii'))
        return data.decode('ascii')
    except Exception as e:
        print(f"Error reading from serial port: {e}")
        return None
    finally:
        ser.close()
