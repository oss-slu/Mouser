from tkinter import *
from tkinter.ttk import *
from tk_models import *
from group_config_ui import GroupConfigUI


class NewExperimentUI(MouserPage):
    def __init__(self, parent:Tk, prev_page: Frame = None):
        super().__init__(parent, "New Experiment", prev_page)

        self.set_next_button(GroupConfigUI(parent, self))

        main_frame = Frame(self)
        main_frame.grid(row=9, column=4, sticky='NESW')
        main_frame.place(relx=0.12, rely=0.20)

        pad_x = 10
        pad_y = 10

        Label(main_frame, text='Experiment Name').grid(row=1, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text='Investigators').grid(row=2, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text='Species').grid(row=4, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text='Measurement Items').grid(row=5, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text="RFID").grid(row=7, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text="Number of Animals").grid(row=8, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text="Number of Groups").grid(row=9, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(main_frame, text="Max Animals per Cage").grid(row=10, column=0, sticky=W, padx=pad_x, pady=pad_y)

        self.exper_name = Combobox(main_frame, width=30)



        for i in range(0,9):
            if i < 4:
                self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)


    def set_next_button(self, next_page):
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)
        self.next_button.place(relx=0.85, rely=0.15)
