from operator import ne
from tkinter import *
from tkinter.ttk import *

from NavigateButton import NavigateButton
from ScrollableFrame import ScrollableFrame

class GroupSetupPage(Frame):
    def __init__(self, parent: Tk, prev_page: Frame = None, next_page: Frame = None):
        super().__init__(parent)
        self.prev_page = prev_page
        self.next_page = next_page

        self.group_names = []

        self.pad_x = 10
        self.pad_y = 20
        self.label_font = ("Arial", 13)
        self.text_width = 20

        self.grid(row=5, column=4, sticky='NSEW')

        title_label = Label(self, text='Experiment Setup', font=("Arial", 25))
        groups_label = Label(self, text='Numbers of Groups', font=self.label_font)
        title_label.grid(row=0, column=1, columnspan=2, padx=self.pad_x, pady=self.pad_y, sticky='E')
        groups_label.grid(row=1, column=0, padx=self.pad_x, pady=self.pad_y)

        check_button_frame = Frame(self, width=20, height=1)
        check_button_frame.grid(row=1, column=1, padx=self.pad_x, pady=self.pad_y)
        self.auto_button = Checkbutton(check_button_frame, text='Auto', takefocus=0)
        self.manual_button = Checkbutton(check_button_frame, text='Manual', takefocus=1)
        self.auto_button.grid(row=0, column=0, padx=self.pad_x, pady=self.pad_y)
        self.manual_button.grid(row=0, column=1, padx=self.pad_x, pady=self.pad_y)

        group_num = Entry(self, width=8, font=self.label_font)
        group_num.grid(row=1, column=2, padx=self.pad_x, pady=self.pad_y)

        set_button = Button(self, text='Set', width=15, command=lambda: self.create_groups(int(group_num.get())))
        set_button.grid(row=1, column=4, padx=self.pad_x, pady=self.pad_y)

        prev_button = NavigateButton(self, 'Previous', self.prev_page)
        next_button = NavigateButton(self, 'Next', self.next_page)
        prev_button.grid(row=4, column=0, columnspan=2, padx=self.pad_x, pady=self.pad_y, sticky=W)
        next_button.grid(row=4, column=3, columnspan=2, padx=self.pad_x, pady=self.pad_y)




    def raise_frame(frame: Frame):
        frame.tkraise()


    def create_groups(self, num: int):
        scroll_frame = ScrollableFrame(self, num)
        scroll_frame.grid(row=2, column=0, columnspan=3, padx=self.pad_x, pady=self.pad_y)

        # TO-DO : write getter funct in this class or scrollframe text input
        save_button = Button(self, text='Save', width=15, command=lambda: self.save_names('temp'))
        save_button.grid(row=2, column=3, columnspan=2, padx=self.pad_x, pady=self.pad_y, sticky=S)


        ### TO-DO : fix scroll window so that it stays same height ###
        ### potential start to solution ###

        # canvas = Canvas(self)
        # bar = Scrollbar(self, orient='vertical', command=canvas.yview)
        # bar.grid(row=2, column=0, columnspan=2, padx=self.pad_x, pady=self.pad_y)
        # scroll_frame = Frame(canvas)
        # scroll_frame.grid(row=2, column=0, columnspan=2, padx=self.pad_x, pady=self.pad_y)
        # for i in range(0,num):
        #     label = Label(canvas, text=('Group ' + str(i+1)), font=self.label_font)
        #     label.grid(row=i, column=0, padx=self.pad_x, pady=self.pad_y)

        #     text = Entry(canvas, width=self.text_width, font=self.label_font)
        #     text.grid(row=i, column=1, padx=self.pad_x, pady=self.pad_y)
        #     self.group_names.append(text.get())


    def save_names(self, names):
        # TO-DO : 
        #   save to file / database
        #   disable text fields, set button, save button
        return




###############################################################
# for demo purposes - remove once everything is all connected #

if __name__ == '__main__':
    root = Tk()
    root.title("Mouser")
    root.geometry('600x600')

    main_frame = GroupSetupPage(root, "Main").grid(sticky=E)
    frame = GroupSetupPage(root, main_frame)
    frame.raise_frame()

    root.mainloop()
###############################################################