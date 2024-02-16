'''Serial Simulation.'''
import shutil
from tkinter import *
from tkinter.ttk import *
from tk_models import *
from serial_port_controller import SerialPortController

class SerialSimulator():
    '''Serial Simulator User Interface.'''
    def __init__(self, parent: Tk):
        self.parent = parent
        self.controller = SerialPortController()

    def open(self):
        '''Opens Serial Simulator user interface.'''
        root = Toplevel(self.parent) #pylint: disable= redefined-outer-name
        root.title("Serial Port Selection")
        root.geometry('400x700')

        self.input_entry = Entry(self, width=40)
        self.input_entry.place(relx=0.50, rely=0.90, anchor=CENTER)
        self.sent_button = Button(self, text = "sent", width = 15)
        self.sent_button.place(relx=0.80, rely = 0.90, anchor=CENTER)


    def write(self):
        '''Writes to simulated serial'''
        _ = self.input_entry.get()
    def check_installed(self, name):
        '''Checks if the passed name is installed.'''
        return shutil.which(name)
