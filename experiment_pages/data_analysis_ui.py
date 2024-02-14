'''Page for analying data collected in database files.'''
from tkinter import *
from tkinter.ttk import *
from tk_models import *


class DataAnalysisUI(MouserPage):
    '''Data Analysis UI.'''
    def __init__(self, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "Data Analysis", prev_page)
