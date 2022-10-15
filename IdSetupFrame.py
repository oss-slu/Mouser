from tkinter import *
from tkinter.ttk import *

from NavigateButton import NavigateButton

class IdSetupFrame(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None, next_page: Frame = None):
        super().__init__(parent)
        self.prev_page = prev_page
        self.next_page = next_page

        # vars for input
        self.rfid = 0
        self.id = 0
        self.weight = 0
        
        pad_x = 10
        pad_y = 20
        label_font = ("Arial", 13)

        self.grid(row=5, column=5, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=3, padx=pad_x, pady=pad_y, sticky=N)

        rfid_label = Label(self, text='RFID', font=label_font).grid(row=1, column=0, padx=pad_x, pady=pad_y, sticky=W)
        id_label = Label(self, text='IDs', font=label_font).grid(row=2, column=0, padx=pad_x, pady=pad_y, sticky=W)
        weight_label = Label(self, text='Animal Weight', font=label_font).grid(row=1, column=2, padx=pad_x, pady=pad_y, sticky=W)

        self.rfid_text = Text(self, height=1, width=20, font=label_font).grid(row=1, column=1, padx=pad_x, pady=pad_y)
        self.weight_text = Text(self, height=1, width=20, font=label_font).grid(row=1, column=3, padx=pad_x, pady=pad_y)


        # TO-DO : if self.id_auto_button is checked disable text box
        self.id_text = Text(self, height=1, width=12, font=label_font).grid(row=2, column=2, padx=pad_x, pady=pad_y)



        check_button_frame = Frame(self, width=20, height=1)
        check_button_frame.grid(row=2, column=1, padx=pad_x, pady=pad_y)
        self.id_auto_button = Checkbutton(check_button_frame, text='Auto').grid(row=0, column=0, padx=pad_x, pady=pad_y)
        self.id_manual_button = Checkbutton(check_button_frame, text='Manual').grid(row=0, column=1, padx=pad_x, pady=pad_y)
        

        self.table = Frame()


        add_button = Button(self, text='Add', width=15, command=lambda: self.add_id()).grid(row=2, column=3, padx=pad_x, pady=pad_y)
        prev_button = NavigateButton(self, 'Previous', self.prev_page).grid(row=5, column=0, columnspan=2, padx=pad_x, pady=pad_y)
        next_button = NavigateButton(self, 'Next', self.next_page).grid(row=5, column=3, columnspan=2, padx=pad_x, pady=pad_y)



        for i in range (0,4):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)


    def raise_frame(frame: Frame):
        frame.tkraise()

    def add_id():
        return


###############################################################
# for demo purposes - remove once everything is all connected #

if __name__ == '__main__':
    root = Tk()
    root.title("Mouser")
    root.geometry('600x600')

    main_frame = IdSetupFrame(root, "Main")
    frame = IdSetupFrame(root, main_frame)
    frame.raise_frame()

    root.mainloop()
###############################################################