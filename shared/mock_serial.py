import time
# pylint: skip-file


class MockSerial:
    def __init__(self, config):
        self.delay = float(config.get("mock", "response_delay_ms", fallback="0")) / 1000
        self.last_write = None         
        self.is_open = False           

    def open(self):
        self.is_open = True
        print("[MOCK] Serial opened")

    def close(self):
        self.is_open = False
        print("[MOCK] Serial closed")

    def write(self, data):
        self.last_write = data
        print("[MOCK] Write: ", data)

    def read(self):
        time.sleep(self.delay)

        if self.last_write == b"PING":
            return b"PONG"
        elif self.last_write == b"STATUS":
            return b"OK"
        else:
            return b"MOCK_DATA"

