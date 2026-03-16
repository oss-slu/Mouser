'''Logger module'''

import os
import datetime
import threading

DEFAULT_LOG_PATH = "dist/Mouser_PoC_PermissionCheck.log"

class Logger:
    '''Handles writing structured log entries to a file.'''
    _lock = threading.Lock()
    @staticmethod
    def log(event, code, message):
        '''Write a log entry with timestamp, event, code, and message.'''
        os.makedirs(os.path.dirname(DEFAULT_LOG_PATH), exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [LOG] Event: {event} | Code: {code} | Message: {message}"
        with Logger._lock:
            with open(DEFAULT_LOG_PATH, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
            print(entry, flush=True)

    