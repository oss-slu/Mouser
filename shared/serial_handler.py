# pylint: skip-file
import time
from shared.serial_listener import SerialReader  # Adjust this to your actual import path

class SerialDataHandler:
    '''Class to handle storing received data.'''
    def __init__(self):
        # Initialize SerialReader and an empty list to store the data
        self.reader = SerialReader(timeout=1)
        self.received_data = []

    def poll_serial_data(self):
        '''Polls the serial reader and stores any received data.'''
        serial_data = self.reader.get_data()
        if serial_data is not None:
            # Store the data in the list
            decoded_data = serial_data.decode('utf-8').strip()
            self.received_data.append(decoded_data)
            print(decoded_data)
        else:
            print("No data available yet.")

    def start(self):
        '''Starts polling for serial data in a loop, typically on a separate thread.'''
        self._running = True
        while self._running:
            self.poll_serial_data()
            # Pause briefly before polling again
            time.sleep(0.5)

    def get_stored_data(self):
        '''Returns the most recent item in the list of stored data.'''
        if self.received_data:
            return self.received_data[-1]
        return None

    def stop(self):
        '''Stops the serial reader and cleanup.'''
        self._running = False
        self.reader.close()

# Example of how to run SerialDataHandler in a separate thread
def main():
    import threading

    data_handler = SerialDataHandler()

    # Start the data handler in a separate thread to prevent blocking
    data_thread = threading.Thread(target=data_handler.start)
    data_thread.start()

    try:
        # Main loop or functionality can go here
        while True:
            print("Main thread is running. Most recent data:", data_handler.get_stored_data())
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping serial reader...")
    finally:
        data_handler.stop()
        data_thread.join()
        print("Serial reader stopped.")

if __name__ == "__main__":
    main()
