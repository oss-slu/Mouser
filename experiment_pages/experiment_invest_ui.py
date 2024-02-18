from customtkinter import *
from tk_models import *


class InvestigatorsUI(MouserPage):
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Investigators", prev_page)