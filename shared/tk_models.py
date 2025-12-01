'''Contains shared tkinter models used througout the program.'''
import os
import sys
from tkinter import PhotoImage
from abc import ABC, abstractmethod
import sqlite3

from customtkinter import *

CURRENT_FRAME: CTkFrame = None

# pylint: disable=no-member, protected-access, useless-parent-delegation,
# pylint: disable=unused-argument, unused-variable, global-statement

def get_resource_path(relative_path):
    """
    Returns an absolute path to a resource (image, file, etc.).
    Works for both development and when using PyInstaller.
    """
    try:
        # When bundled with PyInstaller this attribute points to the
        # unpacked temp folder (e.g. _MEIxxxxx). Use it when available.
        base_path = sys._MEIPASS
    except sqlite3.Error:
        # Fallback to the working directory when running normally.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def raise_frame(frame: CTkFrame): #pylint: disable= redefined-outer-name
    '''Raises passed frame.'''
    global CURRENT_FRAME
    if CURRENT_FRAME:
        CURRENT_FRAME.pack_forget()
    CURRENT_FRAME = frame
    CURRENT_FRAME.pack()


def create_nav_button(parent: CTkFrame, name: str, button_image: PhotoImage, frame: CTkFrame, relx: float, rely: float): #pylint: disable= line-too-long,redefined-outer-name
    '''Makes a navigation button to the various sub-menus of the program.'''

    button = CTkButton(parent, text=name, image=button_image,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image

class MouserPage(CTkFrame):

    '''Standard pageframe used throughout the program.'''
    def __init__(self, root: CTk, title: str, menu_page: CTkFrame = None):
        super().__init__(root)

        self.root = root
        self.title = title

        self.canvas = CTkCanvas(self, width=600, height=600)
        self.canvas.grid(row=0, column=0, columnspan=4)

        self.rectangle = self.canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        self.title_label = self.canvas.create_text(300, 13, anchor="n")
        self.canvas.itemconfig(self.title_label, text=title, font=("Arial", 18))

        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)

        self.menu_button = None
        self.next_button = None
        self.previous_button = None

        if menu_page:
            self.menu_button = MenuButton(self, menu_page)

        self.check_window_size()

        # --- Pylint Stubs (to satisfy E1101, real versions exist in subclasses) ---
        def check_window_size(self):
            """Pylint stub — implemented in actual UI pages."""
            pass

        def set_next_button(self, next_page):
            """Pylint stub — implemented in actual UI pages."""
            pass

        def set_previous_button(self, prev_page):
            """Pylint stub — implemented in actual UI pages."""
            pass

        def raise_frame(self):
            """Pylint stub — real implementation provided externally."""
            raise_frame(self)



class ChangeableFrame(ABC, CTkFrame):
    '''Abstract class.'''
    @abstractmethod
    def update_frame(self):
        '''Abstract update_frame.'''
        pass # pylint: disable= unnecessary-pass

class SettingPage(CTkToplevel):
    '''Initializes the SettingPage.'''
    def __init__(self, title: str):
        super().__init__()
        # Selecting GUI theme - dark,
        # light , system (for system default, useful if we need dark mode later on)
        set_appearance_mode("light")
        # Selecting color theme-blue, green, dark-blue
        set_default_color_theme("dark-blue")
        self.title(title)
        self.geometry("700x600")

class MenuButton(CTkButton):
    '''A standard button that navigates backwards in the program.'''
    def __init__(self, page: CTkFrame, previous_page: MouserPage):

        super().__init__(page, text="Back to Menu", compound=TOP,
                         width=250, height=75, font=("Georgia", 65), command = self.navigate)
        self.place(relx=0.15, rely=0.15, anchor=CENTER)
        self.previous_page = previous_page



    def navigate(self):
        '''Raises the previous_page in the stacking order.'''
        #raise_frame(self.previous_page)
        self.previous_page.raise_frame()

class ChangePageButton(CTkButton):
    '''A standard button that navigates somewhere else in the program.'''
    def __init__(self, page: CTkFrame, next_page: MouserPage, previous: bool = True):
        text = "Next"
        x = 0.75
        if previous:
            text = "Previous"
            x = 0.25
        super().__init__(page, text=text, compound=TOP,
                         width=15, command = self.navigate)
        self.place(relx=x, rely=0.85, anchor=CENTER)
        self.next_page = next_page

    def navigate(self):
        '''Raises the next_page in the stacking order.'''
        #raise_frame(self.next_page)
        self.next_page.raise_frame()

if __name__ == '__main__':
    app = CTk()
    app.title("Template Test")
    app.geometry('600x600')

    main_frame = MouserPage(app, "Main")
    frame = MouserPage(app, "Template")

    main_frame.set_next_button(frame)
    frame.set_previous_button(frame)

    main_frame.raise_frame()

    app.grid_rowconfigure(0, weight=1)
    app.grid_columnconfigure(0, weight=1)

    app.mainloop()

