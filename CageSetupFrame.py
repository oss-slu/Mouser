from operator import indexOf
from tkinter import *
from tkinter.ttk import *
from NavigateButton import *
import array

class CageSetupFrame(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None, next_page: Frame = None):
        super().__init__(parent)

        ### demo animal data ###
        animals = [ ('1', '26.45', '123456AV12', '1', '1'),
                    ('2','21.59', '654321QR07', '1', '2') 
        ]
        ##########################

        self.pad_x = 8
        self.pad_y = 18
        self.label_font = ("Arial", 13)

        self.num_cages = 0
        self.num_animals = 0

        self.grid(row=6, column=6, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=3, padx=self.pad_x, pady=self.pad_y)

        cage_label = Label(self, text='Number of\nCages', font=self.label_font)
        animal_label = Label(self, text='Number of Animals\nPer Cage', font=self.label_font)
        reset_label = Label(self, text='Reset Animal\nCages', font=self.label_font)

        cage_label.grid(row=1, column=0, padx=self.pad_x, pady=self.pad_y)
        animal_label.grid(row=1, column=2, padx=self.pad_x, pady=self.pad_y)
        reset_label.grid(row=3, column=0, padx=self.pad_x, pady=self.pad_y)

        self.num_cages_input = Entry(self, width=8, font=self.label_font)
        self.num_animal_input = Entry(self, width=8, font=self.label_font)
        self.animal_id = Entry(self, width=8, font=self.label_font)
        self.cage_id = Entry(self, width=8, font=self.label_font)    

        self.animal_id.insert(0, 'animal ID')
        self.cage_id.insert(0, 'cage ID')

        self.num_cages_input.grid(row=1, column=1, padx=self.pad_x, pady=self.pad_y)
        self.num_animal_input.grid(row=1, column=3, padx=self.pad_x, pady=self.pad_y)
        self.animal_id.grid(row=3, column=1, padx=self.pad_x, pady=self.pad_y)
        self.cage_id.grid(row=3, column=2, padx=self.pad_x, pady=self.pad_y)

        table = self.create_table(animals)
        table.grid(row=2, column=0, columnspan=6, padx=self.pad_x, pady=self.pad_y)

        set_button = Button(self, text='Set', width=15, command=lambda: self.set_cages())
        reset_button = Button(self, text='Reset', width=15, command=lambda: self.reset_cages())
        reset_all_button = Button(self, text='Reset All', width=15, command=lambda: self.reset_all_cages())
        save_button = Button(self, text='Save', width=15, command=lambda: self.save_cages('temp'))
        
        set_button.grid(row=1, column=5, padx=self.pad_x, pady=self.pad_y)
        reset_button.grid(row=3, column=3, padx=self.pad_x, pady=self.pad_y)
        reset_all_button.grid(row=4, column=3, padx=self.pad_x, pady=self.pad_y)
        save_button.grid(row=4, column=5, padx=self.pad_x, pady=self.pad_y)

        prev_button = NavigateButton(self, 'Previous', prev_page)
        next_button = NavigateButton(self, 'Next', next_page)
        prev_button.grid(row=5, column=0, columnspan=2, padx=self.pad_x, pady=self.pad_y, sticky=W)
        next_button.grid(row=5, column=5, columnspan=2, padx=self.pad_x, pady=self.pad_y, sticky=E)


        for i in range(0,5):
            if i < 4:
                self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)


    def raise_frame(frame: Frame):
        frame.tkraise()


    def create_table(self, animals: array):
        table = LabelFrame(self, height=200, width=(600 - self.pad_x*2), relief=RIDGE)
        table.grid(row=len(animals)+1, column=5)

        labels = ['ID', 'Animal Weight\n(pounds)', 'RFID', 'Group', 'Cage Number']
        for i in range(0, len(labels)):
            Label(table, text=labels[i], font=self.label_font, padding=15).grid(row=0, column=i)
            table.grid_columnconfigure(i, weight=1) 
            for animal in animals:
                Label(table, text=animal[i], font=self.label_font, padding=15).grid(
                    row=animals.index(animal)+1, column=i)
                table.grid_rowconfigure(i+1, weight=1)
        return table



    def set_cages(self):
        self.num_cages = self.num_cages_input.get()
        self.num_animals = self.num_animal_input.get()


    def reset_cages(self, animal_id, cage_id):
        # TO-DO implement
        return


    def reset_all_cages(self):
        # TO-DO implement
        return

    def save_cages(self, cages):
        # TO-DO : 
        #   save to file / database
        #   disable text fields, save button
        return


    def get_num_cages(self):
        return self.num_cages


    def get_num_animals(self):
        return self.num_animals



if __name__ == '__main__':
    root = Tk()
    root.title("Mouser")
    root.geometry('600x600')

    main_frame = CageSetupFrame(root, "Main").grid(sticky=E)
    frame = CageSetupFrame(root, main_frame)
    frame.raise_frame()

    root.mainloop()
###############################################################
