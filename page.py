import tkinter as tk

class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Page")
        label.pack()

        button = tk.Button(self, text="HomePage",
                            command=lambda: controller.show_frame("HomePage"))
        button.pack()

    def getName(self):
        return "Page"
