from re import S
import tkinter as tk
from tkinter import ttk


class App(tk.Tk):
  def __init__(self):
    super().__init__()

    # configure the root window to use the full screen width and height
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()

    self.title('Mouser')
    self.geometry('{}x{}'.format(screen_width, screen_height))

    # set up buttons 
    
    self.animalSetup = ttk.Button(self, text='Animal Setup')
    self.animalSetup.pack()
    
    self.dataCollection = ttk.Button(self, text='Data Collection')
    self.dataCollection.pack()

    self.analysis = ttk.Button(self, text='Analysis')
    self.analysis.pack()

    self.accounts = ttk.Button(self, text='Accounts')
    self.accounts.pack()

    self.exit = ttk.Button(self, text='exit')
    self.exit.pack()

if __name__ == "__main__":
  app = App()
  app.mainloop()
