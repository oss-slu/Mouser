from customtkinter import *
from tk_models import *
import tkinter.font as tkfont
import shutil
from serial_port_controller import SerialPortController

class SerialSimulator():
    def __init__(self, parent: CTk):
        self.parent = parent
        self.controller = SerialPortController()

    def open(self):
        root = CTkToplevel(self.parent)
        root.title("Serial Port Selection")
        root.geometry('400x700')

        self.input_entry = CTkEntry(self, width=40)
        self.input_entry.place(relx=0.50, rely=0.90, anchor=CENTER)
        self.sent_button = CTkButton(self, text = "sent", width = 15)
        self.sent_button.place(relx=0.80, rely = 0.90, anchor=CENTER)


    def write(self):

        message = self.input_entry.get()
        pass

    def check_installed(self, name):

        return shutil.which(name)
