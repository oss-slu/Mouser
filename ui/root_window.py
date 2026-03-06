"""
Initializes and returns the main Tkinter application window (root) with modern CTk theming.
Applies global light/dark/system theme support and platform-specific scaling adjustments.
"""
import platform
import tkinter.font as tkFont
from customtkinter import (
    CTk,
    set_appearance_mode,
    set_default_color_theme,
    set_widget_scaling,
    set_window_scaling,
)

BASE_W, BASE_H = 1000, 720  

def _center_on_screen(root, w, h):
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = max((sw - w) // 2, 0)
    y = max((sh - h) // 2, 0)
    root.geometry(f"{w}x{h}+{x}+{y}")

def create_root_window():
    """Creates and returns the CTk root window with global theming and scaling."""
    # Configure global CTk appearance
    # macOS dark mode can produce low-contrast black-on-black controls in some third-party CTk widgets.
    # Use Light on macOS for consistent readability; keep System elsewhere.
    if platform.system() == "Darwin":
        set_appearance_mode("Light")
        # Improve readability on high-DPI macOS displays.
        set_widget_scaling(1.25)
        set_window_scaling(1.1)
    else:
        set_appearance_mode("System")
        set_widget_scaling(1.0)
        set_window_scaling(1.0)
    set_default_color_theme("dark-blue")

    root = CTk()
    root.title("Mouser")

    # macOS Retina scaling adjustment
    if root.tk.call("tk", "windowingsystem") == "aqua":
        scale_factor = 2
        root.tk.call("tk", "scaling", scale_factor)

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=int(default_font.cget("size") * scale_factor))

    
    # Platform-specific window sizing: Linux
    w, h = BASE_W, BASE_H
    if platform.system() == "Linux":
        w += 50
        h += 50 

    _center_on_screen(root, w, h)
    root.minsize(w, h)



    # Add window padding for aesthetic margins
    root.configure(padx=10, pady=10)
    return root
