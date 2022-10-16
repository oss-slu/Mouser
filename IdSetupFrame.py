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
        
        self.id_list = [1, 2]

        # Grid Items
        self.pad_x = 10
        self.pad_y = 20
        self.label_font = ("Arial", 13)
        self.text_width = 15

        self.grid(row=5, column=4, sticky='NESW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        title_label.grid(row=0, column=1, columnspan=2, padx=self.pad_x, pady=self.pad_y, sticky='E')

        rfid_label = Label(self, text='RFID', font=self.label_font).grid(row=1, column=0, padx=self.pad_x, pady=self.pad_y, sticky=W)
        id_label = Label(self, text='IDs', font=self.label_font).grid(row=2, column=0, padx=self.pad_x, pady=self.pad_y, sticky=W)
        weight_label = Label(self, text='Animal Weight', font=self.label_font).grid(row=1, column=2, padx=self.pad_x, pady=self.pad_y, sticky=W)

        self.rfid_text = Text(self, height=1, width=self.text_width, font=self.label_font).grid(row=1, column=1, padx=self.pad_x, pady=self.pad_y)
        self.weight_text = Text(self, height=1, width=self.text_width, font=self.label_font).grid(row=1, column=3, padx=self.pad_x, pady=self.pad_y)


        # TO-DO : if self.id_auto_button is checked disable text box
        self.id_text = Text(self, height=1, width=self.text_width, font=self.label_font).grid(row=2, column=2, padx=self.pad_x, pady=self.pad_y)
        

        check_button_frame = Frame(self, width=20, height=1)
        check_button_frame.grid(row=2, column=1, padx=self.pad_x, pady=self.pad_y)
        self.id_auto_button = Checkbutton(check_button_frame, text='Auto', takefocus=1).grid(row=0, column=0, padx=self.pad_x, pady=self.pad_y)
        self.id_manual_button = Checkbutton(check_button_frame, text='Manual', takefocus=0).grid(row=0, column=1, padx=self.pad_x, pady=self.pad_y)
     
        

        # Table Frame Items
        self.id_table = self.create_table(self.id_list)
        self.id_table.grid(row=3, column=0, columnspan=4)
        

        # buttons
        add_button = Button(self, text='Add', width=15, command=lambda: self.add_id()).grid(row=2, column=3, padx=self.pad_x, pady=self.pad_y)
        sort_buton = Button(self, text='Sort by Weight', width=15, command=lambda: self.sort_table()).grid(row=4, column=3, padx=self.pad_x, pady=self.pad_y)
        prev_button = NavigateButton(self, 'Previous', self.prev_page).grid(row=5, column=0, columnspan=2, padx=self.pad_x, pady=self.pad_y)
        next_button = NavigateButton(self, 'Next', self.next_page).grid(row=5, column=3, columnspan=2, padx=self.pad_x, pady=self.pad_y)


        for i in range (0,5):
            if i==3:
                self.grid_rowconfigure(i, weight=5)
            else:
                self.grid_rowconfigure(i, weight=1)
                self.grid_columnconfigure(i, weight=1)



    def raise_frame(frame: Frame):
        frame.tkraise()


    # TO-DO : connect to data & add
    def add_id():
        return


    # TO-DO : connect to data
    def create_table(self, ids):
        table = LabelFrame(self, height=200, width=(600 - self.pad_x*2), relief=RIDGE)
        table.grid(row=len(ids)+1, column=4)

        labels = ['ID (auto generated)', 'Animal Weight (pounds)', 'RFID', 'Comments']
        for i in range(0,len(labels)):
            Label(table, text=labels[i], font=self.label_font, padding=5).grid(row=0, column=i)

        for i in range(0,len(self.id_list)+1):
            if i>0:
                Label(table, text=str(self.id_list[i-1]), font=self.label_font, padding=5).grid(row=i, column=0)
            table.grid_rowconfigure(i, weight=1)

        for i in range(0,3):
            table.grid_columnconfigure(i, weight=1)

        return table


    # TO-DO : connect to data and sort
    def sort_table(self, data):
        # call create_table again with new sorted array of data
        return 




###############################################################
# for demo purposes - remove once everything is all connected #

if __name__ == '__main__':
    root = Tk()
    root.title("Mouser")
    root.geometry('600x600')

    main_frame = IdSetupFrame(root, "Main").grid(sticky=E)
    frame = IdSetupFrame(root, main_frame)
    frame.raise_frame()

    root.mainloop()
###############################################################