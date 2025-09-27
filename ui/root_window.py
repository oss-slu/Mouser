import os
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