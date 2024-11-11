# pylint: skip-file
import os
from customtkinter import *
from shared.tk_models import *

class DataCollectionButtons:
    '''Class that creates the buttons for the experiment page.'''

    def __init__(self, parent, main_frame, name, controller=None):
        from experiment_pages.experiment.data_analysis_ui import DataAnalysisUI
        from experiment_pages.experiment.map_rfid import MapRFIDPage
        from experiment_pages.experiment.cage_config_ui import CageConfigurationUI
        from experiment_pages.experiment.experiment_invest_ui import InvestigatorsUI
        
        self.analysis_page = DataAnalysisUI(parent, self, os.path.abspath(name))
        self.cage_page = CageConfigurationUI(name, parent, self)
        if controller is None:
            self.rfid_page = MapRFIDPage(name, parent, self)
        else:
            self.rfid_page = MapRFIDPage(name, parent, self, controller)
        self.invest_page = InvestigatorsUI(parent, self)

        button_size = 30

        self.analysis_button = CTkButton(main_frame, text='Data Exporting', width=button_size,
                                command= self.analysis_page.raise_frame)
        self.group_button = CTkButton(main_frame, text='Group Configuration', width=button_size,
                                command= lambda: [self.cage_page.raise_frame(),
                                                  self.cage_page.update_controller_attributes(),
                                                  self.cage_page.update_config_frame()])
        self.rfid_button = CTkButton(main_frame, text='Map RFID', width=button_size,
                                command=  self.rfid_page.raise_frame)

        self.analysis_button.grid(row=1, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.group_button.grid(row=2, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.rfid_button.grid(row=3, column=0, ipady=10, ipadx=10, pady=10, padx=10)
    
    def get_analysis_button(self):
        '''Returns the data analysis button.'''
        return self.analysis_button
    
    def get_group_button(self):
        '''Returns the group configuration button.'''
        return self.group_button
    
    def get_rfid_button(self):
        '''Returns the RFID mapping button.'''
        return self.rfid_button
    
class DataExportButtons:
    '''Class that creates the buttons for the experiment page.'''
    def __init__(self, parent, main_frame, name, controller=None):
        from experiment_pages.experiment.data_collection_ui import DataCollectionUI
        from experiment_pages.experiment.map_rfid import MapRFIDPage
        from experiment_pages.experiment.cage_config_ui import CageConfigurationUI
        from experiment_pages.experiment.experiment_invest_ui import InvestigatorsUI
        
        self.data_page = DataCollectionUI(parent, self, name)
        self.cage_page = CageConfigurationUI(name, parent, self)
        if controller is None:
            self.rfid_page = MapRFIDPage(name, parent, self)
        else:
            self.rfid_page = MapRFIDPage(name, parent, self, controller)
        self.invest_page = InvestigatorsUI(parent, self)

        button_size = 30

        self.collection_button = CTkButton(main_frame, text='Data Collection', width=button_size,
                                command= self.data_page.raise_frame)
        self.group_button = CTkButton(main_frame, text='Group Configuration', width=button_size,
                                command= lambda: [self.cage_page.raise_frame(),
                                                  self.cage_page.update_controller_attributes(),
                                                  self.cage_page.update_config_frame()])
        self.rfid_button = CTkButton(main_frame, text='Map RFID', width=button_size,
                                command=  self.rfid_page.raise_frame)

        self.collection_button.grid(row=0, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.group_button.grid(row=2, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.rfid_button.grid(row=3, column=0, ipady=10, ipadx=10, pady=10, padx=10)


    def get_collection_button(self):
        '''Returns the data collection button.'''
        return self.collection_button
    
    def get_group_button(self):
        '''Returns the group configuration button.'''
        return self.group_button
    
    def get_rfid_button(self):
        '''Returns the RFID mapping button.'''
        return self.rfid_button
    
class GroupConfigButtons:
    '''Class that creates the buttons for the experiment page.'''
    def __init__(self, parent, main_frame, name, controller=None):
        from experiment_pages.experiment.data_collection_ui import DataCollectionUI
        from experiment_pages.experiment.data_analysis_ui import DataAnalysisUI
        from experiment_pages.experiment.map_rfid import MapRFIDPage
        from experiment_pages.experiment.experiment_invest_ui import InvestigatorsUI
        
        self.data_page = DataCollectionUI(parent, self, name)
        self.analysis_page = DataAnalysisUI(parent, self, os.path.abspath(name))
        if controller is None:
            self.rfid_page = MapRFIDPage(name, parent, self)
        else:
            self.rfid_page = MapRFIDPage(name, parent, self, controller)
        self.invest_page = InvestigatorsUI(parent, self)

        button_size = 30

        self.collection_button = CTkButton(main_frame, text='Data Collection', width=button_size,
                                command= self.data_page.raise_frame)
        self.analysis_button = CTkButton(main_frame, text='Data Exporting', width=button_size,
                                command= self.analysis_page.raise_frame)
        self.rfid_button = CTkButton(main_frame, text='Map RFID', width=button_size,
                                command=  self.rfid_page.raise_frame)

        self.collection_button.grid(row=0, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.analysis_button.grid(row=1, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.rfid_button.grid(row=3, column=0, ipady=10, ipadx=10, pady=10, padx=10)


    def get_collection_button(self):
        '''Returns the data collection button.'''
        return self.collection_button
    
    def get_analysis_button(self):
        '''Returns the data analysis button.'''
        return self.analysis_button
    
    def get_rfid_button(self):
        '''Returns the RFID mapping button.'''
        return self.rfid_button
    
class RFIDButtons:
    '''Class that creates the buttons for the experiment page.'''
    def __init__(self, parent, main_frame, name, controller=None):
        from experiment_pages.experiment.data_collection_ui import DataCollectionUI
        from experiment_pages.experiment.data_analysis_ui import DataAnalysisUI
        from experiment_pages.experiment.cage_config_ui import CageConfigurationUI
        from experiment_pages.experiment.experiment_invest_ui import InvestigatorsUI
        
        self.data_page = DataCollectionUI(parent, self, name)
        self.analysis_page = DataAnalysisUI(parent, self, os.path.abspath(name))
        self.cage_page = CageConfigurationUI(name, parent, self)
        self.invest_page = InvestigatorsUI(parent, self)

        button_size = 30

        self.collection_button = CTkButton(main_frame, text='Data Collection', width=button_size,
                                command= self.data_page.raise_frame)
        self.analysis_button = CTkButton(main_frame, text='Data Exporting', width=button_size,
                                command= self.analysis_page.raise_frame)
        self.group_button = CTkButton(main_frame, text='Group Configuration', width=button_size,
                                command= lambda: [self.cage_page.raise_frame(),
                                                  self.cage_page.update_controller_attributes(),
                                                  self.cage_page.update_config_frame()])

        self.collection_button.grid(row=0, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.analysis_button.grid(row=1, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        self.group_button.grid(row=2, column=0, ipady=10, ipadx=10, pady=10, padx=10)


    def get_collection_button(self):
        '''Returns the data collection button.'''
        return self.collection_button
    
    def get_analysis_button(self):
        '''Returns the data analysis button.'''
        return self.analysis_button
    
    def get_group_button(self):
        '''Returns the group configuration button.'''
        return self.group_button