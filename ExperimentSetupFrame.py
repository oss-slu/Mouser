from tkinter import *
from tkinter.ttk import *
from NavigateButton import *
from IdSetupFrame import IdSetupFrame

class ExperimentSetupFrame(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None):
        super().__init__(parent)
       
        self.root = parent

        # vars for user input
        self.exper_name = ''
        self.investigators = ['investigator a', 'investigator b', 'investigator c']
        self.invest_added = []
        self.measurement_items = []
        self.species = ''

        pad_x = 10
        pad_y = 20
        label_font = ("Arial", 13)
        
        self.grid(row=5, column=4, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=2, padx=pad_x, pady=pad_y)

        Label(self, text='Experiment Name', font=label_font).grid(row=1, column=0, padx=pad_x, pady=pad_y, sticky=W)
        Label(self, text='Investigators', font=label_font).grid(row=2, column=0, padx=pad_x, pady=pad_y, sticky=W)
        Label(self, text='Species', font=label_font).grid(row=3, column=0, padx=pad_x, pady=pad_y, sticky=W)
        Label(self, text='Measurement Items', font=label_font).grid(row=4, column=0, padx=pad_x, pady=pad_y, sticky=W)

        self.name_text = Text(self, height=1, width=30, font=label_font).grid(row=1, column=1, columnspan=2, padx=pad_x, pady=pad_y)
        self.spec_text = Text(self, height=1, width=30, font=label_font).grid(row=3, column=1, columnspan=2, padx=pad_x, pady=pad_y)
        self.meas_item_text = Text(self, height=1, width=30, font=label_font).grid(row=4, column=1, columnspan=2, padx=pad_x, pady=pad_y)

        self.options = StringVar()
        invest_drop = OptionMenu(self, self.options, self.investigators[0], *self.investigators, command=self.callback)
        invest_drop.config(width=40) 
        invest_drop['menu'].config(font=label_font)
        invest_drop.grid(row=2, column=1, columnspan=2, padx=pad_x, pady=pad_y)
        self.options.set(self.investigators[0])
        self.selected = ''

        invest_button = Button(self, text='Add', width=15, command=lambda: self.get_investigators())
        invest_button.grid(row=2, column=3, padx=pad_x, pady=pad_y,sticky=E)
        
        measure_button = Button(self, text='Add', width=15, command=lambda: self.add_items())
        measure_button.grid(row=4, column=3, padx=pad_x, pady=pad_y,sticky=E)


        back_button = NavigateButton(self, 'Back', prev_page)
        next_button = Button(self, text='Next', width=15, command=lambda: self.create_next(self))
        back_button.grid(row=5, column=0, padx=pad_x, pady=pad_y, sticky=W)
        next_button.grid(row=5, column=3, padx=pad_x, pady=pad_y, sticky=E)

        for i in range (0, 5):
            if i < 5:
                self.grid_rowconfigure(i, weight=1)
            if i==1 or i==2:
                self.grid_columnconfigure(i, weight=4)
            else:
                self.grid_columnconfigure(i, weight=1)



    def create_next(self, frame: Frame):
        next = IdSetupFrame(self.root, frame)
        next.grid(row=0, column=0)


    def raise_frame(frame: Frame):
        frame.tkraise()


    def callback(self, selection):
        self.selected = selection
        return self.selected
