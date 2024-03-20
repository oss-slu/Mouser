'''Contains cage configuration page and behaviour.'''
from customtkinter import *
from tkcalendar import DateEntry
from shared.tk_models import *
from shared.scrollable_frame import ScrolledFrame
from databases.database_controller import DatabaseController
from shared.audio import AudioManager

#pylint: disable= undefined-variable
class CageConfigurationUI(MouserPage):
    '''The Frame that allows user to configure the cages.'''
    def __init__(self, database, parent: CTk, prev_page: CTkFrame = None):

        super().__init__(parent, "Group Configuration", prev_page)

        self.prev_page = prev_page
        self.db = DatabaseController(database)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.05, rely=0.20, relheight=0.75, relwidth=0.88)

        input_frame = CTkFrame(scroll_canvas)
        self.config_frame = CTkFrame(scroll_canvas)

        auto_button = CTkButton(input_frame, text='Randomize', width=15,
                            command= self.randomize)
        save_button = CTkButton(input_frame, text='Save', width=15,
                            command= self.save_to_database)
        move_button = CTkButton(input_frame, text='Move', width=15,
                            command= self.check_move_input)

        self.id_input = CTkEntry(input_frame, width=110)
        self.cage_input = CTkEntry(input_frame, width=110)

        self.id_input.insert(END, 'animal id')
        self.cage_input.insert(END, 'cage id')

        self.id_input.bind("<Button-1>", lambda arg='id': self.clear_entry(arg))
        self.cage_input.bind("<Button-1>", lambda arg='cage': self.clear_entry(arg))

        self.pad_x, self.pad_y = 10, 10
        self.calendar = DateEntry(input_frame, date_pattern='yyyy-mm-dd')
        self.calendar.grid(row=0, column=5, padx=self.pad_x, pady=self.pad_y)

        auto_button.grid(row=0, column=0, padx=self.pad_x, pady=self.pad_y)
        self.id_input.grid(row=0, column=1, padx=self.pad_x, pady=self.pad_y)
        self.cage_input.grid(row=0, column=2, padx=self.pad_x, pady=self.pad_y)
        move_button.grid(row=0, column=3, padx=self.pad_x, pady=self.pad_y)
        save_button.grid(row=0, column=4, padx=self.pad_x, pady=self.pad_y)

        for i in range(0, 5):
            input_frame.grid_columnconfigure(i, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        input_frame.pack(side=TOP, fill=X, anchor='center')
        self.config_frame.pack(side=TOP, fill=BOTH, anchor ='center')


        self.update_config_frame()


    def update_config_frame(self):
        '''updates the config frame to reflect new information.'''
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.create_group_frames()


    def create_group_frames(self):
        '''Initializes group frames from information in database.'''
        groups = self.db.get_groups()

        label_style = CTkFont("Arial", 12)

        for group in groups:
            group_frame = CTkFrame(self.config_frame, border_width=3, border_color="#00e7ff", bg_color='#0097A7')
            label = CTkLabel(group_frame, text=group, bg_color='#0097A7', font=label_style)
            label.pack(side=TOP, padx=self.pad_x, pady=self.pad_y, anchor='center')

            self.create_cage_frames(group, group_frame)
            #Only Necessary Change is the side of the frame.
            #From TOP to LEFT gives us the cage groups horizontally.
            group_frame.pack(side=LEFT, expand=TRUE, fill=BOTH, anchor='center')

    def create_cage_frames(self, group, group_frame):
        '''Initializes cage frames for given group and group frame
        from information in database.'''
        cages = self.db.get_cages_in_group(group)
        meas_items = self.db.get_measurement_items()


        for cage in cages:
            cage_frame = CTkFrame(group_frame, border_width=3, border_color="#00e7ff")
            CTkLabel(cage_frame, text='Cage ' + cage).pack(side=TOP, anchor='center')

            id_weight_label_frame = CTkFrame(cage_frame)

            CTkLabel(id_weight_label_frame, text='Animal ID').pack(side=LEFT, anchor='center')
            for item in meas_items:

                CTkLabel(id_weight_label_frame, text=item).pack(side=LEFT, anchor='center')

            id_weight_label_frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center')

            self.create_animal_frames(cage, cage_frame)

            cage_frame.pack(side=LEFT, expand=TRUE, fill=BOTH, anchor='center')

    def create_animal_frames(self, cage, cage_frame):
        '''Creates frames for animals from information in database.'''
        animals = self.db.get_animals_in_cage(cage)

        for animal in animals:

            animal_frame = CTkFrame(cage_frame, border_width=3, border_color="#00e7ff")

            id_measurement_frame = CTkFrame(animal_frame)

            CTkLabel(id_measurement_frame, text=animal, anchor='center').pack(
                        side=LEFT, expand=TRUE, fill=BOTH, anchor='e')

            CTkLabel(id_measurement_frame, text=self.db.get_animal_measurements(animal), anchor='center').pack(
                        side=LEFT, expand=TRUE, fill=BOTH, anchor='center')

            id_measurement_frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center')

            animal_frame.pack(side=TOP,
                       expand=TRUE,
                       fill=BOTH,
                       anchor='center',
                       padx= 5,
                       pady= 5,
                       ipadx= 5,
                       ipady= 5)

    def clear_entry(self, input_type):
        '''Clears entry from input frames.'''
        if input_type == 'id':
            self.id_input.delete(0, END)
        else:
            self.cage_input.delete(0, END)

    def randomize(self):
        '''Autosorts the animals into cages in group.'''
        self.db.autosort()
        self.update_config_frame()

    def move_animal(self, animal_id, new_cage):
        '''Moves animal id to new cage.'''
        old_cage = self.db.get_animal_current_cage(animal_id)
        self.db.update_animal_cage(animal_id, old_cage, new_cage)

        self.clear_entry('cage')
        self.clear_entry('id')
        self.id_input.insert(END, 'animal id')
        self.cage_input.insert(END, 'cage id')

        self.update_config_frame()

    def raise_warning(self, option: int):
        '''Raises a warning page.'''
        message = CTk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(False, False)

        if option == 1:
            label = CTkLabel(message, text='Animal ID and Cage ID must be integers.')

        elif option == 2:
            label = CTkLabel(message, text='Not a valid Animal ID.')

        elif option == 3:
            label = CTkLabel(message, text='Not a valid Cage ID.')

        elif option == 4:

            label = CTkLabel(message, text='Number of animals in a cage must not exceed '
                             + str(self.db.get_cage_max()))

        label.grid(row=0, column=0, padx=10, pady=10)

        ok_button = CTkButton(message, text="OK", width=10,
                        command= lambda: [message.destroy()])
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        AudioManager.play(filepath='sounds/error.wav')

        message.mainloop()

    def check_move_input(self):
        '''Checks to see if the animal and cage inputs are valid
        and raises a warning if any issues occur.'''
        animal = self.id_input.get()
        cage = self.cage_input.get()

        valid_animal = self.db.check_valid_animal(animal)
        valid_cage = self.db.check_valid_cage(cage)

        if animal == '' or cage == '':
            self.raise_warning(1)

        elif not isinstance(int(animal), int) or not isinstance(int(cage), int):
            self.raise_warning(1)

        elif not valid_animal:
            self.raise_warning(2)

        elif not valid_cage:
            self.raise_warning(3)

        elif isinstance(int(animal), int) and isinstance(int(cage), int) and valid_animal and valid_cage:
            self.move_animal(animal, cage)

    def check_num_in_cage_allowed(self):
        '''Checks if the number of animals in a cage is allowed.'''
        return self.db.check_num_in_cage_allowed()

    def update_controller_attributes(self):
        '''Resets attributes in the database.'''
        self.db.reset_attributes()

    def save_to_database(self):
        '''Saves updated values to database.'''
        if self.check_num_in_cage_allowed():
            self.db.update_experiment()
            raise_frame(self.prev_page)
        else:
            self.raise_warning(4)

    def close_connection(self):
        '''Closes database file.'''
        self.db.close()
