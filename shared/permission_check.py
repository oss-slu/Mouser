'''Permission check module for PoC.'''
import os
from logger import Logger

class PermissionCheck:
    '''Simple PoC for permission, driver, port, and environment checks.'''
    @staticmethod
    def check_permissions(file_path):
        '''Check permission for file path'''
        try:
            open(file_path, "r")
            Logger.log("Permission Check", 0, "PERMISSION_OK")
        except PermissionError as e:
            Logger.log("Permission Check", e.errno, "PERMISSION_DENIED")

    @staticmethod
    def check_driver(device_path):
        '''Check if device path exists'''
        if not os.path.exists(device_path):
            Logger.log("Driver Check", 2, "DRIVER_MISSING")
        else:
            Logger.log("Driver Check", 0, "DRIVER_OK")

    @staticmethod
    def check_port_busy(port_name):
        '''Check if port is busy'''
        try:
            open(port_name)
            Logger.log("Port Check", 0, "PORT_FREE")
        except OSError as e:
            if e.errno == 16:  # Device or resource busy
                Logger.log("Port Check", e.errno, "PORT_BUSY")
            else:
                Logger.log("Port Check", e.errno, "UNKNOWN_ERROR")

    @staticmethod
    def check_closed_environment():
        '''Check if running in a closed environment'''
        try:
            Logger.log("Environment Check", 0, "ENV_OK")
        except Exception as e:
            Logger.log("Environment Check", -1, "ENV_RESTRICTED")

    @staticmethod
    def check_all_permissions():
        '''Run all checks and log results.'''
        PermissionCheck.check_permissions("shared/test_file.txt") 
        PermissionCheck.check_driver("/dev/ttyUSB0")
        PermissionCheck.check_port_busy("/dev/ttyUSB0")
        PermissionCheck.check_closed_environment()
