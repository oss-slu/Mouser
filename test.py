from serial_port_controller import SerialPortController

import shutil
import os.path
import webbrowser
import tkinter as tk
from tkinter import messagebox
from tkinter import *

#this file has nothing to do with main Mouser, just as a test file for different things
# this file will be used to test the simulator with os walk
ser = SerialPortController()
#ser.write_test('COM5')


## note: to send over through serial port, the two port must be open before data is written through
"""
ser.set_reader_port('COM4')
ser.set_writer_port('COM5')
ser.write_to('Hello')
print(ser.read_info())
#print(ser.read_info('COM4').strip())
"""
root = Tk() 
root.geometry("300x200") 
  
w = Label(root, text ='GeeksForGeeks', font = "50")  
w.pack() 
  
  
  
messagebox.askretrycancel("askretrycancel", "Try again?")   
  
root.mainloop()


#print(os.path.exists(""))
#webbrowser.open("https://stackoverflow.com/questions/66681576/can-i-connect-a-python-gui-to-a-website-using-http")

# Import module 
  
# Create object 
"""
def display_selection():
    # Get the selected value.
    selection = combo.get()
    a = messagebox.askyesno(
        message=f"The selected value is: {selection}",
        title="Selection"
    )
    print(a)

main_window = tk.Tk()
main_window.config(width=300, height=200)
main_window.title("Combobox")
combo = ttk.Combobox(
    state="readonly",
    values=["Python", "C", "C++", "Java"]
)
combo.place(x=50, y=50)
button = ttk.Button(text="Display selection", command=display_selection)
button.place(x=50, y=100)
main_window.mainloop()
"""