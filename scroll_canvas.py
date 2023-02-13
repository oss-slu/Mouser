from tkinter import *
from tkinter.ttk import *

class ScrollCanvas(Canvas):
    def __init__(self, parent, title:str):
        super().__init__(parent)

    # needs to have page back and forth buttons

        self.config(height=600, width=600)

        self.grid(row=0, column=0, columnspan=4)
        self.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        self.titleLabel = self.create_text(300, 13, anchor="n")
        self.set_title(title)

        # self.update_canvas_size()


    def set_title(self, title):
        self.itemconfig(self.titleLabel, text=title, font=("Arial", 18))


    def on_frame_configure(self, event=None):   
        self.configure(scrollregion=self.bbox("all"))


    def update_canvas_size(self, frame):
        # for child in self.winfo_children():
        #     if child.winfo_height() > self.winfo_height():
        #         print('self, child')
        #         print(self.winfo_height())
        #         print(child.winfo_height())
        #         self.config(height=child.winfo_height())
        #         print(self.winfo_height())
        print('here')
        print(frame.winfo_height())
        self.config(height=frame.winfo_height())
        print('canvas:')
        print(self.winfo_height())

        # self.after(1000, self.update_canvas_size)

