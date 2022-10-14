from cProfile import label
from tkinter import *
from tkinter.ttk import *

from NavigateButton import *

class ExperimentSetupFrame(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None):
        super().__init__(parent)

        # vars for user input
        self.exper_name = ''
        self.investigators = ['investigator a', 'investigator b', 'investigator c']
        self.invest_added = []
        self.measurement_items = []
        self.species = ''

        padX = 10
        padY = 20
        label_font = ("Arial", 13)

        
        self.grid(row=5, column=4, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=2, padx=padX, pady=padY, sticky=N)

        name_label = Label(self, text='Experiment Name', font=label_font).grid(row=1, column=0, padx=padX, pady=padY, sticky=W)
        invest_label = Label(self, text='Investigators', font=label_font).grid(row=2, column=0, padx=padX, pady=padY, sticky=W)
        spec_label = Label(self, text='Species', font=label_font).grid(row=3, column=0, padx=padX, pady=padY, sticky=W)
        meas_item_label = Label(self, text='Measurement Items', font=label_font).grid(row=4, column=0, padx=padX, pady=padY, sticky=W)

        self.name_text = Text(self, height=1, width=30, font=label_font).grid(row=1, column=1, columnspan=2, padx=padX, pady=padY)
        self.spec_text = Text(self, height=1, width=30, font=label_font).grid(row=3, column=1, columnspan=2, padx=padX, pady=padY)
        self.meas_item_text = Text(self, height=1, width=30, font=label_font).grid(row=4, column=1, columnspan=2, padx=padX, pady=padY)

        self.options = StringVar()
        invest_drop = OptionMenu(self, self.options, self.investigators[0], *self.investigators, command=self.callback)
        invest_drop.config(width=40) 
        invest_drop['menu'].config(font=label_font)
        invest_drop.grid(row=2, column=1, columnspan=2, padx=padX, pady=padY)
        self.options.set(self.investigators[0])
        self.selected = ''

        invest_button = Button(self, text='Add', width=15, command=lambda: self.get_investigators())
        invest_button.grid(row=2, column=3, padx=padX, pady=padY,sticky=E)
        
        measure_button = Button(self, text='Add', width=15, command=lambda: self.add_items())
        measure_button.grid(row=4, column=3, padx=padX, pady=padY,sticky=E)

        # TO-DO connect next page when made
        next_button = NavigateButton(self, 'Next', self).grid(row=5, column=3, padx=padX, pady=padY,sticky=E)

        for i in range (0, 5):
            if i < 5:
                self.grid_rowconfigure(i, weight=1)
            if i==1 or i==2:
                self.grid_columnconfigure(i, weight=4)
            else:
                self.grid_columnconfigure(i, weight=1)



    def raise_frame(frame: Frame):
        frame.tkraise()


    def callback(self, selection):
        self.selected = selection
        return self.selected


    def get_experiment_name(self):
        return self.name_text.get('1.0', 'end')


    def get_investigators(self):
        if (self.selected != '' and self.selected not in self.invest_added):
            self.invest_added.append(self.selected)
        # TO-DO : add GUI to show who they've added
        #         give option to remove added name?
        return self.invest_added


    def get_species(self):
        return self.spec_text.get('1.0', 'end')


    def add_items(self):
        return
        # TO-DO : add items list 
        #         comma seperated or type one and hit add
        #         display on gui?





###############################################################
# for demo purposes - remove once everything is all connected #

if __name__ == '__main__':
    root = Tk()
    root.title("Mouser")
    root.geometry('600x600')

    main_frame = ExperimentSetupFrame(root, "Main")
    frame = ExperimentSetupFrame(root, main_frame)
    frame.raise_frame()

    root.mainloop()
###############################################################