from tkinter import *
from tkinter.ttk import *
from map_rfid import *


class ChangeRFIDDialog():
    def __init__(self, parent: Tk, map_rfid: MapRFIDPage):
        self.parent = parent
        self.map_rfid = map_rfid

    def open(self):
        self.root = root = Toplevel(self.parent)
        root.title("Change RFID")
        root.geometry('400x400')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        simulate_rfid_button = Button(root, text="Simulate RFID", compound=TOP,
                                      width=15, command=lambda: self.add_random_rfid())
        simulate_rfid_button.place(relx=0.50, rely=0.20, anchor=CENTER)

        self.root.mainloop()

    def add_random_rfid(self):
        rfid = get_random_rfid()
        self.map_rfid.change_selected_value(rfid)
        self.close()

    def close(self):
        self.root.destroy()
