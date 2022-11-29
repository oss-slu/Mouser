from tkinter import *
from tkinter.ttk import *
from tk_models import *
from experiment_pages.experiment import Experiment


class CreateExperimentButton(Button):
    def __init__(self, experiment: Experiment, page: Frame, menu_page: Frame):
        super().__init__(page, text="Create", compound=TOP,
                         width=15, command=lambda: [menu_page.update_frame(), experiment.save_to_database(), self.navigate()])
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.next_page = menu_page

    def navigate(self):
        self.next_page.tkraise()


class SummaryUI(MouserPage):
    def __init__(self, input: Experiment, parent:Tk, prev_page: Frame, menu_page: Frame):
        super().__init__(parent, "New Experiment - Summary", prev_page)
        
        self.input = input
        self.prev_page = prev_page

        CreateExperimentButton(input, self, menu_page)

        self.main_frame = Frame(self)
        self.main_frame.grid(row=8, column=1, sticky='NESW')
        self.main_frame.place(relx=0.38, rely=0.20)

        self.group_frame = Frame(self.main_frame)
        self.group_frame.grid(row=5, column=0, padx=10, pady=10, sticky='NESW')


    def update_page(self):
        for widget in self.group_frame.winfo_children():
            widget.destroy()
        self.create_summary_frame() 


    def create_summary_frame(self):
        Label(self.main_frame, text=self.input.get_name()).grid(
                row=0, column=0, padx=10, pady=10)
        Label(self.main_frame, text=self.input.get_species()).grid(
                row=2, column=0, padx=10, pady=10)

        names = ''
        for name in self.input.get_investigators():
            names += name + ', '
        Label(self.main_frame, text=names).grid(row=1, column=0, padx=10, pady=10)

        items = ''
        for item in self.input.get_measurement_items():
            items += item + ', '
        Label(self.main_frame, text=items).grid(row=2, column=0, padx=10, pady=10)

        animals = self.input.get_num_animals() + ' ' + self.input.get_species()
        Label(self.main_frame, text=animals).grid(row=3, column=0, padx=10, pady=10)

        cage = self.input.get_max_animals() + ' per Cage'
        Label(self.main_frame, text=cage).grid(row=4, column=0, padx=10, pady=10)

        groups = self.input.get_group_names()
        index = 0
        for group in groups:
            Label(self.group_frame, text=group).grid(row=index, column=0, padx=10, pady=10)
            index += 1

        rfid = self.input.uses_rfid()
        if rfid == True:
            Label(self.main_frame, text='Uses RFID').grid(row=6, column=0, padx=10, pady=10)
        else:
            Label(self.main_frame, text='Does Not Use RFID').grid(row=6, column=0, padx=10, pady=10)


    def create_experiment(self):
        self.input.save_to_database()
        self.prev_page.destroy()

