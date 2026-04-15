'''Contains shared tkinter models used througout the program.'''
import os
import sys
import platform
from tkinter import PhotoImage
from abc import ABC, abstractmethod
from customtkinter import *

current_frame: CTkFrame = None

# Shared default palette derived from experiment_pages/create_experiment/new_experiment_ui.py
DEFAULT_PAGE_BG = ("#f8fafc", "#0b1220")
DEFAULT_HEADER_COLOR = "#0f172a"
DEFAULT_TEXT_MUTED = ("#64748b", "#94a3b8")
DEFAULT_CARD_BORDER = ("#e2e8f0", "#223044")
DEFAULT_ENTRY_BG = ("#ffffff", "#0b1220")
DEFAULT_ENTRY_BORDER = ("#cbd5e1", "#334155")
DEFAULT_ACCENT_BLUE = "#3b82f6"
DEFAULT_ACCENT_VIOLET = "#8b5cf6"
DEFAULT_ACCENT_TEAL = "#14b8a6"
DEFAULT_ACCENT_AMBER = "#f59e0b"
DEFAULT_ACCENT_GREEN = "#22c55e"
DEFAULT_DANGER = "#ef4444"
DEFAULT_ICON_LEFT = "\u2B05"
DEFAULT_ICON_RIGHT = "\u27A1"


def get_ui_metrics():
    """Return cross-platform UI sizing values to keep layouts consistent."""
    system = platform.system()
    if system == "Darwin":
        return {
            "nav_width": 180,
            "nav_height": 50,
            "nav_font_size": 18,
            "action_width": 220,
            "action_height": 54,
            "action_font_size": 18,
            "table_font_size": 20,
            "table_row_height": 34,
            "label_font_size": 22,
        }
    if system == "Windows":
        return {
            "nav_width": 180,
            "nav_height": 48,
            "nav_font_size": 16,
            "action_width": 205,
            "action_height": 50,
            "action_font_size": 16,
            "table_font_size": 16,
            "table_row_height": 30,
            "label_font_size": 16,
        }
    return {
        "nav_width": 170,
        "nav_height": 46,
        "nav_font_size": 15,
        "action_width": 200,
        "action_height": 48,
        "action_font_size": 15,
        "table_font_size": 15,
        "table_row_height": 28,
        "label_font_size": 15,
    }

def get_resource_path(relative_path):
    """
    Returns an absolute path to a resource (image, file, etc.).
    Works for both development and when using PyInstaller.
    """
    try:
        # When bundled with PyInstaller this attribute points to the
        # unpacked temp folder (e.g. _MEIxxxxx). Use it when available.
        base_path = sys._MEIPASS
    except Exception:
        # Fallback to the working directory when running normally.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def raise_frame(frame: CTkFrame): #pylint: disable= redefined-outer-name
    '''Raises passed frame.'''
    global current_frame #pylint: disable = global-statement
    if current_frame:
        current_frame.pack_forget()
    current_frame = frame
    current_frame.pack()
   
def create_nav_button(parent: CTkFrame, name: str, button_image: PhotoImage, frame: CTkFrame, relx: float, rely: float): #pylint: disable= line-too-long,redefined-outer-name
    '''Makes a navigation button to the various sub-menus of the program.'''

    button = CTkButton(parent, text=name, image=button_image,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image

class MouserPage(CTkFrame):

    '''Standard page frame used throughout the program without a default header.'''
    def __init__(self, parent: CTk, title: str, menu_page: CTkFrame = None):
        super().__init__(parent)
        self.root = parent
        self.title = title

        self.configure(fg_color=DEFAULT_PAGE_BG)
        default_bg = DEFAULT_PAGE_BG[0] if get_appearance_mode().lower() != "dark" else DEFAULT_PAGE_BG[1]
        self.canvas = CTkCanvas(self, width=600, height=600, highlightthickness=0, bg=default_bg)
        self.canvas.grid(row=0, column=0, columnspan=4, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)

        self.menu_button = None
        self.next_button = None
        self.previous_button = None

        if menu_page:
            self.menu_button = MenuButton(self, menu_page)

        self.check_window_size()

    def raise_frame(self):
        '''Raises the page frame in the stacking order.'''
        raise_frame(self)

    def set_next_button(self, next_page):

        '''Sets next_button to be a ChangePageButton that navigates to next_page.'''
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)

    def set_previous_button(self, previous_page):
        '''Sets previous_button to be a ChangePageButton that navigates to previous_page.'''
        if self.previous_button:
            self.previous_button.destroy()
        self.previous_button = ChangePageButton(self, previous_page, True)

    def set_menu_button(self, menu_page):
        '''Sets menu_button to be a ChangePageButton that navigates to menu_page.'''
        if self.menu_button:
            self.menu_button.destroy()
        self.menu_button = MenuButton(self, menu_page)

    def check_window_size(self):
        '''Checks to see if the window size and page size match.If they don't, resizes the page to match'''
        window = self.winfo_toplevel()
        if window.winfo_height() != self.canvas.winfo_height():
            self.resize_canvas_height(window.winfo_height())
        if window.winfo_width() != self.canvas.winfo_width():
            self.resize_canvas_width(window.winfo_width())

        self.after(10, self.check_window_size)

    def resize_canvas_height(self, root_height):
        '''Resizes page height.'''
        self.canvas.config(height=root_height)

    def resize_canvas_width(self, root_width):
        '''Resizes page width.'''
        self.canvas.config(width=root_width)

        if hasattr(self, "rectangle"):
            self.canvas.coords(self.rectangle, 0, 0, root_width, 50)
        if hasattr(self, "title_label"):
            self.canvas.coords(self.title_label, (root_width/2), 13)


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
        metrics = get_ui_metrics()
        icon_font = CTkFont("Segoe UI Symbol", metrics["nav_font_size"] + 4)
        icon_size = max(metrics["nav_height"], 48)

        super().__init__(page, text=DEFAULT_ICON_LEFT, compound=TOP,
                         width=icon_size, height=icon_size,
                         font=icon_font, command=self.navigate,
                         corner_radius=icon_size // 2, text_color="white",
                         fg_color=DEFAULT_ACCENT_AMBER, hover_color="#d97706")
        self.place(relx=0.15, rely=0.15, anchor=CENTER)
        self.previous_page = previous_page



    def navigate(self):
        '''Raises the previous_page in the stacking order.'''
        #raise_frame(self.previous_page)
        self.previous_page.raise_frame()

class ChangePageButton(CTkButton):
    '''A standard button that navigates somewhere else in the program.'''
    def __init__(self, page: CTkFrame, next_page: MouserPage, previous: bool = True):
        metrics = get_ui_metrics()
        icon_font = CTkFont("Segoe UI Symbol", metrics["nav_font_size"] + 4)
        icon_text = DEFAULT_ICON_LEFT if previous else DEFAULT_ICON_RIGHT
        x = 0.25 if previous else 0.75
        button_color = DEFAULT_ACCENT_AMBER if previous else DEFAULT_ACCENT_BLUE
        hover_color = "#d97706" if previous else "#2563eb"

        super().__init__(page, text=icon_text, compound=TOP,
                         width=80, height=48,
                         font=icon_font, command=self.navigate,
                         corner_radius=24, text_color="white",
                         fg_color=button_color, hover_color=hover_color)
        self.place(relx=x, rely=0.85, anchor=CENTER)
        self.next_page = next_page

    def navigate(self):
        '''Raises the next_page in the stacking order.'''
        #raise_frame(self.next_page)
        self.next_page.raise_frame()

if __name__ == '__main__':
    root = CTk()
    root.title("Template Test")
    root.geometry('600x600')

    main_frame = MouserPage(root, "Main")
    frame = MouserPage(root, "Template")

    main_frame.set_next_button(frame)
    frame.set_previous_button(frame)

    main_frame.raise_frame()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
