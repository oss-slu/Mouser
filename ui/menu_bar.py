"""
Builds the application menu bar using CTkMenuBar with a modern aesthetic.
Applies consistent spacing, readable fonts, and clear visual grouping.
"""

from CTkMenuBar import CTkMenuBar, CustomDropdownMenu
from ui.commands import open_file, create_file, save_file, open_serial_port_setting, open_test


def build_menu(root, experiments_frame, rfid_serial_port_controller):
    """Constructs the main menu bar with modern CTk styling."""
    menu_bar = CTkMenuBar(
        root,
        bg_color=("#f8fafc", "#111827"),
        height=30,
        padx=8,
        pady=3
    )

    # --- Single Menu (replaces File/Settings) ---
    app_menu = menu_bar.add_cascade(
        "Menu",
        fg_color=("#e2e8f0", "#1f2937"),
        hover_color=("#cbd5e1", "#374151"),
        text_color=("#0f172a", "#f9fafb"),
        corner_radius=8
    )
    app_dropdown = CustomDropdownMenu(
        widget=app_menu,
        bg_color=("#ffffff", "#0f172a"),
        fg_color=("#ffffff", "#0f172a"),
        border_color=("#cbd5e1", "#374151"),
        separator_color=("#e5e7eb", "#1f2937"),
        text_color=("#0f172a", "#f9fafb"),
        hover_color=("#e2e8f0", "#1f2937")
    )
    app_dropdown.add_option("New Experiment", lambda: create_file(root, experiments_frame))
    app_dropdown.add_option("Open Experiment", lambda: open_file(root, experiments_frame))
    app_dropdown.add_option("Save File", save_file)
    app_dropdown.add_option("Serial Port Settings", lambda: open_serial_port_setting(rfid_serial_port_controller))
    app_dropdown.add_option("Equipment Testing", lambda: open_test(root))

    # Inline note: menu_bar styling inherits global CTk theme
    root.config(menu=menu_bar)
