'''Now unused select experiment ui'''
from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *
from tk_models import *
from experiment_pages.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment_menu_ui import ExperimentMenuUI


class NewExperimentButton(Button):# pylint: disable= undefined-variable
    '''New Experiment Button widgit'''
    def __init__(self, parent: Tk, page: Frame):
        super().__init__(page, text="Create New Experiment", compound=TOP,
                         width=22, command=lambda: [self.create_next_page(), self.navigate()])
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.parent = parent
        self.page = page

    def create_next_page(self):
        '''Sets next page to be a New Experiment UI page'''
        self.next_page = NewExperimentUI(self.parent, self.page)

    def navigate(self):
        '''Raises next page.'''
        self.next_page.raise_frame()

class ExperimentsUI(MouserPage, ChangeableFrame): # pylint: disable= undefined-variable
    '''Experiment Selection user interface.'''
    def __init__(self, parent:Tk, _: Frame = None):
        super().__init__(parent, "Mouser")
        self.parent = parent

        self.main_frame = Frame(self)
        self.main_frame.place(relx=.12, rely = 0.25, relheight= .75, relwidth= .75)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.selectable_frames = []
        self.update_frame()

    def read_csv(self):
        '''Reads experiment list from csv file.'''
        self.experiment_list = []

    def update_frame(self):
        '''Updates frame.'''
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.read_csv()

        index = 0
        for exp in self.experiment_list:
            index += 1
            name = exp[0]
            date = exp[1]
            self.create_selectable_frame(name, date, index)

    def create_selectable_frame(self, name, date, index):
        '''Creates a selectable from for a given experiment name and date.'''
        selectable_frame = Frame(self.main_frame, borderwidth=3, relief='groove')
        selectable_frame.grid(row=index, column=0, pady=5, sticky='NESW')
        selectable_frame.grid_columnconfigure(0, weight= 1)
        selectable_frame.grid_columnconfigure(1, weight= 1)
        name_label = Label(selectable_frame, text=name, width=30, font=("Arial", 12))
        name_label.grid(row=index, column=0, padx=20, sticky=W)

        date_label = Label(selectable_frame, text=date, font=("Arial", 12))
        date_label.grid(row=index, column=1, padx=15, pady=10)

        selectable_frame.bind("<Enter>", lambda event, arg=selectable_frame: self.frame_hover(event, arg))
        selectable_frame.bind("<Leave>", lambda event, arg=selectable_frame: self.frame_hover_leave(event, arg))

        selectable_frame.bind("<Button-1>", lambda event, arg=name: self.frame_click(event, arg))
        name_label.bind("<Button-1>", lambda event, arg=name: self.frame_click(event, arg))
        date_label.bind("<Button-1>", lambda event, arg=name: self.frame_click(event, arg))

    def frame_hover(self, _, hovered_frame):
        '''On frame hover'''
        hovered_frame['relief'] = 'sunken'

    def frame_hover_leave(self, _, hovered_frame):
        '''On frame hover leave.'''
        hovered_frame['relief'] = 'groove'

    def frame_click(self, _, name):
        '''On frame click'''
        page = ExperimentMenuUI(self.parent, name, self)
        page.tkraise()
