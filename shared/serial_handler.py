# pylint: skip-file
import time
import threading
from shared.serial_listener import SerialReader  # Adjust this to your actual import path

class SerialDataHandler:
    '''Class to handle storing received data.'''
    def __init__(self, port=None):
        print(f"Initializing SerialDataHandler on port: {port}")
        self.reader = SerialReader(timeout=1, port=port)
        self.received_data = []
        self._running = False
        self.lock = threading.Lock()
        self.listener_thread = None

    def poll_serial_data(self):
        '''Polls the serial reader and stores any received data.'''
        try:
            serial_data = self.reader.get_data()
            if serial_data is not None:
                decoded_data = serial_data.decode('utf-8').strip()
                with self.lock:
                    self.received_data.append(decoded_data)
                print(f"Received data: {decoded_data}")
        except Exception as e:
            print(f"Error polling serial data: {e}")
            self._running = False  # Stop on error

    def start(self):
        '''Starts polling for serial data in a loop.'''
        if self._running:
            print("⚠️ SerialDataHandler is already running!")
            return
        
        self._running = True
        print("🔄 SerialDataHandler started listening...")

        def listen_loop():
            while self._running:
                if not self.reader:  # Check if reader was closed
                    break
                self.poll_serial_data()
                time.sleep(0.1)  # Shorter sleep for more responsive stopping
            print("🛑 Listen loop ended")

        self.listener_thread = threading.Thread(target=listen_loop, daemon=True)
        self.listener_thread.start()

    def stop(self):
        '''Stops the serial reader and cleanup.'''
        print("📥 Stopping SerialDataHandler...")
        self._running = False
        
        # Wait for listener thread to finish
        if self.listener_thread and self.listener_thread.is_alive():
            try:
                self.listener_thread.join(timeout=2)
                if self.listener_thread.is_alive():
                    print("⚠️ Warning: Listener thread did not stop cleanly")
            except Exception as e:
                print(f"Error joining listener thread: {e}")

        # Close the reader
        if self.reader:
            try:
                self.reader.close()
            except Exception as e:
                print(f"Error closing reader: {e}")
            finally:
                self.reader = None

        self.listener_thread = None
        print("✅ SerialDataHandler stopped")

    def close(self):
        '''Alias for stop() for compatibility.'''
        self.stop()

    def get_stored_data(self):
        '''Returns the most recent item in the list of stored data.'''
        with self.lock:
            return self.received_data.pop(0) if self.received_data else None

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
