from tkinter import *
from tkinter.ttk import *
from turtle import onclick
from login import LoginFrame
from tk_models import *

from accounts import AccountsFrame
from ExperimentSetupFrame import *

from ExperimentSetupFrame import *
from IdSetupFrame import *
from GroupSetupFrame import *

root = Tk()
root.title("Mouser")
root.geometry('600x600')
# root.resizable(False, False)

main_frame = MouserPage(root, "Mouser")
login_frame = LoginFrame(root, main_frame)

accounts_frame = AccountsFrame(root, main_frame)
animal_setup_frame = ExperimentSetupFrame(root, main_frame)

mouse_image = PhotoImage(file="./images/flask.png")
user_image = PhotoImage(file="./images/user_small.png")

create_nav_button(main_frame, "Experiments", mouse_image,
                  animal_setup_frame, 0.5, 0.33)
create_nav_button(main_frame, "Accounts", user_image,
                  accounts_frame, 0.5, 0.67)

frames = [animal_setup_frame]

for i, frame in enumerate(frames):
    back = MenuButton(frame, main_frame)
    frame.grid(row=0, column=0, sticky="NESW")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

raise_frame(login_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
