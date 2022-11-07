from tkinter import *
from tkinter.ttk import *

class MouserPage(Frame):
    def __init__(self, parent: Tk, title: str, backButton: bool, nextButton: bool, font=("Arial", 25)):
        super().__init__(parent)
        self.title = title
        titleLabel = Label(self, text=title, font=font)
        titleLabel.grid(row=0, column=0, columnspan=4, sticky=N)
        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


    def raise_frame(self):
        self.tkraise()