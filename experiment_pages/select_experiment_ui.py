from tkinter import *
from tkinter.ttk import *
from tk_models import *
import csv
from experiment_pages.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment_menu_ui import ExperimentMenuUI

class NewExperimentButton(Button):
    def __init__(self, parent: Tk, page: Frame):
        super().__init__(page, text="Create New Experiment", compound=TOP,
                         width=22, command=lambda: [self.create_next_page(), self.navigate()])
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.parent = parent
        self.page = page

    def create_next_page(self):
        self.next_page = NewExperimentUI(self.parent, self.page)

    def navigate(self):
        self.next_page.tkraise()


class ExperimentsUI(MouserPage):
    def __init__(self, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "Experiments", prev_page)
        self.parent = parent

        NewExperimentButton(parent, self)

        self.main_frame = Frame(self, width=500)
        self.main_frame.grid(row=1, column=1, sticky='NESW')
        self.main_frame.place(relx=0.12, rely=0.25)

        self.selectable_frames = []
        self.update_frame()


    def read_csv(self):
        self.experiment_list = []
        with open('./created_experiments.csv', 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                self.experiment_list.append(line)
            f.close()


    def update_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.read_csv()
        Label(self, text='Name').place(relx=0.14, rely=0.2)
        Label(self, text='Date Created').place(relx=0.7, rely=0.2)

        index = 0
        for exp in self.experiment_list:
            index += 1
            name = exp[0]
            date = exp[1]
            self.create_selectable_frame(name, date, index)


    def create_selectable_frame(self, name, date, index):
        frame = Frame(self.main_frame, borderwidth=3, width=500, relief='groove')
        frame.grid(row=index, column=0, pady=5)
        name_label = Label(frame, text=name, width=30, font=("Arial", 12))
        name_label.grid(row=index, column=0, padx=20, sticky=W)
        date_label = Label(frame, text=date, font=("Arial", 12))
        date_label.grid(row=index, column=1, padx=20, pady=10, sticky=E)

        frame.bind("<Enter>", lambda event, arg=frame: self.frame_hover(event, arg))
        frame.bind("<Leave>", lambda event, arg=frame: self.frame_hover_leave(event, arg))

        frame.bind("<Button-1>", lambda event, arg=name: self.frame_click(event, arg))
        name_label.bind("<Button-1>", lambda event, arg=name: self.frame_click(event, arg))
        date_label.bind("<Button-1>", lambda event, arg=name: self.frame_click(event, arg))


    def frame_hover(self, event, frame):
        frame['relief'] = 'sunken'


    def frame_hover_leave(self, event, frame):
        frame['relief'] = 'groove'


    def frame_click(self, event, name):
        page = ExperimentMenuUI(self.parent, name, self)
        page.tkraise()

