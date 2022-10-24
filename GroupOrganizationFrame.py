from tkinter import *
from tkinter.ttk import *
from NavigateButton import *
from CageSetupFrame import CageSetupFrame

groups = {'group 1', 'group 2', 'group 3'}

class GroupOrganizationFrame(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None):
        super().__init__(parent)

        self.root = parent
        self.pad_x = 10
        self.pad_y = 20
        self.label_font = ("Arial", 13)

        self.grid(row=4, column=6, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=3, padx=self.pad_x, pady=self.pad_y)

        prev_button = NavigateButton(self, 'Previous', prev_page)
        next_button = Button(self, text='Next', width=15, command=lambda: self.create_next(self))
        prev_button.grid(row=4, column=0, columnspan=1, padx=self.pad_x, pady=self.pad_y, sticky=W)
        next_button.grid(row=4, column=5, columnspan=1, padx=self.pad_x, pady=self.pad_y, sticky=E)
        


    def raise_frame(frame: Frame):
        frame.tkraise()

    def create_next(self, frame: Frame):
        next = CageSetupFrame(self.root, frame)
        next.grid(row=0, column=0)

    def drag_group(self, groups):
        for i in groups:
            Label()

