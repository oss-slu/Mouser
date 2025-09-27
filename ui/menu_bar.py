from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from ui.commands import open_file, create_file, save_file, open_serial_port_setting, open_test

def build_menu(root, experiments_frame, rfid_serial_port_controller):
    menu_bar = CTkMenuBar(root)
    file_menu = menu_bar.add_cascade("File")
    settings_menu = menu_bar.add_cascade("Settings")

    file_dropdown = CustomDropdownMenu(widget=file_menu)
    file_dropdown.add_option(option="New Experiment", command=lambda: create_file(root, experiments_frame))
    file_dropdown.add_option(option="Open Experiment", command=lambda: open_file(root, experiments_frame))
    file_dropdown.add_option(option="Save File", command=save_file)

    settings_dropdown = CustomDropdownMenu(widget=settings_menu)
    settings_dropdown.add_option(option="Serial Port", command=lambda: open_serial_port_setting(rfid_serial_port_controller))
    settings_dropdown.add_option(option="Test Serials", command=lambda: open_test(root))

    root.config(menu=menu_bar)







