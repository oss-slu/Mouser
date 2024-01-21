from tkinter  import *
from tkinter.ttk import *
from tk_models import *
import tkinter.font as tkfont
import shutil
from serial_port_controller import SerialPortController

class SerialSimulator():
    def __init__(self, parent: Tk):
        self.parent = parent
        self.controller = SerialPortController()

    def open(self):
        root = Toplevel(self.parent)
        root.title("Serial Port Selection")
        root.geometry('400x700')

        self.input_entry = Entry(self, width=40)
        self.input_entry.place(relx=0.50, rely=0.90, anchor=CENTER)
        self.sent_button = Button(self, text = "sent", width = 15)
        self.sent_button.place(relx=0.80, rely = 0.90, anchor=CENTER)


    def write(self):

        message = self.input_entry.get()
        pass

    def check_installed(self, name):

        return shutil.which(name)
