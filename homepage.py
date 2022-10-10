import tkinter as tk

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Home Page")
        label.pack()

        button = tk.Button(self, text="Page",
                            command=lambda: controller.show_frame("Page"))
        button.pack()

    def getName(self):
      return "HomePage"
