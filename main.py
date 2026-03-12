"""
Main entry point for the Mouser application.

Responsible for:
- Creating the root window
- Setting app geometry and title
- Initializing shared state (e.g., TEMP_FILE_PATH)
- Building menu and welcome screen
- Launching the app loop via root.mainloop()

All UI setup is now modularized under /ui for maintainability.
"""

import os
import sys
import shutil
import tempfile
import serial
import regex
import threading
import atexit
from shared.logger import Logger



# Ensure project root is on sys.path so local packages (e.g. `databases`) can be
# imported when running this script directly from the repo folder or from other
# working directories.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from shared.tk_models import MouserPage, raise_frame  # pylint: disable=wrong-import-position
from shared.serial_port_controller import SerialPortController  # pylint: disable=wrong-import-position
from ui.root_window import create_root_window  # pylint: disable=wrong-import-position
from ui.menu_bar import build_menu  # pylint: disable=wrong-import-position
from ui.welcome_screen import setup_welcome_screen  # pylint: disable=wrong-import-position

SCANNER_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600

def connect_to_scanner(port, baud_rate):
    '''Connect to the scanner via serial port'''
    try:
        scanner = serial.Serial(port, baud_rate, timeout=1)
        Logger.log("ScannerConnection", 0, "ScannerConnectionOK")
        return scanner
    except serial.SerialException as e:
        Logger.log("ScannerConnection", e.errno, "ScannerConnectionFailed")
        sys.exit(1)

def validate_scan(scan):
    '''Validate the scanned data format'''
    return bool(regex.match(r'^\d{12}$', scan))
        
def scan_loop(scanner):
    '''Loop to read scans from the scanner and validate scanner'''
    while True:
        try:
            scan = scanner.readline().decode('utf-8').strip()
            if scan:
                Logger.log("ScanCaptured", 0, "ScanCapturedOK")
                if validate_scan(scan):
                    Logger.log("ScanValidated", 0, "ScanValidatedOK")
                else:
                    Logger.log("InvalidFormat", 0, "InvalidFormatDetected")
        except serial.SerialException as e:
            Logger.log("ScanLoopError", e.errno if hasattr(e, 'errno') else -1, "ScanLoopError")
        except Exception as e:
            Logger.log("ScanLoopError", -1, f"UnexpectedError: {e}")
            
def program_exit_handler(scanner):
    '''Handle program exit and log shutdown'''
    Logger.log("ScannerShutdown", 0, "ScannerShutdownOK")
    if scanner and scanner.is_open:
        scanner.close()

def end_program(scanner):
    '''End the program gracefully'''
    program_exit_handler(scanner)
    sys.exit(0)

# Global app variables
TEMP_FOLDER_NAME = "Mouser"
TEMP_FILE_PATH = None
CURRENT_FILE_PATH = None
PASSWORD = None

# Clear any old Temp folders
temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

# Create root window
root = create_root_window()

# Window size constants
MAINWINDOW_WIDTH = 900
MAINWINDOW_HEIGHT = 600

# Get screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set root window geometry
x_pos = int((screen_width - MAINWINDOW_WIDTH) / 2)
y_pos = int((screen_height - MAINWINDOW_HEIGHT) / 2)
root.geometry(f"{MAINWINDOW_WIDTH}x{MAINWINDOW_HEIGHT}+{x_pos}+{y_pos}")
root.title("Mouser")
root.minsize(MAINWINDOW_WIDTH, MAINWINDOW_HEIGHT)

# Main layout setup
main_frame = MouserPage(root, "Mouser")
rfid_serial_port_controller = SerialPortController("reader")
experiments_frame = setup_welcome_screen(root, main_frame)

# Menu bar setup
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller,
)

# Final grid configuration
raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Start the main event loop
root.mainloop()

if __name__ == "__main__":
    # Connect to scanner
    scanner = connect_to_scanner(SCANNER_PORT, BAUD_RATE)
    atexit.register(program_exit_handler, scanner)

    scan_thread = threading.Thread(
        target=scan_loop,
        args=(scanner,),
        daemon=True
    )
    scan_thread.start()


    root.mainloop()

