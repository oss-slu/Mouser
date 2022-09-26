from tkinter import *
from tkinter.ttk import *

root = Tk()
root.title("Mouser")
root.geometry('600x600')

main = Frame(root)

title = Label(main, text="Mouser", font=("Arial", 25))
title.grid(row=0, column=0, columnspan=4, sticky=N)

mouse = PhotoImage(file="./images/mouse_small.png")
graph = PhotoImage(file="./images/graph_small.png")
magnify = PhotoImage(file="./images/magnifier_small.png")
user = PhotoImage(file="./images/user_small.png")

buttonDim = 25

animal_setup = Button(main, text="Animal Setup", image=mouse,
                      compound=TOP, width=buttonDim)
animal_setup.place(relx=0.33, rely=0.33, anchor=CENTER)

data_collection = Button(main, text="Data Collection",
                         image=graph, compound=TOP, width=buttonDim)
data_collection.place(relx=0.67, rely=0.33, anchor=CENTER)

analysis = Button(main, text="Analysis", image=magnify,
                  compound=TOP, width=buttonDim)
analysis.place(relx=0.33, rely=0.67, anchor=CENTER)

accounts = Button(main, text="Accounts", image=user,
                  compound=TOP, width=buttonDim)
accounts.place(relx=0.67, rely=0.67, anchor=CENTER)

main.grid(row=0, column=0, sticky="NESW")
main.grid_rowconfigure(0, weight=1)
main.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
