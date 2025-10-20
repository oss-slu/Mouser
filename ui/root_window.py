"""
Initializes and returns the main Tkinter application window (root) with modern CTk theming.
Applies global light/dark/system theme support and platform-specific scaling adjustments.
"""

import tkinter.font as tkFont
from customtkinter import CTk, set_appearance_mode, set_default_color_theme


def create_root_window():
    """Creates and returns the CTk root window with global theming and scaling."""
    # Configure global CTk appearance
    set_appearance_mode("System")
    set_default_color_theme("dark-blue")

    root = CTk()
    root.title("Mouser")

    # macOS Retina scaling adjustment
    if root.tk.call("tk", "windowingsystem") == "aqua":
        scale_factor = 2
        root.tk.call("tk", "scaling", scale_factor)

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=int(default_font.cget("size") * scale_factor))

    # Add window padding for aesthetic margins
    root.configure(padx=10, pady=10)
    return root
