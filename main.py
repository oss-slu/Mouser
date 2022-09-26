from tkinter import *
from tkinter.ttk import *

root = Tk()
root.title("Mouser")
root.geometry('600x600')

main = Frame(root)

title = Label(main, text="Mouser", font=("Arial", 25))
title.grid(row=0, column=0, columnspan=4, sticky=N)

mouse = PhotoImage(file="./images/mouse_small.png")

animal_setup = Button(main, text="Animal Setup", image=mouse, compound=TOP)
animal_setup.grid(row=1, column=0, columnspan=2)

data_collection = Button(main, text="Data Collection",
                         image=mouse, compound=TOP)
data_collection.grid(row=1, column=2, columnspan=2)

analysis = Button(main, text="Analysis", image=mouse, compound=TOP)
analysis.grid(row=2, column=0, columnspan=2)

accounts = Button(main, text="Accounts", image=mouse, compound=TOP)
accounts.grid(row=2, column=2, columnspan=2)

main.grid(row=0, column=0, sticky="NESW")
main.grid_rowconfigure(0, weight=1)
main.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
