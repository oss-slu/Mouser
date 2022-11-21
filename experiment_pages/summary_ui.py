from tkinter import *
from tkinter.ttk import *
from tk_models import *
from experiment_pages.experiment import Experiment


class SummaryUI(MouserPage):
    def __init__(self, input: Experiment, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "New Experiment - Summary", prev_page)
        
        self.input = input

        self.main_frame = Frame(self)

    
    def update_page(self):
        pass
