from tkinter import *
from tkinter.ttk import *
from tk_models import *


class GroupConfigUI(MouserPage):
    def __init__(self, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "New Experiment - Group Configuration", prev_page)
