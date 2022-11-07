from tkinter import *
from tkinter.ttk import *
from tk_models import *

# class FrameTest(MouserPage):
#     def __init__(self, parent: Tk, previous_page: Frame):
#         super().__init__(parent, "New Experiment", previous_page)

#         self.grid(row=9, column=6)
#         Label(self, text='Experiment Name').grid(row=1, column=0, padx=10)



class FrameTest(Frame):
    def __init__(self, parent: Tk, menu_page: Frame = None):
        super().__init__(parent)
        self.grid(row=9, column=4, sticky='NSEW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25), anchor='center')
        title_label.grid(row=0, column=0, columnspan=4)


        # canvas = Canvas(self, width=600, height=600)
        # canvas.grid(row=0, column=0, columnspan=4)
        # canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        # titleLabel = canvas.create_text(300, 13, anchor="n")
        # canvas.itemconfig(titleLabel, text='New Experiment', font=("Arial", 18))

        Label(self, text='Experiment Name').grid(row=1, column=0, padx=10)
        # Label(self, text='Investigators').grid(row=2, column=0, sticky=W)
        # Label(self, text='Species').grid(row=4, column=0, sticky=W)
        # Label(self, text='Measurement Items').grid(row=5, column=0, sticky=W)
        # Label(self, text="RFID").grid(row=7, column=0, sticky=W)
        # Label(self, text="Number of Animals").grid(row=8, column=0, sticky=W)
        # Label(self, text="Number of Groups").grid(row=9, column=0, sticky=W)
        # Label(self, text="Max Animals per Cage").grid(row=10, column=0, sticky=W)



        for i in range(0,9):
            if i < 6:
                self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)


    def raise_frame(self):
        self.tkraise()



if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')

    frame = FrameTest(root, "Template")

    # main_frame.set_next_button(frame)
    # frame.set_previous_button(main_frame)

    frame.raise_frame()

    # root.grid_rowconfigure(0, weight=1)
    # root.grid_columnconfigure(0, weight=1)

    root.mainloop()
