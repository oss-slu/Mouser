
from experiment_pages.create_experiment.summary_ui import SummaryUI
from customtkinter import *
from tkinter import filedialog
from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase
from shared.experiment import Experiment

class ReviewUI(MouserPage):
    '''Review User Interface for experiment summary.'''
    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):
        super().__init__(parent, "Review Experiment - Summary", prev_page)
        
        self.input = experiment
        self.menu = menu_page

        # Create the SummaryUI
        self.summary_ui = SummaryUI(experiment, self, prev_page, menu_page)
        
        #return to menu button
        review_button = CTkButton(self, text="Back to Menu", command=self.go_back)
        review_button.place(relx=0.5, rely=0.9, anchor="center")

    def go_back(self):
        # Logic to go back to the previous page
        pass

    def update_page(self):
        '''Update the review page if necessary.'''
        self.summary_ui.update_page()  # Update the summary UI when needed
