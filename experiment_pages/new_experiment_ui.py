from tkinter import *
from tkinter.ttk import *
from tk_models import *
from os.path import *
from scrollable_frame import ScrolledFrame
from experiment_pages.group_config_ui import GroupConfigUI
from experiment_pages.experiment import Experiment
from database_apis.users_database import UsersDatabase
from audio import AudioManager

class NewExperimentUI(MouserPage):
    def __init__(self, parent:Tk, menu_page: Frame = None):
        super().__init__(parent, "New Experiment", menu_page)

        self.input = Experiment()
        self.users_database = UsersDatabase()

        self.next_page = GroupConfigUI(self.input, parent, self, menu_page)
        self.set_next_button(self.next_page)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.12, rely=0.25, relheight=0.75, relwidth=0.88)

        self.main_frame = Frame(scroll_canvas)
        self.main_frame.grid(row=10, column=3, sticky='NESW')

        self.invest_frame = Frame(self.main_frame)
        self.item_frame = Frame(self.main_frame)
        self.rfid_frame = Frame(self.main_frame)

        self.invest_frame.grid(row=2, column=1, sticky='NESW')
        self.item_frame.grid(row=5, column=1, sticky='NESW')
        self.rfid_frame.grid(row=6, column=1, sticky='NESW')

        pad_x = 10
        pad_y = 10

        self.items = []
        self.added_invest = []

        Label(self.main_frame, text='Experiment Name').grid(row=0, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text='Investigators').grid(row=1, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text='Species').grid(row=3, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text='Measurement Items').grid(row=4, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text="RFID").grid(row=6, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text="Number of Animals").grid(row=7, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text="Number of Groups").grid(row=8, column=0, sticky=W, padx=pad_x, pady=pad_y)
        Label(self.main_frame, text="Max Animals per Cage").grid(row=9, column=0, sticky=W, padx=pad_x, pady=pad_y)

        self.exper_name = Entry(self.main_frame, width=40)
        self.investigators = Combobox(self.main_frame, values=self.get_user_list(), width=37)
        self.species = Entry(self.main_frame, width=40)
        self.measure_items = Entry(self.main_frame, width=40)
        self.animal_num = Entry(self.main_frame, width=10)
        self.group_num = Entry(self.main_frame, width=10)
        self.num_per_cage = Entry(self.main_frame, width=10)

        self.exper_name.grid(row=0, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.investigators.grid(row=1, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.species.grid(row=3, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.measure_items.grid(row=4, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.animal_num.grid(row=7, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.group_num.grid(row=8, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.num_per_cage.grid(row=9, column=1, sticky=W, padx=pad_x, pady=pad_y)

        self.rfid = BooleanVar()
        Radiobutton(self.rfid_frame, text='Yes', variable=self.rfid, val=True).grid(row=0, column=0, 
                    padx=pad_x, pady=pad_y)
        Radiobutton(self.rfid_frame, text='No', variable=self.rfid, val=False).grid(row=0, column=1, 
                    padx=pad_x, pady=pad_y)

        add_invest_button = Button(self.main_frame, text='+', width=3, 
                            command= lambda: self.add_investigator())
        add_invest_button.grid(row=1, column=2, padx=pad_x, pady=pad_y)

        add_item_button = Button(self.main_frame, text='+', width=3, 
                            command= lambda: [self.add_measuremnt_item(), self.measure_items.delete(0, END)])
        add_item_button.grid(row=4, column=2, padx=pad_x, pady=pad_y)
        
        
        for i in range(0,10):
            if i < 3:
                self.main_frame.grid_columnconfigure(i, weight=1)
            self.main_frame.grid_rowconfigure(i, weight=1)


    def set_next_button(self, next_page):
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)
        self.next_button.configure(command= lambda: [self.check_animals_divisible(), self.next_button.navigate()])
        self.next_button.place(relx=0.85, rely=0.15)


    def update_invest_frame(self):
        for widget in self.invest_frame.winfo_children():
            widget.destroy()

        funcs = []
        buttons = []
        for investigator in self.added_invest:
            Label(self.invest_frame, text=investigator).grid(row=self.added_invest.index(investigator), 
                    column=1, sticky=W, padx=10)
            rem_button = Button(self.invest_frame, text='-', width=3)
            rem_button.grid(row=self.added_invest.index(investigator), column=2, padx=10)
            buttons.append(rem_button)
            funcs.append(lambda x=investigator: self.remove_investigator(x))

        index = 0
        for f in funcs:
            buttons[index].configure(command=f)
            index += 1


    def update_items_frame(self):
        for widget in self.item_frame.winfo_children():
            widget.destroy()

        funcs = []
        buttons = []
        for meas_item in self.items:
            Label(self.item_frame, text=meas_item).grid(
                            row=self.items.index(meas_item), column=0, sticky=W, padx=10)
            rem_button = Button(self.item_frame, text='-', width=3)
            rem_button.grid(row=self.items.index(meas_item), column=2, sticky=W, padx=10)
            buttons.append(rem_button)
            funcs.append(lambda meas_item=meas_item: self.remove_measurment_item(meas_item))

        index = 0
        for f in funcs:
            buttons[index].configure(command=f)
            index += 1


    def get_user_list(self):
        users = self.users_database.get_all_users()
        user_list = []
        for user in users:
            user_list.append(user[1] + " (" + user[3] + ")")
        return user_list


    def add_investigator(self):
        if self.investigators.get() not in self.added_invest and self.investigators.get() != '':
            self.added_invest.append(self.investigators.get())
            self.update_invest_frame()


    def remove_investigator(self, person):
        if person in self.added_invest:
            self.added_invest.remove(person)
            self.update_invest_frame()


    def add_measuremnt_item(self):
        if self.measure_items.get() not in self.items and self.measure_items.get() != '':
            self.items.append(self.measure_items.get())
            self.update_items_frame()


    def remove_measurment_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.update_items_frame()


    def raise_warning(self, option: int):
        message = Tk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(True, True)

        if option == 1:
            label = Label(message, text='Number of animals must be divisible by number groups.')
            label.grid(row=0, column=0, padx=10, pady=10)
        elif option == 2:
            label1 = Label(message, text='Number of animals, groups, or maximum')
            label2 = Label(message, text='animals per cage must be greater than 0.')
            label1.grid(row=0, column=0, padx=10)
            label2.grid(row=1, column=0, padx=10)
        elif option == 3:
            label3 = Label(message, text='Experiment name used. Please use other name.')
            label3.grid(row=0, column=0, padx=10, pady=10)
        elif option == 4:
            label4 = Label(message, text='Unequal Group Size: Please allow the total number of animals to be less than or equal to the total number of animals allowed in all combined cages')
            label4.grid(row=0, column=0, padx=10, pady=10)
        
        AudioManager.play("sounds/error.wav")

        ok_button = Button(message, text="OK", width=10, 
                        command= lambda: [message.destroy()])
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        message.mainloop()


    def check_animals_divisible(self):
        #If the total number of animals is greater than the total number of animals allowed in all combined cages, raise warning. Fixes Issue #108.
        if int(self.animal_num.get()) > (int(self.group_num.get()) * int(self.num_per_cage.get())):
            self.raise_warning(4)
        elif self.animal_num.get() == '' or self.group_num.get() == '' or self.animal_num.get() == '': 
            self.raise_warning(2)
        elif int(self.animal_num.get()) % int(self.group_num.get()) != 0:
            self.raise_warning(1)
        elif int(self.animal_num.get()) == 0 or int(self.group_num.get()) == 0 or int(self.animal_num.get()) == 0:
            self.raise_warning(2)
        elif int(self.group_num.get()) * int(self.num_per_cage.get()) > int(self.animal_num.get()):
            self.raise_warning(1)
        elif int(self.animal_num.get()) % int(self.group_num.get()) == 0 and int(self.animal_num.get()) != 0:
            self.save_input()

    def save_input(self):
        self.input.set_name(self.exper_name.get())
        self.input.set_unique_id()
        self.input.set_investigators(self.added_invest)
        self.input.set_species(self.species.get())
        self.input.set_measurement_items(self.items)
        self.input.set_uses_rfid(self.rfid.get())
        self.input.set_num_animals(self.animal_num.get())
        self.input.set_num_groups(self.group_num.get())
        self.input.set_max_animals(self.num_per_cage.get())
        self.input.set_animals_per_group(int(self.animal_num.get()) / int(self.group_num.get()))

        self.next_page.update_page()

        
