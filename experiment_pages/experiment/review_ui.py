from experiment_pages.create_experiment.summary_ui import *

class ReviewSummaryUI(SummaryUI):
    '''Summary User Interface for the review page (without the create button).'''
    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):
        # Override the parent's title by calling MouserPage's init directly
        MouserPage.__init__(self, parent, "Review Experiment - Summary", prev_page)
        
        self.input = experiment
        self.menu = menu_page

        # Skip the CreateExperimentButton that's in SummaryUI
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.10, rely=0.25, relheight=0.7, relwidth=0.8)

        self.main_frame = CTkFrame(scroll_canvas)
        self.main_frame.pack(side=LEFT, expand=True)

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

        # Configure the grid so it expands properly
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def go_back(self):
        # Logic to go back to the previous page
        pass

    def update_page(self):
        '''Update the review page if necessary.'''
        self.summary_ui.update_page()  # Update the summary UI when needed
