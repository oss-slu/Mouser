from tkinter import *
from tkinter.ttk import *

class NavigateButton(Button):
    def __init__(self, page: Frame, name: str, nextPage: Frame):
        super().__init__(page, text=name, compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.nextPage = nextPage

    def navigate(self):
        self.nextPage.tkraise()
