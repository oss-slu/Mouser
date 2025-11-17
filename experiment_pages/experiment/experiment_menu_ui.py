'''Experiment Menu Module'''
import os
from customtkinter import *
from shared.tk_models import *
from shared.serial_port_controller import SerialPortController
from experiment_pages.experiment.data_collection_ui import DataCollectionUI
from experiment_pages.experiment.data_analysis_ui import DataAnalysisUI
from experiment_pages.experiment.map_rfid import MapRFIDPage
from experiment_pages.experiment.cage_config_ui import CageConfigurationUI
from experiment_pages.experiment.experiment_invest_ui import InvestigatorsUI
from experiment_pages.experiment.review_ui import ReviewUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI

from databases.experiment_database import ExperimentDatabase

class ExperimentMenuUI(MouserPage):  # pylint: disable=undefined-variable
    '''Main experiment navigation menu.'''

    def __init__(
        self,
        parent: CTk,
        name: str,
        prev_page: ChangeableFrame = None,
        full_path: str = "",
        controller: SerialPortController = None
    ):
        '''Initialize Experiment Menu UI'''

        # For Pylint: ensure required attributes exist before usage
        self.root = parent
        self.menu_button = None

        # New experiment setup page
        self.new_experiment_page = NewExperimentUI(parent, self)
        self.new_experiment = self.new_experiment_page

        experiment_name = os.path.basename(name)
        experiment_name = os.path.splitext(experiment_name)[0]
        self.experiment = ExperimentDatabase(name)
        self.file_path = full_path

        super().__init__(parent, experiment_name, prev_page)

        # Layout container
        main_frame = CTkFrame(self)
        main_frame.grid(row=6, column=1, sticky='NESW')
        main_frame.place(relx=0, rely=0, relwidth=1, relheight=0.9)

        # Grid Config
        main_frame.grid_rowconfigure(0, weight=1, minsize=50)
        main_frame.grid_rowconfigure(1, weight=1, minsize=50)
        main_frame.grid_rowconfigure(2, weight=1, minsize=50)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # Child pages
        self.data_page = DataCollectionUI(parent, name, self)
        self.analysis_page = DataAnalysisUI(parent, self, os.path.abspath(name))
        self.cage_page = CageConfigurationUI(name, parent, self, self.file_path)
        self.summary_page = ReviewUI(parent, self, name)

        # MapRFIDPage constructor mismatch fix (E1121)
        if controller is None:
            # MapRFIDPage(name, parent, prev_page, file_path)
            self.rfid_page = MapRFIDPage(
                name=name,
                parent=parent,
                prev_page=self,
                file_path=self.file_path
            )
        else:
            # MapRFIDPage(name, parent, prev_page, controller, file_path)
            self.rfid_page = MapRFIDPage(
                name=name,
                parent=parent,
                prev_page=self,
                controller=controller,
                file_path=self.file_path
            )

        self.invest_page = InvestigatorsUI(parent, self)

        # Buttons UI
        button_height = main_frame.winfo_screenheight() * 0.3
        button_width = main_frame.winfo_screenwidth() * 0.48
        button_font = ("Arial Black", 35)

        self.collection_button = CTkButton(
            main_frame, text='Data Collection',
            width=button_width, height=button_height, border_width=2.5,
            command=self.data_page.raise_frame, font=button_font
        )

        self.analysis_button = CTkButton(
            main_frame, text='Data Exporting',
            width=button_width, height=button_height, border_width=2.5,
            command=self.analysis_page.raise_frame, font=button_font
        )

        self.group_button = CTkButton(
            main_frame, text='Group Configuration',
            width=button_width, height=button_height, border_width=2.5,
            command=lambda: [
                self.cage_page.raise_frame(),
                self.cage_page.update_config_frame()
            ],
            font=button_font
        )

        self.rfid_button = CTkButton(
            main_frame, text='Map RFID',
            width=button_width, height=button_height, border_width=2.5,
            command=self.rfid_page.raise_frame, font=button_font
        )

        self.summary_button = CTkButton(
            main_frame, text='Summary View',
            width=button_width, height=button_height, border_width=2.5,
            command=self.summary_page.raise_frame, font=button_font
        )

        # Button placement
        self.collection_button.grid(row=0, column=0)
        self.analysis_button.grid(row=0, column=1)
        self.group_button.grid(row=1, column=0)
        self.rfid_button.grid(row=1, column=1)
        self.summary_button.grid(row=2, column=0)

        # Remove default menu button (if exists)
        if self.menu_button:
            self.menu_button.destroy()

        self.bind("<<FrameRaised>>", self.on_show_frame)

        # Initial checks
        self.disable_buttons_if_needed()

    def on_show_frame(self, event=None):
        '''Called when this frame becomes visible.'''
        return

    def disable_buttons_if_needed(self):
        '''Enable or disable buttons based on RFID mapping status.'''
        if self.all_rfid_mapped():
            self.rfid_button.configure(state="disabled")
            self.collection_button.configure(state="normal")
            self.analysis_button.configure(state="normal")
        else:
            self.collection_button.configure(state="disabled")
            self.analysis_button.configure(state="disabled")
            self.rfid_button.configure(state="normal")

    def all_rfid_mapped(self):
        '''Test stub — always returns True.'''
        return True

    def safe_option_get(self, name, class_name="CTk"):
        '''
        Safe wrapper for option_get to avoid TclError on macOS.
        Replaces invalid parameter name "className".
        '''
        try:
            return self.root.option_get(name, class_name)
        except Exception:  # pylint: disable=broad-exception-caught
            return None

    def raise_frame(self):
        '''Bring this frame to the front.'''
        self.on_show_frame()
        super().raise_frame()

    def delete_warning(self, page: CTkFrame, name: str):
        '''Popup confirmation for deleting an experiment.'''
        message = CTk()
        message.title("WARNING")
        message.geometry('750x550')
        message.resizable(False, False)

        label1 = CTkLabel(message, text='This will delete the experiment and all its data')
        label2 = CTkLabel(message, text='Are you sure you want to continue?')

        label1.grid(row=0, column=0, columnspan=2)
        label2.grid(row=1, column=0, columnspan=2)

        yes_button = CTkButton(
            message, text="Yes, Delete", width=10,
            command=lambda: [self.delete_experiment(page, name), message.destroy()]
        )
        no_button = CTkButton(message, text="Cancel", width=10, command=message.destroy)

        yes_button.grid(row=2, column=0, padx=10, pady=10)
        no_button.grid(row=2, column=1, padx=10, pady=10)

        message.mainloop()

    def disconnect_database(self):
        '''Close all database connections.'''
        self.data_page.close_connection()
        self.cage_page.close_connection()

        # Fix E1101 – MapRFIDPage.close_connection missing
        if hasattr(self.rfid_page, "close_connection"):
            self.rfid_page.close_connection()

    def delete_experiment(self, page: CTkFrame, name: str):
        '''Deletes an experiment and its files.'''
        self.disconnect_database()
        splitted = name.split("\\")

        # Build correct OS path
        if "Protected" in splitted[-1]:
            base = os.getcwd()
            rel = "databases/experiments/" + splitted[-1]
            name = os.path.join(base, rel)

        try:
            os.remove(name)
        except OSError as error:
            print("Error deleting experiment:", error)
            return

        page.tkraise()

    def open_data_collection(self):
        '''Open data collection page.'''
        page = DataCollectionUI(self.root, self.file_path, self)
        page.raise_frame()

    def open_data_analysis(self):
        '''Open data analysis page.'''
        page = DataAnalysisUI(self.root, self.file_path, self)
        page.raise_frame()

    def back_to_welcome(self):
        '''Return to welcome screen.'''
        from ui.welcome_screen import setup_welcome_screen
        setup_welcome_screen(self.root, self)