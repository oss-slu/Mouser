import tkinter as tk
from homepage import HomePage
from page import Page

class Controller(tk.Tk):

  def __init__(self):
        
    tk.Tk.__init__(self)
    container = tk.Frame(self)
    container.pack(side="top", fill="both", expand = True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    self.frames = {}

    for F in (HomePage, Page):
      frame = F(container, self)
      self.frames[frame.getName()] = frame
      frame.grid(row=0, column=0, sticky="nsew")

    self.show_frame("HomePage")

  def show_frame(self, cont):
    frame = self.frames[cont]
    frame.tkraise()

app = Controller()
app.mainloop()
