"""
Initializes and returns the main Tkinter application window (root).
Includes platform-specific scaling (e.g., macOS Retina support) and 
default font resizing for consistent cross-platform appearance.
Extracted from main.py to isolate root window logic.
"""

import tkinter.font as tkFont
from customtkinter import CTk


def create_root_window():
    root = CTk()

    if root.tk.call('tk', 'windowingsystem') == 'aqua':
        # macOS scaling fix
        scale_factor = 2
        root.tk.call('tk', 'scaling', scale_factor)

        default_font = tkFont.nametofont("TkDefaultFont")
        current_size = default_font.cget("size")
        default_font.configure(size=int(current_size * scale_factor))

    return root

