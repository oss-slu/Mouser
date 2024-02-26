#pylint: skip-file
'''Page for analying data collected in database files.'''
from customtkinter import *
from shared.tk_models import *


class DataAnalysisUI(MouserPage):
    '''Data Analysis UI.'''
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Data Analysis", prev_page)
