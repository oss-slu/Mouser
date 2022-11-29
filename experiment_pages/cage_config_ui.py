from tkinter import *
from tkinter.ttk import *
from tk_models import *


class CageConfigurationUI(MouserPage):
    def __init__(self, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "Group Configuration", prev_page)