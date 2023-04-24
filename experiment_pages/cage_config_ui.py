from tkinter import *
from tkinter.ttk import *
from tk_models import *
from scrollable_frame import ScrolledFrame
from database_controller import DatabaseController


class CageConfigurationUI(MouserPage):
    def __init__(self, database, parent: Tk, prev_page: Frame = None):
        super().__init__(parent, "Group Configuration", prev_page)

        self.prev_page = prev_page
        self.db = DatabaseController(database)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.05, rely=0.20, relheight=0.75, relwidth=0.88)

        input_frame = Frame(scroll_canvas)
        self.config_frame = Frame(scroll_canvas, relief=RIDGE)

        auto_button = Button(input_frame, text='Auto Group', width=15, 
                            command= lambda: self.auto_group())
        save_button = Button(input_frame, text='Save', width=15, 
                            command= lambda: self.save_to_database())
        move_button = Button(input_frame, text='Move', width=15, 
                            command= lambda: self.check_move_input())

        self.id_input = Entry(input_frame, width=10)
        self.cage_input = Entry(input_frame, width=10)

        self.id_input.insert(END, 'animal id')
        self.cage_input.insert(END, 'cage id')

        self.id_input.bind("<Button-1>", lambda event, arg='id': self.clear_entry(event, arg))
        self.cage_input.bind("<Button-1>", lambda event, arg='cage': self.clear_entry(event, arg))

        self.pad_x, self.pad_y = 10, 10

        auto_button.grid(row=0, column=0, padx=self.pad_x, pady=self.pad_y)
        self.id_input.grid(row=0, column=1, padx=self.pad_x, pady=self.pad_y)
        self.cage_input.grid(row=0, column=2, padx=self.pad_x, pady=self.pad_y)
        move_button.grid(row=0, column=3, padx=self.pad_x, pady=self.pad_y)
        save_button.grid(row=0, column=4, padx=self.pad_x, pady=self.pad_y)

        for i in range(0, 4):
            input_frame.grid_columnconfigure(i, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        input_frame.pack(side=TOP, expand=TRUE, anchor='center')
        self.config_frame.pack(side=TOP, expand=TRUE, anchor='center')

        self.update_config_frame()


    def update_config_frame(self):
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.create_group_frames()
        

    def create_group_frames(self):
        groups = self.db.get_groups()

        frame_style, label_style = Style(), Style()
        frame_style.configure('GroupFrame.TFrame', background='#0097A7')
        label_style.configure('GroupLabel.TLabel', background='#0097A7', font=('Arial', 12))

        for group in groups:
            frame = Frame(self.config_frame, borderwidth=3, relief='groove', style='GroupFrame.TFrame')
            label = Label(frame, text=group, style='GroupLabel.TLabel')
            label.pack(side=TOP, padx=self.pad_x, pady=self.pad_y, anchor='center')
            
            self.create_cage_frames(group, frame)
            frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center')
           

    def create_cage_frames(self, group, group_frame):
        cages = self.db.get_cages_in_group(group)
        meas_items = self.db.get_measurement_items()

        for i in range (0, len(cages)):
            frame = Frame(group_frame, borderwidth=3, relief='groove')
            Label(frame, text='Cage ' + cages[i]).pack(side=TOP, anchor='center')
            
            id_weight_label_frame = Frame(frame)

            Label(id_weight_label_frame, text='Animal ID').pack(side=LEFT, anchor='center')
            for item in meas_items:
                Label(id_weight_label_frame, text=item).pack(side=LEFT, anchor='center')
            
            id_weight_label_frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center')

            self.create_animal_frames(cages[i], frame)
            
            frame.pack(side=LEFT, expand=TRUE, fill=BOTH, anchor='center')

       
    def create_animal_frames(self, cage, cage_frame):
        animals = self.db.get_animals_in_cage(cage)

        for animal in animals:
            frame = Frame(cage_frame, borderwidth=3, relief='groove')
            
            id_measurement_frame = Frame(frame)

            Label(id_measurement_frame, text=animal, anchor='center').pack(
                        side=LEFT, expand=TRUE, fill=BOTH, anchor='e')
            Label(id_measurement_frame, text=self.db.get_animal_measurements(animal), anchor='center').pack(
                        side=LEFT, expand=TRUE, fill=BOTH, anchor='center')

            id_measurement_frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center')

            frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center', padx= 5, pady= 5, ipadx= 5, ipady= 5) 


    def clear_entry(self, event, input):
        if input == 'id':
            self.id_input.delete(0, END)
        else:
            self.cage_input.delete(0, END)


    def auto_group(self):
        self.db.autosort()
        self.update_config_frame()

    
    def move_animal(self, id, new_cage):
        old_cage = self.db.get_animal_current_cage(id)
        self.db.update_animal_cage(id, old_cage, new_cage)
        
        self.clear_entry(None, 'cage')
        self.clear_entry(None, 'id')
        self.id_input.insert(END, 'animal id')
        self.cage_input.insert(END, 'cage id')

        self.update_config_frame()


    def raise_warning(self, option: int):
        message = Tk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(False, False)

        if option == 1:
            label = Label(message, text='Animal ID and Cage ID must be integers.')

        elif option == 2:
            label = Label(message, text='Not a valid Animal ID.')

        elif option == 3:
            label = Label(message, text='Not a valid Cage ID.')

        elif option == 4:
            label = Label(message, text='Number of animals in a cage must not exceed '+ str(self.db.get_cage_max()))

        label.grid(row=0, column=0, padx=10, pady=10)

        ok_button = Button(message, text="OK", width=10, 
                        command= lambda: [message.destroy()])
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        message.mainloop()


    def check_move_input(self):
        animal = self.id_input.get()
        cage = self.cage_input.get()

        valid_animal = self.db.check_valid_animal(animal)
        valid_cage = self.db.check_valid_cage(cage)        

        if animal == '' or cage == '':
            self.raise_warning(1)

        elif isinstance(int(animal), int) == False or isinstance(int(cage), int) == False:
            self.raise_warning(1)

        elif valid_animal == False:
            self.raise_warning(2)

        elif valid_cage == False:
            self.raise_warning(3)

        elif isinstance(int(animal), int) and isinstance(int(cage), int) and valid_animal and valid_cage: 
            self.move_animal(animal, cage)


    def check_num_in_cage_allowed(self):
        return self.db.check_num_in_cage_allowed()


    def update_controller_attributes(self):
        self.db.reset_attributes()


    def save_to_database(self):
        if self.check_num_in_cage_allowed() == True:
            self.db.update_experiment()
            self.prev_page.tkraise()
        else:
            self.raise_warning(4)
