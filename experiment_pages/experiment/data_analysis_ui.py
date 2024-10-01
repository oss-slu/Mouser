#pylint: skip-file
'''Page for analying data collected in database files.'''
   
import os
from customtkinter import *
from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase


class DataAnalysisUI(MouserPage):
    '''Data Exporting UI.'''
    def __init__(self, parent: CTk, prev_page: CTkFrame = None, db_file=None):
        super().__init__(parent, "Data Exporting", prev_page)
        self.db_file = db_file  # Accept the database file dynamically
        
        # Create the main frame
        main_frame = CTkFrame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.75)

        # Add a button to export the database to CSV
        self.export_button = CTkButton(main_frame, text="Export Data to CSV", command=self.export_to_csv)
        self.export_button.grid(row=0, column=0, padx=20, pady=20)

    def export_to_csv(self):
        '''Handles exporting the database to CSV files.'''
        if not self.db_file or not os.path.exists(self.db_file):
            print(f"Database file {self.db_file} not found.")
            return

        try:
            db = ExperimentDatabase(self.db_file)
            db.export_all_tables_to_csv()
            print("Data exported successfully to CSV files.")
        except Exception as e:
            print(f"An error occurred while exporting data: {e}")

    def raise_frame(self):
        '''Raise the frame for this UI'''
        super().raise_frame()

