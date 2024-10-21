import time
from serial_listener import SerialReader  # Adjust this to your actual import path

class SerialDataHandler:
    '''Class to handle storing received data.'''
    def __init__(self):
        # Initialize SerialReader and an empty list to store the data
        self.reader = SerialReader(timeout=1)
        self.received_data = []

    def store_serial_data(self):
        '''Polls the serial reader and stores any received data.'''
        while True:
            serial_data = self.reader.get_data()
            if serial_data is not None:
                # Store the data in the list
                self.received_data.append(serial_data.decode('utf-8').strip())
                print(serial_data.decode('utf-8').strip())
            else:
                print("No data available yet.")
            # Pause briefly before checking again
            time.sleep(0.5)

    def get_stored_data(self):
        '''Return the list of stored data.'''
        if self.received_data:
            return self.received_data[-1]

    def stop(self):
        '''Stops the serial reader and cleans up resources.'''
        self.reader.close()

# Example use of SerialDataHandler in your app
def main():
    data_handler = SerialDataHandler()

    try:
        data_handler.store_serial_data()
    except KeyboardInterrupt:
        print("Stopping serial reader...")
    finally:
        data_handler.stop()
        print("Serial reader stopped.")

if __name__ == "__main__":
    main()
