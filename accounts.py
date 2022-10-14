from tkinter import *
from tkinter.ttk import *
from tk_models import *


class UserSettingsFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Account Settings", True, previous_page)


class AccountsFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Accounts", True, previous_page)
