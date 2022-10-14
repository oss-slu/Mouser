from cProfile import label
from tkinter import *
from tkinter.ttk import *

from NavigateButton import *

class experimentSetupFrame(Frame):
    def __init__(self, parent: Tk, previousPage: Frame = None):
        super().__init__(parent)

        # vars for user input
        self.experName = ''
        self.investigators = ['investigator a', 'investigator b', 'investigator c']
        self.investAdded = []
        self.measurementItems = []
        self.species = ''

        padX = 10
        padY = 20
        labelFont = ("Arial", 13)

        
        self.grid(row=5, column=4, sticky='NESW')

        titleLabel = Label(self, text='Experiment Setup', font=("Arial", 25))
        titleLabel.grid(row=0, column=1, columnspan=2, padx=padX, pady=padY, sticky=N)

        nameLabel = Label(self, text='Experiment Name', font=labelFont).grid(row=1, column=0, padx=padX, pady=padY, sticky=W)
        investLabel = Label(self, text='Investigators', font=labelFont).grid(row=2, column=0, padx=padX, pady=padY, sticky=W)
        specLabel = Label(self, text='Species', font=labelFont).grid(row=3, column=0, padx=padX, pady=padY, sticky=W)
        measItemLabel = Label(self, text='Measurement Items', font=labelFont).grid(row=4, column=0, padx=padX, pady=padY, sticky=W)

        self.nameText = Text(self, height=1, width=30, font=labelFont).grid(row=1, column=1, columnspan=2, padx=padX, pady=padY)
        self.specText = Text(self, height=1, width=30, font=labelFont).grid(row=3, column=1, columnspan=2, padx=padX, pady=padY)
        self.measItemText = Text(self, height=1, width=30, font=labelFont).grid(row=4, column=1, columnspan=2, padx=padX, pady=padY)

        self.options = StringVar()
        investDrop = OptionMenu(self, self.options, self.investigators[0], *self.investigators, command=self.callback)
        investDrop.config(width=40) 
        investDrop['menu'].config(font=labelFont)
        investDrop.grid(row=2, column=1, columnspan=2, padx=padX, pady=padY)
        self.options.set(self.investigators[0])
        self.selected = ''

        investButton = Button(self, text='Add', width=15, command=lambda: self.getInvestigator())
        investButton.grid(row=2, column=3, padx=padX, pady=padY,sticky=E)
        
        measureButton = Button(self, text='Add', width=15, command=lambda: self.addItems())
        measureButton.grid(row=4, column=3, padx=padX, pady=padY,sticky=E)

        # TO-DO connect next page when made
        nextButton = NavigateButton(self, 'Next', self).grid(row=5, column=3, padx=padX, pady=padY,sticky=E)

        for i in range (0, 5):
            if i < 5:
                self.grid_rowconfigure(i, weight=1)
            if i==1 or i==2:
                self.grid_columnconfigure(i, weight=4)
            else:
                self.grid_columnconfigure(i, weight=1)



    def raiseFrame(frame: Frame):
        frame.tkraise()


    def callback(self, selection):
        self.selected = selection
        return self.selected


    def getExperimentName(self):
        return self.nameText.get('1.0', 'end')


    def getInvestigator(self):
        if (self.selected != '' and self.selected not in self.investAdded):
            self.investAdded.append(self.selected)
        # TO-DO : add GUI to show who they've added
        #         give option to remove added name?
        return self.investAdded


    def getSpecies(self):
        return self.specText.get('1.0', 'end')


    def addItems(self):
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

    mainFrame = experimentSetupFrame(root, "Main")
    frame = experimentSetupFrame(root, mainFrame)
    frame.raiseFrame()

    root.mainloop()
###############################################################