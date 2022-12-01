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
        main_frame.grid(row=6, column=1, sticky='NESW')
        main_frame.place(relx=0.3, rely=0.20)

        data_page = DataCollectionUI(parent, self)
        analysis_page = DataAnalysisUI(parent, self)
        cage_page = CageConfigurationUI(name, parent, self)
        rfid_page = MapRFIDPage(parent, self)
        invest_page = InvestigatorsUI(parent, self)

        button_size = 30

        collection_button = Button(main_frame, text='Data Collection', width=button_size, 
                                command= lambda: data_page.raise_frame())
        analysis_button = Button(main_frame, text='Data Analyis', width=button_size,
                                command= lambda: analysis_page.raise_frame())
        group_button = Button(main_frame, text='Group Configuration', width=button_size,
                                command= lambda: cage_page.raise_frame())
        rfid_button = Button(main_frame, text='Map RFID', width=button_size,
                                command= lambda: rfid_page.raise_frame())
        invest_button = Button(main_frame, text='Investigators', width=button_size,
                                command= lambda: invest_page.raise_frame())
        delete_button = Button(main_frame, text='Delete Experiment', width=button_size,
                                command= lambda: self.delete_warning())

        collection_button.grid(row=0, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        analysis_button.grid(row=1, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        group_button.grid(row=2, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        rfid_button.grid(row=3, column=0, ipady=10, ipadx=10, pady=10, padx=10)
        invest_button.grid(row=4, column=0, ipadx=10, ipady=10, pady=10, padx=10)
        delete_button.grid(row=5, column=0, ipadx=10, ipady=10, pady=10, padx=10)


    def delete_warning(self):
        message = Tk()
        message.title("WARNING")
        message.geometry('300x100')
        message.resizable(False, False)

        label1 = Label(message, text='This will delete the experiment and all its data')
        label2 = Label(message, text='are you sure you want to continue?')

        label1.grid(row=0, column=0, columnspan=2, padx=10)
        label2.grid(row=1, column=0, columnspan=2, padx=10)

        yes_button = Button(message, text="Yes, Delete", width=10, 
                        command= lambda: [self.delete_experiment(), message.destroy()])
        no_button = Button(message, text="Cancel", width=10, command= lambda: message.destroy())

        yes_button.grid(row=2, column=0, padx=10, pady=10)
        no_button.grid(row=2, column=1, padx=10, pady=10)

        for i in range(0,3):
            message.grid_rowconfigure(i, 1)
            message.grid_columnconfigure(i, 1)

        message.mainloop()


    def delete_experiment(self):
        # TO-DO delete database
        # TO-DO delete from experiment selection file
        pass

