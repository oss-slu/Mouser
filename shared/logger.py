'''Logger module'''

import os
import datetime

DEFAULT_LOG_PATH = "dist/Mouser_PoC_PermissionCheck.log"

class Logger:
    '''Handles writing structured log entries to a file.'''
    @staticmethod
    def log(operation_name, error_code, category):
        '''Write a log entry with timestamp, operation name, error code, and category.'''
        os.makedirs(os.path.dirname(DEFAULT_LOG_PATH), exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] Operation: {operation_name} | Error Code: {error_code} | Category: {category}\n"
        with open(DEFAULT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
        print(entry.strip())
