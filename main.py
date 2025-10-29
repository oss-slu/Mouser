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
import shutil
import tempfile
import threading

from version import __version__
from shared.tk_models import MouserPage, raise_frame
from shared.serial_port_controller import SerialPortController
from shared.auto_updater import AutoUpdater
from shared.config import get_config
from ui.root_window import create_root_window
from ui.menu_bar import build_menu
from ui.welcome_screen import setup_welcome_screen


def check_for_updates_on_startup():
    """
    Check for updates in background thread on app startup.
    
    If auto-update is enabled in config, will automatically:
    1. Check for updates
    2. Download update
    3. Install and restart
    
    If auto-update is disabled, will only notify user.
    """
    try:
        config = get_config()
        
        # Check if auto-update is enabled
        if not config.get_auto_update_enabled():
            return  # Auto-update disabled, skip check
        
        updater = AutoUpdater()
        
        # Check for updates
        if updater.check_for_updates():
            latest_version = updater.get_latest_version()
            print(f"\n{'='*60}")
            print(f"UPDATE AVAILABLE: Version {latest_version}")
            print(f"Current version: {__version__}")
            
            # Auto-download if enabled
            if config.get_auto_download_enabled():
                print("Downloading update...")
                
                def progress_callback(downloaded, total):
                    percent = (downloaded / total) * 100
                    if int(percent) % 10 == 0:  # Print every 10%
                        print(f"  Download progress: {percent:.0f}%")
                
                if updater.download_update(progress_callback):
                    print("Download complete!")
                    
                    # Auto-install if enabled
                    if config.get_auto_install_enabled():
                        print("Installing update and restarting...")
                        print(f"{'='*60}\n")
                        updater.install_update()  # This will restart the app
                    else:
                        print("Auto-install disabled. Update downloaded to temp folder.")
                        print(f"{'='*60}\n")
                else:
                    print("Download failed.")
                    print(f"{'='*60}\n")
            else:
                print("Auto-download disabled.")
                print(f"Download from: https://github.com/oss-slu/Mouser/releases")
                print(f"{'='*60}\n")
        
    except Exception as e:
        # Silently fail - don't interrupt app startup
        print(f"Note: Could not check for updates ({e})")


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

# Get screen width and height
mainwindow_width = 900
mainwindow_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set root window geometry
x = int((screen_width - mainwindow_width) / 2)
y = int((screen_height - mainwindow_height) / 2)
root.geometry(f"{mainwindow_width}x{mainwindow_height}+{x}+{y}")
root.title(f"Mouser v{__version__}")
root.minsize(mainwindow_width, mainwindow_height)

# Main layout setup
main_frame = MouserPage(root, "Mouser")
rfid_serial_port_controller = SerialPortController("reader")
experiments_frame = setup_welcome_screen(root, main_frame)

# Menu bar setup
build_menu(
    root=root,
    experiments_frame=experiments_frame,
    rfid_serial_port_controller=rfid_serial_port_controller
)

# Final grid configuration
raise_frame(experiments_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

# Check for updates in background thread (non-blocking)
update_thread = threading.Thread(target=check_for_updates_on_startup, daemon=True)
update_thread.start()

# Start the main event loop
root.mainloop()



