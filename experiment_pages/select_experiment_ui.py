from customtkinter import *
from tk_models import *
from scrollable_frame import ScrolledFrame
import csv
from experiment_pages.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment_menu_ui import ExperimentMenuUI

class NewExperimentButton(CTkButton):
    def __init__(self, parent: CTk, page: CTkFrame):
        super().__init__(page, text="Create New Experiment", compound=TOP,
                         width=22, command=lambda: [self.create_next_page(), self.navigate()])
        self.place(relx=0.85, rely=0.15, anchor=CENTER)
        self.parent = parent
        self.page = page

    def create_next_page(self):
        self.next_page = NewExperimentUI(self.parent, self.page)

    def navigate(self):
        self.next_page.raise_frame()


class ExperimentsUI(MouserPage):
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Mouser")
        self.parent = parent
