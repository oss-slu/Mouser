from tkinter import *
from tkinter.ttk import *
from turtle import onclick
from login import LoginFrame
from tk_models import *

from accounts import AccountsFrame
from experiment_pages.select_experiment_ui import ExperimentsUI

from vert_scroll_model import *

root = Tk()
root.title("Mouser")
root.geometry('600x600')
# root.resizable(False, False)

main_frame = MouserPage(root, "Mouser")



root.mainloop()
