#pylint: skip-file
from databases.experiment_database import ExperimentDatabase
from shared.tk_models import *

class ReviewUI(MouserPage):
    '''Review User Interface for experiment summary.'''
    def __init__(self, parent: CTk, prev_page: CTkFrame, database_name: str = ""):
        super().__init__(parent, "Review Experiment - Summary", prev_page)
        
        self.database = ExperimentDatabase(database_name)

        self.main_frame = CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, sticky='NESW')
        self.main_frame.place(relx=0.5, rely=0.5, anchor=CENTER) #pylint: disable = undefined-variable

        # Example usage with getter
        name_label = CTkLabel(
            self.main_frame,
            text=f"Experiment name: {self.database.get_name()}",
        )
        name_label.place(relx=0.5, rely=0.1, anchor=CENTER) #pylint: disable = undefined-variable

        # Adding additional text
        additional_text_label = CTkLabel(
            self.main_frame,
            text="Additional information goes here."
        )
        additional_text_label.place(relx=0.5, rely=0.2, anchor=CENTER) #pylint: disable = undefined-variable
