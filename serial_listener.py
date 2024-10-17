import serial

# Read from the serial port
def read_serial_data():
    ser = serial.Serial(port = 'COM1', baudrate = 4800, bytesize = serial.SEVENBITS, parity = serial.PARITY_EVEN, stopbits = serial.STOPBITS_TWO)

    try:
        data = ser.read(19)
        second_measurement = data[11:20]
        decoded_second_measurement = second_measurement.decode('ascii')
        print(data)
        print(second_measurement)
        print(decoded_second_measurement)
        return decoded_second_measurement
    except Exception as e:
        print(f"Error reading from serial port: {e}")
        return None
    finally:
        ser.close()

read_serial_data()
        