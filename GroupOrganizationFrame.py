from tkinter import *
from tkinter.ttk import *
from NavigateButton import *
from CageSetupFrame import CageSetupFrame


class GroupOrganizationFrame(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None):
        super().__init__(parent)

        # vars for demo
        self.groups = ['Group 1', 'Group 2', 'Group 3']
        self.animals = [ ('1', '26.45', '123456AV12'), ('2','21.59', '654321QR07', 'Group 1') ]

        self.root = parent
        self.pad_x = 10
        self.pad_y = 10
        self.label_font = ("Arial", 13)

        self.grid(row=5, column=6, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=4, padx=self.pad_x, pady=self.pad_y)

        reset_label = Label(self, text='Reset Animal\nGroups', font=self.label_font)
        reset_label.grid(row=3, column=0, padx=self.pad_x, pady=self.pad_y)

        self.animal_id = Entry(self, width=8, font=self.label_font)
        self.animal_id.grid(row=3, column=1, padx=self.pad_x, pady=self.pad_y)
        self.animal_id.insert(0, 'animal ID')

        drag_table = self.drag_table(self.groups)
        drag_table.grid(row=1, column=0, columnspan=6, padx=self.pad_x, pady=self.pad_y)

        ungrouped = self.ungrouped_table()
        ungrouped.grid(row=2, column=0, columnspan=6, padx=self.pad_x, pady=self.pad_y)

        reset_button = Button(self, text='Reset', width=15, command=lambda: self.reset_groups())
        reset_all_button = Button(self, text='Reset All', width=15, command=lambda: self.reset_all_groups())
        save_button = Button(self, text='Save', width=15, command=lambda: self.save_groups('temp'))

        reset_button.grid(row=3, column=2, padx=self.pad_x, pady=self.pad_y)
        reset_all_button.grid(row=4, column=4, padx=self.pad_x, pady=self.pad_y)
        save_button.grid(row=4, column=5, padx=self.pad_x, pady=self.pad_y)

        prev_button = NavigateButton(self, 'Previous', prev_page)
        next_button = Button(self, text='Next', width=15, command=lambda: self.create_next(self))
        prev_button.grid(row=5, column=0, columnspan=1, padx=self.pad_x, pady=self.pad_y, sticky=W)
        next_button.grid(row=5, column=5, columnspan=1, padx=self.pad_x, pady=self.pad_y, sticky=E)
        

        for i in range(0,6):
            if i < 5:
                self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)



    def raise_frame(frame: Frame):
        frame.tkraise()


    def create_next(self, frame: Frame):
        next = CageSetupFrame(self.root, frame)
        next.grid(row=0, column=0)


    def drag_group(self, table):
        draggable = LabelFrame(table, height=100, width=200, relief=RIDGE)
        draggable.grid(row=2, column=2)
        Label(draggable, text='ID', font=self.label_font).grid(row=0, column=0, sticky=W)
        Label(draggable, text='Animal\nWeight', font=self.label_font).grid(row=0, column=1, sticky=W)
        Label(draggable, text=self.animals[0][0], font=self.label_font).grid(
            row=1, column=0, padx=self.pad_x, pady=5, sticky=W)
        Label(draggable, text=self.animals[0][1], font=self.label_font).grid(
            row=1, column=1, padx=self.pad_x, pady=5, sticky=W)
        for i in range(0,1):
            draggable.grid_rowconfigure(i, weight=1)
            draggable.grid_columnconfigure(i, weight=1)
        return draggable


    def drag_table(self, groups):
        table = LabelFrame(self, height=200, width=(600 - self.pad_x), relief=FLAT)
        table.grid(row=2, column=len(groups)+1, padx=30)
        col = 0
        for group_name in groups:
            Label(table, text=group_name, font=self.label_font).grid(
                row=0, column=col, padx=50)
            for animal in self.animals:
                if group_name in animal:
                    draggable = self.drag_group(table)
                    draggable.grid(row=1, column=col, padx=30)
            col += 1
        return table
            

    def find_ungrouped(self):
        ungrouped = []
        for group in self.groups:
            for animal in self.animals:
                if group in animal:
                    break
                ungrouped.append(animal)
        return ungrouped


    def ungrouped_table(self):
        table = LabelFrame(self, height=200, width=(600 - self.pad_x*2), relief=RIDGE)
        table.grid(row=len(self.animals)+1, column=3)

        labels = ['ID (auto generated)', 'Animal Weight (pounds)', 'RFID']
        for i in range(0, len(labels)):
            Label(table, text=labels[i], font=self.label_font, padding=15).grid(row=0, column=i)
            table.grid_columnconfigure(i, weight=1) 
        for animal in self.find_ungrouped():
            Label(table, text=animal[0], font=self.label_font, padding=15).grid(row=1, column=0)
            Label(table, text=animal[1], font=self.label_font, padding=15).grid(row=1, column=1)
            Label(table, text=animal[2], font=self.label_font, padding=15).grid(row=1, column=2)
        return table

