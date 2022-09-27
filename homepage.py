import tkinter as tk

class Mouser(tk.Tk):

  def __init__(self):
        
    tk.Tk.__init__(self)
    container = tk.Frame(self)

    container.pack(side="top", fill="both", expand = True)

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    self.frames = {}

    for F in (HomePage, Page):
      frame = F(container, self)
      self.frames[F] = frame
      frame.grid(row=0, column=0, sticky="nsew")

    self.show_frame(HomePage)

  def show_frame(self, cont):
    frame = self.frames[cont]
    frame.tkraise()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Home Page")
        label.pack()

        button = tk.Button(self, text="Page",
                            command=lambda: controller.show_frame(Page))
        button.pack()

class Page(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Page")
        label.pack()

        button = tk.Button(self, text="HomePage",
                            command=lambda: controller.show_frame(HomePage))
        button.pack()


app = Mouser()
app.mainloop()
