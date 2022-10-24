from tkinter import *
from tkinter.ttk import *
from turtle import onclick
from tk_models import *
from accounts import AccountsFrame
from ExperimentSetupFrame import *

root = Tk()
root.title("Mouser")
root.geometry('600x600')

data_collection_frame = Frame(root)
analysis_frame = Frame(root)
main_frame = MouserPage(root, "Mouser")
accounts_frame = AccountsFrame(root, main_frame)
animal_setup_frame = ExperimentSetupFrame(root, main_frame)

mouse_image = PhotoImage(file="./images/mouse_small.png")
graph_image = PhotoImage(file="./images/graph_small.png")
magnify_image = PhotoImage(file="./images/magnifier_small.png")
user_image = PhotoImage(file="./images/user_small.png")

create_nav_button(main_frame, "Animal Setup", mouse_image,
                  animal_setup_frame, 0.33, 0.33)
create_nav_button(main_frame, "Data Collection", graph_image,
                  data_collection_frame, 0.67, 0.33)
create_nav_button(main_frame, "Analysis", magnify_image,
                  analysis_frame, 0.33, 0.67)
create_nav_button(main_frame, "Accounts", user_image,
                  accounts_frame, 0.67, 0.67)

frames = [animal_setup_frame,
          data_collection_frame, analysis_frame]

for i, frame in enumerate(frames):
    if frame != animal_setup_frame:
        back = BackButton(frame, main_frame)
    frame.grid(row=0, column=0, sticky="NESW")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

raise_frame(main_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()

