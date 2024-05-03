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


class ExperimentMenuUI(MouserPage): #pylint: disable= undefined-variable
    '''Experiment Menu Page Frame'''
    def __init__(self, parent: CTk, name: str, prev_page: ChangeableFrame = None, controller: SerialPortController = None): #pylint: disable= undefined-variable

        #Get name of file from file path
        experiment_name = os.path.basename(name)
        experiment_name = os.path.splitext(experiment_name)[0]

        super().__init__(parent, experiment_name, prev_page)

        main_frame = CTkFrame(self) # pylint: disable=redefined-outer-name

        main_frame.grid(row=6, column=1, sticky='NESW')
        main_frame.place(relx=0.3, rely=0.20, relwidth= 0.40, relheight = 0.75)

        main_frame.grid_columnconfigure(0, weight = 1)

        self.data_page = DataCollectionUI(parent, self, name)
        self.analysis_page = DataAnalysisUI(parent, self)
        self.cage_page = CageConfigurationUI(name, parent, self)
        self.rfid_page = MapRFIDPage(name, parent, self, controller)
        self.invest_page = InvestigatorsUI(parent, self)

        button_size = 30


        collection_button = CTkButton(main_frame, text='Data Collection', width=button_size,
                                command= self.data_page.raise_frame)
        analysis_button = CTkButton(main_frame, text='Data Analysis', width=button_size,
                                command= self.analysis_page.raise_frame)
        group_button = CTkButton(main_frame, text='Group Configuration', width=button_size,
                                command= lambda: [self.cage_page.raise_frame(),
                                                  self.cage_page.update_controller_attributes(),
                                                  self.cage_page.update_config_frame()])
        rfid_button = CTkButton(main_frame, text='Map RFID', width=button_size,
                                command=  self.rfid_page.raise_frame)
        invest_button = CTkButton(main_frame, text='Investigators', width=button_size,
                                command= self.invest_page.raise_frame)
        delete_button = CTkButton(main_frame, text='Delete Experiment', width=button_size,
                                command= lambda: self.delete_warning(prev_page, name))

        collection_button.grid(row=0, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        analysis_button.grid(row=1, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        group_button.grid(row=2, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        rfid_button.grid(row=3, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        invest_button.grid(row=4, column=0, ipadx=10, ipady=10, pady=10, padx=10)
        delete_button.grid(row=5, column=0, ipadx=10, ipady=10, pady=10, padx=10)   


    def delete_warning(self, page: CTkFrame, name: str):
        '''Raises warning frame for deleting experiment.'''
        message = CTk()
        message.title("WARNING")
        message.geometry('300x100')
        message.resizable(False, False)

        label1 = CTkLabel(message, text='This will delete the experiment and all its data')
        label2 = CTkLabel(message, text='are you sure you want to continue?')

        label1.grid(row=0, column=0, columnspan=2, padx=10)
        label2.grid(row=1, column=0, columnspan=2, padx=10)

        yes_button = CTkButton(message, text="Yes, Delete", width=10,
                        command= lambda: [self.delete_experiment(page, name), message.destroy()])
        no_button = CTkButton(message, text="Cancel", width=10, command= message.destroy)
        yes_button.grid(row=2, column=0, padx=10, pady=10)
        no_button.grid(row=2, column=1, padx=10, pady=10)

        #for i in range(0,3):
        #    message.grid_rowconfigure(i, 1)
        #    message.grid_columnconfigure(i, 1)

        message.mainloop()

    def disconnect_database(self):
        '''Close database in all other pages.'''
        self.data_page.close_connection()
        self.cage_page.close_connection()
        self.rfid_page.close_connection()

    def delete_experiment(self, page: CTkFrame, name: str):
        '''Delete Experiment.'''

        # disconnect the file from the database
        self.disconnect_database()
        splitted = name.split("\\")
        if ("Protected" in splitted[-1]):
            path = os.getcwd()
            name = path + "\\databases\\experiments\\" + splitted[-1]
            

        try:
            os.remove(name)
        except OSError as error:
            print("error from deleting experiment: ",error)
            return

        page.tkraise()
