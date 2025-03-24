'''New Experiment Module'''
from os.path import *
from customtkinter import *
from shared.tk_models import *
from shared.scrollable_frame import ScrolledFrame
from experiment_pages.experiment.group_config_ui import GroupConfigUI
from shared.experiment import Experiment
from shared.audio import AudioManager


class NewExperimentUI(MouserPage):# pylint: disable= undefined-variable
    '''New Experiment user interface.'''
    def __init__(self, parent: CTk, menu_page: CTkFrame = None):

        super().__init__(parent, "New Experiment", menu_page)
        self.input = Experiment()

        self.next_page = GroupConfigUI(self.input, parent, self, menu_page)
        self.set_next_button(self.next_page)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.12, rely=0.25, relheight=0.75, relwidth=0.88)

        self.main_frame = CTkFrame(scroll_canvas)
        self.main_frame.grid(row=10, column=3, sticky='NESW')

        self.invest_frame = CTkFrame(self.main_frame, height=0)
        self.item_frame = CTkFrame(self.main_frame, height=0)
        self.rfid_frame = CTkFrame(self.main_frame, height=0)

        self.invest_frame.grid(row=2, column=1, sticky='NESW')
        self.item_frame.grid(row=5, column=1, sticky='NESW')
        self.rfid_frame.grid(row=6, column=1, sticky='NESW')

        pad_x = 10
        pad_y = 10

        self.items = ''
        self.added_invest = []

        CTkLabel(self.main_frame, text='Experiment Name').grid(
                        row=0, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="Password").grid(
                        row=0, column=2, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text='Investigators').grid(
                     row=1, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text='Species').grid(
                       row=3, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text='Measurement Items').grid(
                      row=4, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="RFID").grid(
                      row=6, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="Number of Animals").grid(
                       row=7, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="Number of Groups").grid(
                       row=8, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame,text="Max Animals per Cage").grid(
                      row=9, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="Measurements per Day").grid(
                      row=10, column=0, sticky=W, padx=pad_x, pady=pad_y)

        self.exper_name = CTkEntry(self.main_frame, width=140)
        self.password = CTkEntry(self.main_frame,width=120,show="*")
        self.investigators = CTkEntry(self.main_frame, width=140)
        self.species = CTkEntry(self.main_frame, width=140)

        self.measure_items = CTkEntry(self.main_frame, width=140)

        self.animal_num = CTkEntry(self.main_frame, width=110)
        self.group_num = CTkEntry(self.main_frame, width=110)
        self.num_per_cage = CTkEntry(self.main_frame, width=110)
        
        self.daily_freq = CTkEntry(self.main_frame, width=110)
        self.daily_freq.insert(0, "1")  # Default value

        self.exper_name.grid(row=0, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.password.grid(row=0,column=3, sticky=W, padx=pad_x,pady=pad_y)
        self.investigators.grid(row=1, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.species.grid(row=3, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.measure_items.grid(row=4, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.animal_num.grid(row=7, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.group_num.grid(row=8, column=1, sticky=W, padx=pad_x, pady=pad_y)
        self.num_per_cage.grid(row=9, column=1, sticky=W, padx=pad_x, pady=pad_y)

        self.daily_freq.grid(row=10, column=1, sticky=W, padx=pad_x, pady=pad_y)


        self.rfid = BooleanVar()

        CTkRadioButton(self.rfid_frame, text='Yes', variable=self.rfid, value=1).grid(row=0, column=0,
                    padx=pad_x, pady=pad_y)
        CTkRadioButton(self.rfid_frame, text='No', variable=self.rfid, value=0).grid(row=0, column=1,
                    padx=pad_x, pady=pad_y)

        add_invest_button = CTkButton(self.main_frame, text='+', width=3,
                              command=lambda: [self.add_investigator(), self.investigators.delete(0, END)])
        add_invest_button.grid(row=1, column=2, padx=pad_x, pady=pad_y)

        # add_item_button = CTkButton(self.main_frame, text='+', width=3,
        #                     command= lambda: [self.add_measurement_item(), self.measure_items.delete(0, END)])
        # add_item_button.grid(row=4, column=2, padx=pad_x, pady=pad_y)

        for i in range(0,10):
            if i < 3:
                self.main_frame.grid_columnconfigure(i, weight=1)
            self.main_frame.grid_rowconfigure(i, weight=1)

        self.bind_all_entries()

    def bind_all_entries(self):
        self.exper_name.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.password.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.species.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.measure_items.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.animal_num.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.group_num.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.num_per_cage.bind("<KeyRelease>", lambda event: self.enable_next_button())

    def enable_next_button(self):
        if self.exper_name.get() and self.species.get() \
                and self.animal_num.get() and self.group_num.get() and self.num_per_cage.get() \
                and ((self.added_invest or self.investigators.get()) and (self.items or self.measure_items.get())):
            self.next_button.configure(state="normal")
            print("Button enabled")
        else:
            self.next_button.configure(state="disabled")
            print("Button disabled.")

    def set_next_button(self, next_page):
        '''Sets what page the next button navigates to.'''
        #pylint: disable = access-member-before-definition
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)#pylint: disable= undefined-variable
        #pylint: enable= access-member-before-definition
        self.next_button.configure(command= lambda: [self.check_animals_divisible(), self.next_button.navigate()], state="disabled")
        self.next_button.place(relx=0.85, rely=0.15)

    def update_invest_frame(self):
        '''Updates investigator frame.'''
        for widget in self.invest_frame.winfo_children():
            widget.destroy()

        funcs = []
        buttons = []
        for investigator in self.added_invest:
            CTkLabel(self.invest_frame, text=investigator).grid(row=self.added_invest.index(investigator),
                    column=1, sticky=W, padx=10)
            rem_button = CTkButton(self.invest_frame, text='-', width=3)
            rem_button.grid(row=self.added_invest.index(investigator), column=2, padx=10)
            buttons.append(rem_button)
            funcs.append(lambda x=investigator: self.remove_investigator(x))

        index = 0
        for f in funcs:
            buttons[index].configure(command=f)
            index += 1


    def get_user_list(self):
        '''Gets list of users in user database.'''
        users = self.users_database.get_all_users()
        user_list = []
        for user in users:
            user_list.append(user[1] + " (" + user[3] + ")")
        return user_list

    def add_investigator(self):
        if self.investigators.get() and self.investigators.get() not in self.added_invest:

            self.added_invest.append(self.investigators.get())
            self.update_invest_frame()

    def remove_investigator(self, person):
        '''Removes the passed investigator from the investigator frame.'''
        if person in self.added_invest:
            self.added_invest.remove(person)
            self.update_invest_frame()


    def raise_warning(self, option: int):
        '''Raises an error window that can be dismissed with any key or mouse press.'''

        def dismiss_warning(event=None):
            '''Destroy the warning window when triggered.'''
            print(f"Event triggered: {event}")  # Debugging to confirm key press is detected
            message.destroy()

        # Create the warning window
        message = CTk()
        message.title("WARNING")
        message.geometry('320x180')
        message.resizable(True, True)

        # Add the appropriate warning message based on the option
        if option == 1:
            label = CTkLabel(message, text='Number of animals must be divisible by number groups.')
            label.grid(row=0, column=0, padx=10, pady=10)
        elif option == 2:
            label1 = CTkLabel(message, text='Number of animals, groups, or maximum')
            label2 = CTkLabel(message, text='animals per cage must be greater than 0.')
            label1.grid(row=0, column=0, padx=10)
            label2.grid(row=1, column=0, padx=10)
        elif option == 3:
            label3 = CTkLabel(message, text='Experiment name used. Please use another name.')
            label3.grid(row=0, column=0, padx=10, pady=10)
        elif option == 4:
            label4 = CTkLabel(message, text='''Unequal Group Size: Please allow the total number of animals to be
            less than or equal to the total number of
            animals allowed in all combined cages''')
            label4.grid(row=0, column=0, padx=10, pady=10)

        # Play the error sound
        AudioManager.play("sounds/error.wav")

        # Bind key and mouse events to dismiss the warning
        message.bind("<KeyPress>", dismiss_warning)  # Captures any key press
        message.bind("<Button>", dismiss_warning)   # Captures any mouse click

        # Add an OK button for manual dismissal (as fallback)
        ok_button = CTkButton(message, text="OK", width=10, command=dismiss_warning)
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        # Ensure the warning window grabs focus
        message.focus_force()

        # Start the event loop
        message.mainloop()


    def check_animals_divisible(self):
        '''If the total number of animals is greater than the total number
        of animals allowed in all combined cages, raise warning.'''

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
        '''Saves experiment to a file.'''
        self.input.set_name(self.exper_name.get())
        if self.password.get():
            self.input.set_password(self.password.get())
        self.input.set_unique_id()
        self.input.set_investigators(self.added_invest)
        self.input.set_species(self.species.get())
        self.input.set_measurement_item(self.measure_items.get())
        self.input.set_uses_rfid(self.rfid.get())
        self.input.set_num_animals(self.animal_num.get())
        self.input.set_num_groups(self.group_num.get())
        self.input.set_max_animals(self.num_per_cage.get())
        self.input.set_animals_per_group(int(self.animal_num.get()) / int(self.group_num.get()))
        self.input.set_daily_frequency(self.daily_freq.get())

        self.next_page.update_page()
