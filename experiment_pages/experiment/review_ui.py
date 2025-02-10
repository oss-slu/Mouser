from databases.experiment_database import ExperimentDatabase
from experiment_pages.create_experiment.summary_ui import *

class ReviewSummaryUI(SummaryUI):
    '''Summary User Interface for the review page (without the create button).'''
    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):
        # Override the parent's title by calling MouserPage's init directly
        MouserPage.__init__(self, parent, "Review Experiment - Summary", prev_page)
        
        self.database = ExperimentDatabase(experiment)

        # Print the name to console
        print("Experiment name:", self.database.get_name())

        # Skip the CreateExperimentButton that's in SummaryUI
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.10, rely=0.25, relheight=0.7, relwidth=0.8)

        self.main_frame = CTkFrame(scroll_canvas)
        self.main_frame.pack(side=LEFT, expand=True)

        # Example usage with getter
        name_label = CTkLabel(
            self.main_frame,
            text=f"Experiment name: {self.database.get_name()}"
        )
        name_label.pack(pady=20) 

class ReviewUI(MouserPage):
    '''Review User Interface for experiment summary.'''
    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):
        super().__init__(parent, "Review Experiment - Summary", prev_page)
        
        self.input = experiment
        self.menu = menu_page

        # Use ReviewSummaryUI for the review page
        self.summary_ui = ReviewSummaryUI(experiment, self, prev_page, menu_page)
        
        # Add the summary UI to the grid layout of ReviewUI
        self.summary_ui.grid(row=0, column=0, sticky="nsew")
