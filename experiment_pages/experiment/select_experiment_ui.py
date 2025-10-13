'''Now unused select experiment ui'''
from customtkinter import *
from shared.tk_models import MouserPage
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI

class NewExperimentButton(CTkButton):
    '''New Experiment Button widgit'''
    def __init__(self, parent: CTk, page: CTkFrame):
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

class ExperimentsUI(MouserPage):
    '''Experiments UI'''
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Mouser")
        self.previous = prev_page
        self.parent = parent
