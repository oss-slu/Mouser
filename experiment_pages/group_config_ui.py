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
        self.main_frame.grid(row=2, column=1, sticky='NESW')
        self.main_frame.place(relx=0.27, rely=0.20)

        self.group_frame = Frame(self.main_frame)
        self.item_frame = Frame(self.main_frame)

        self.group_frame.grid(row=0, column=0, sticky='NESW')
        self.item_frame.grid(row=1, column=0, sticky='NESW')

        self.create_group_entries(int(self.input.get_num_groups()))
        self.create_item_frame(self.input.get_measurement_items())

        for i in range(0,2):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)


    def set_next_button(self, next_page):
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)
        self.next_button.configure(command= lambda: [self.save_input(), self.next_button.navigate()])
        self.next_button.place(relx=0.85, rely=0.15)


    def create_group_entries(self, num):
        Label(self.group_frame, text="Group Name").grid(row=0, column=0, padx=10, pady=10)
        self.group_input = []
        for i in range(0, num):
            name = Entry(self.group_frame, width = 40)
            name.grid(row=i+1, column=0, padx=10, pady=10)
            self.group_input.append(name)

    
    def create_item_frame(self, items):
        self.button_vars = [] 
        self.item_auto_buttons = []
        self.item_man_buttons = []
        for i in range(0, len(items)):
            self.type = StringVar()
            self.button_vars.append(self.type)
            
            Label(self.item_frame, text=items[i]).grid(row=i, column=0, padx=10, pady=10, sticky=W)
            auto = Radiobutton(self.item_frame, text='Automatic', variable=self.type, val='automatic')
            man = Radiobutton(self.item_frame, text='Manual', variable=self.type, val='manual')
            
            auto.grid(row=i, column=1, padx=10, pady=10)
            man.grid(row=i, column=2, padx=10, pady=10)

            self.item_auto_buttons.append(auto)
            self.item_man_buttons.append(man)



    def update_page(self):
        for widget in self.group_frame.winfo_children():
            widget.destroy()
        for widget in self.item_frame.winfo_children():
            widget.destroy()
        self.create_group_entries(int(self.input.get_num_groups()))
        self.create_item_frame(self.input.get_measurement_items())


    def save_input(self):
        for entry in self.group_input:
            self.group_names.append(entry.get())
            self.input.group_names = self.group_names
            
        for var in self.button_vars:
            self.input.item_collect_type.append(var)
            