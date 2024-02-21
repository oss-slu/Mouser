from customtkinter import *
from tk_models import *


class DataAnalysisUI(MouserPage):
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Data Analysis", prev_page)