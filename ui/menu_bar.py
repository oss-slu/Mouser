"""
Builds the application menu bar using CTkMenuBar with a modern aesthetic.
Applies consistent spacing, readable fonts, and clear visual grouping.
"""

from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from ui.commands import open_file, create_file, save_file, open_serial_port_setting, open_test


def build_menu(root, experiments_frame, rfid_serial_port_controller):
    """Constructs the main menu bar with modern CTk styling."""
    menu_bar = CTkMenuBar(root)
    menu_bar.configure(bg_color="#1e1e1e")

    # --- File Menu ---
    file_menu = menu_bar.add_cascade("File")
    file_dropdown = CustomDropdownMenu(widget=file_menu)
    file_dropdown.add_option("New Experiment", lambda: create_file(root, experiments_frame))
    file_dropdown.add_option("Open Experiment", lambda: open_file(root, experiments_frame))
    file_dropdown.add_option("Save File", save_file)

    # --- Settings Menu ---
    settings_menu = menu_bar.add_cascade("Settings")
    settings_dropdown = CustomDropdownMenu(widget=settings_menu)
    settings_dropdown.add_option("Serial Port", lambda: open_serial_port_setting(rfid_serial_port_controller))
    settings_dropdown.add_option("Test Serials", lambda: open_test(root))

    # Inline note: menu_bar styling inherits global CTk theme
    root.config(menu=menu_bar)
