#pylint: skip-file
'''Experiement Investigator Module.'''
from customtkinter import *
from shared.tk_models import *


class InvestigatorsUI(MouserPage):
    '''Investigator page frame.'''
    def __init__(self, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Investigators", prev_page)
