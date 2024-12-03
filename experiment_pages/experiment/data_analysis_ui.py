#pylint: skip-file
'''Page for analyzing data collected in database files.'''

import os
from customtkinter import *
from tkinter import filedialog
from shared.tk_models import *
from databases.experiment_database import ExperimentDatabase


class DataAnalysisUI(MouserPage):
    '''Data Exporting UI.'''
    def __init__(self, parent: CTk, prev_page: CTkFrame = None, db_file=None):
        super().__init__(parent, "Data Exporting", prev_page)
        self.db_file = db_file  # Accept the database file dynamically
        
        # Create the main frame
        main_frame = CTkFrame(self, corner_radius=15)
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.place(relx=0.3, rely=0.2, relwidth=0.4, relheight=0.75)

        # Add a title label
        title_label = CTkLabel(
            main_frame, 
            text="Data Analysis & Export", 
            font=("Arial", 22, "bold"),  # Larger font for clarity
            pady=20
        )
        title_label.grid(row=0, column=0, padx=20, pady=20)

        # Add a button to export the database to CSV
        self.export_button = CTkButton(
            main_frame, 
            text="Export Data to CSV", 
            command=self.export_to_csv, 
            width=200, 
            height=75, 
            font=("Arial", 20)
        )
        self.export_button.grid(row=1, column=0, padx=20, pady=30)  # Adjust padding for spacing

    def export_to_csv(self):
        '''Handles exporting the database to CSV files.'''
        if not self.db_file or not os.path.exists(self.db_file):
            print(f"Database file {self.db_file} not found.")
            self.show_notification("Error", "Database file not found.")
            return
        
        # Ask user for the directory to save CSV files
        save_dir = filedialog.askdirectory(title="Select Directory to Save CSV Files")
        if not save_dir:  # User cancelled the dialog
            return

        try:
            db = ExperimentDatabase(self.db_file)
            db.export_all_tables_to_single_csv(save_dir)
            print("Data exported successfully to CSV files.")
            # Once export is done, show the success notification
            self.show_notification("Success", "Export to CSV successful!")
        except Exception as e:
            print(f"An error occurred while exporting data: {e}")
            self.show_notification("Error", "Export to CSV failed")

    def raise_frame(self):
        '''Raise the frame for this UI'''
        super().raise_frame()

    def show_notification(self, title, message):
        '''Displays a notification when export is complete.'''
        notification = CTkToplevel(self)  # Use Toplevel for a non-blocking modal
        notification.title(title)
        notification.geometry("400x200")  # Increased size for better visibility
        notification.resizable(False, False)

        # Add a label for the message
        label = CTkLabel(
            notification, 
            text=message, 
            font=("Arial", 20), 
            pady=20
        )
        label.pack(pady=10)

        # Add an OK button
        ok_button = CTkButton(
            notification, 
            text="OK", 
            command=notification.destroy, 
            width=100, 
            height=100, 
            font=("Arial", 18)
        )
        ok_button.pack(pady=20)

        notification.transient(self)  # Keep the dialog on top
        notification.grab_set()  # Make it modal
