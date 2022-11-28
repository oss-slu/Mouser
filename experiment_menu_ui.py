from tkinter import *
from tkinter.ttk import *
from tk_models import *
from experiment_pages.data_collection_ui import DataCollectionUI
from experiment_pages.data_analysis_ui import DataAnalysisUI
from experiment_pages.map_rfid import MapRFIDPage
from experiment_pages.cage_config_ui import CageConfigurationUI
from experiment_pages.experiment_invest_ui import InvestigatorsUI

class ExperimentMenuUI(MouserPage):
    def __init__(self, parent:Tk, name: str, prev_page: Frame = None):
        super().__init__(parent, name, prev_page)
        
        main_frame = Frame(self)
        main_frame.grid(row=5, column=1, sticky='NESW')
        main_frame.place(relx=0.27, rely=0.20)

        data_page = DataCollectionUI(parent, self)
        analysis_page = DataAnalysisUI(parent, self)
        cage_page = CageConfigurationUI(parent, self)
        rfid_page = MapRFIDPage(parent, self)
        invest_page = InvestigatorsUI(parent, self)

        collection_button = Button(main_frame, text='Data Collection', 
                                command= lambda: data_page.raise_frame())
        analysis_button = Button(main_frame, text='Data Analyis', 
                                command= lambda: analysis_page.raise_frame())
        group_button = Button(main_frame, text='Group Configuration', 
                                command= lambda: cage_page.raise_frame())
        rfid_button = Button(main_frame, text='Map RFID', 
                                command= lambda: rfid_page.raise_frame())
        invest_button = Button(main_frame, text='Investigators', 
                                command= lambda: invest_page.raise_frame())

        collection_button.grid(row=0, column=0, padx=10, pady=10)
        analysis_button.grid(row=1, column=0, padx=10, pady=10)
        group_button.grid(row=2, column=0, padx=10, pady=10)
        rfid_button.grid(row=3, column=0, padx=10, pady=10)
        invest_button.grid(row=4, column=0, padx=10, pady=10)

