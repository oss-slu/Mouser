from tkinter import *
from tkinter.ttk import *
from tk_models import *
from experiment_pages.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment_menu_ui import ExperimentMenuUI

experiment_list = {
    'Experiment 1': '10/31/22', 
    'Experiment 2': '11/11/22', 
    'Experiment 3': '02/22/22', 
    'Experiment 4': '10/02/22'
}


class NewExperimentButton(Button):
    def __init__(self, page: Frame, next_page: Frame):
        super().__init__(page, text="Create New Experiment", compound=TOP,
                         width=22, command=lambda: self.navigate())
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.next_page = next_page

    def navigate(self):
        self.next_page.tkraise()


class ExperimentsUI(MouserPage):
    def __init__(self, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "Experiments", prev_page)
        self.parent = parent

        new_exp_frame = NewExperimentUI(parent, self)
        NewExperimentButton(self, new_exp_frame)

        Label(self, text='Name').place(relx=0.14, rely=0.2)
        Label(self, text='Date Created').place(relx=0.7, rely=0.2)

        self.main_frame = Frame(self, width=500)
        self.main_frame.grid(row=1, column=1, sticky='NESW')
        self.main_frame.place(relx=0.12, rely=0.25)

        self.selectable_frames = []

        index = 0
        for exp in experiment_list:
            self.create_selectable_frame(exp, index)
            index += 1


    def create_selectable_frame(self, experiment, index):
        frame = Frame(self.main_frame, borderwidth=3, width=500, relief='groove')
        frame.grid(row=index, column=0, pady=5)
        name = Label(frame, text=experiment, width=30, font=("Arial", 12))
        name.grid(row=index, column=0, padx=20, sticky=W)
        date = Label(frame, text=experiment_list[experiment], font=("Arial", 12))
        date.grid(row=index, column=1, padx=20, pady=10, sticky=E)

        frame.bind("<Enter>", lambda event, arg=frame: self.frame_hover(event, arg))
        frame.bind("<Leave>", lambda event, arg=frame: self.frame_hover_leave(event, arg))

        frame.bind("<Button-1>", lambda event, arg=experiment: self.frame_click(event, arg))
        name.bind("<Button-1>", lambda event, arg=experiment: self.frame_click(event, arg))
        date.bind("<Button-1>", lambda event, arg=experiment: self.frame_click(event, arg))


    def frame_hover(self, event, frame):
        frame['relief'] = 'sunken'


    def frame_hover_leave(self, event, frame):
        frame['relief'] = 'groove'


    def frame_click(self, event, experiment):
        page = ExperimentMenuUI(self.parent, experiment, self)
        page.tkraise()
