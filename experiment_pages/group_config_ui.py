from tkinter import *
from tkinter.ttk import *
from tk_models import *
from experiment_pages.summary_ui import SummaryUI
from experiment_pages.experiment import Experiment

class GroupConfigUI(MouserPage):
    def __init__(self, input: Experiment, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "New Experiment - Group Configuration", prev_page)

        self.input = input
        self.group_names = []

        self.set_next_button(SummaryUI(self.input, parent, self))
        self.main_frame = Frame(self)
        self.main_frame.grid(row=3, column=3, sticky='NESW')
        self.main_frame.place(relx=0.12, rely=0.20)

        self.group_frame = Frame(self.main_frame)
        self.group_frame.grid(row=0, column=0, columnspan=3, sticky='NESW')

        Label(self.group_frame, text="Group Name").grid(row=0, column=0, padx=10, pady=10)
        Label (self.group_frame, text="Animals\nPer Group").grid(row=0, column=1, padx=10, pady=10)

        self.group_input = []
        for i in range(1, int(self.input.get_num_groups())):
            name = Entry(self.group_frame, width = 40)
            name.grid(row=i, column=0, padx=10, pady=5)
            self.group_input.append(name)


    def set_next_button(self, next_page):
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)
        self.next_button.configure(command= lambda: [self.save_input(), self.next_button.navigate()])
        self.next_button.place(relx=0.85, rely=0.15)


    def save_input(self):
        for entry in self.group_input:
            self.group_names.append(entry.get())
            self.input.group_names = self.group_names
            