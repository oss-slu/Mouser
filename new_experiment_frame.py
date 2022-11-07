from tkinter import *
from tkinter.ttk import *
from tk_models import *


investigators = ['investigator a', 'investigator b', 'investigator c']


# class MenuButton(Button):
#     def __init__(self, page: Frame, previous_page: Frame):
#         super().__init__(page, text="Back to Menu", compound=TOP,
#                          width=15, command=lambda: self.navigate())
#         self.previous_page = previous_page

#     def navigate(self):
#         self.previous_page.tkraise()


class NewExperimentFrame(Frame):
    def __init__(self, parent: Tk, previous_page: Frame = None):
        super().__init__(parent)
        self.grid(row=12, column=3)

        canvas = Canvas(self, width=600, height=600)
        canvas.grid(row=0, column=0, columnspan=3)
        canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        titleLabel = canvas.create_text(300, 13, anchor="n")
        canvas.itemconfig(titleLabel, text='New Experiment', font=("Arial", 18))

        # MenuButton(self, previous_page).grid(row=1, column=0)

        self.added_invest = []

        Label(self, text='Experiment Name').grid(row=1, column=0, sticky=W)
        # Label(self, text='Investigators').grid(row=2, column=0, sticky=W)
        # Label(self, text='Species').grid(row=4, column=0, sticky=W)
        # Label(self, text='Measurement Items').grid(row=5, column=0, sticky=W)
        # Label(self, text="RFID").grid(row=7, column=0, sticky=W)
        # Label(self, text="Number of Animals").grid(row=8, column=0, sticky=W)
        # Label(self, text="Number of Groups").grid(row=9, column=0, sticky=W)
        # Label(self, text="Max Animals per Cage").grid(row=10, column=0, sticky=W)

        # self.exper_name = Text(self, width=30)

        # self.investigator = Combobox(self, width=30)
        # self.investigator['values'] = investigators
        # self.investigator['state'] = 'readonly'
        # self.investigator.grid(row=2, column=1, sticky=W)
        # self.investigator.bind('<<ComboboxSelected>>', self.add_investigator)
        # # add_invest = Button(self, text="+", width= 3, 
        # #                     command=lambda: self.add_investigator(self.investigators.current))
        # # add_invest.place(relx=0.8, rely=0.3)

        # # self.invest_added = Text(self, width=30)
        # self.measurement_items = Text(self, width=30)
        # self.species = Text(self, width=30)


    def raise_frame(self):
        self.tkraise()


    def add_investigator(self, event):
        if self.investigator.get() not in self.added_invest:
            self.added_invest.append(self.investigator.get())
            # Label(self, text=self.investigator.get()).pack()
            # Button(self, text='-', width=1, command=lambda: 
            #         self.remove_investigator(self.investigator.get())).pack()
        print(self.added_invest)
        return self.added_invest

    def remove_investigator(self, invest):
        self.added_invest.remove(invest)
        print(self.added_invest)
        return self.added_invest