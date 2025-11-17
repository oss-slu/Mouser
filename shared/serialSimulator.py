'''Serial Simulation.'''
import shutil

from customtkinter import *

from shared.serial_port_controller import SerialPortController
from shared.tk_models import *


class SerialSimulator():
    '''Serial Simulator User Interface.'''
    def __init__(self, parent: CTk):
        self.parent = parent
        self.controller = SerialPortController()

    def open(self):
        '''Opens Serial Simulator user interface.'''
        root = CTkToplevel(self.parent) #pylint: disable= redefined-outer-name
        root.title("Serial Port Selection")
        root.geometry('400x700')

        self.input_entry = CTkEntry(self, width=40)
        self.input_entry.place(relx=0.50, rely=0.90, anchor=CENTER)
        self.sent_button = CTkButton(self, text = "sent", width = 15)
        self.sent_button.place(relx=0.80, rely = 0.90, anchor=CENTER)


    def write(self):
        '''Writes to simulated serial'''
        _ = self.input_entry.get()
    def check_installed(self, name):
        '''Checks if the passed name is installed.'''
        return shutil.which(name)
