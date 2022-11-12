from tkinter import *
from tkinter.ttk import *
from tk_models import *


class ExperimentMenuUI(MouserPage):
    def __init__(self, parent:Tk, name: str, prev_page: Frame = None):
        super().__init__(parent, name, prev_page)