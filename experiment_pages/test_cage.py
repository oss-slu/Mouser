from tkinter import *
from tkinter.ttk import *
from tk_models import *
from scrollable_frame import ScrolledFrame
# from ExperimentDatabase import ExperimentDatabase

from database_controller import DatabaseController



class CageConfigurationUI(MouserPage):
    def __init__(self, database, parent: Tk, prev_page: Frame = None):
        super().__init__(parent, "Group Configuration", prev_page)

        # file = str(database) + '.db'
        # self.db = ExperimentDatabase(file)

        # self.groups = self.db.get_all_groups()

        #############################################

        self.db = DatabaseController(database)

        #############################################

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

        pad_x, pad_y = 10, 10

        auto_button.grid(row=0, column=0, padx=pad_x, pady=pad_y)
        self.id_input.grid(row=0, column=1, padx=pad_x, pady=pad_y)
        self.cage_input.grid(row=0, column=2, padx=pad_x, pady=pad_y)
        move_button.grid(row=0, column=3, padx=pad_x, pady=pad_y)
        save_button.grid(row=0, column=4, padx=pad_x, pady=pad_y)

        for i in range(0, 4):
            input_frame.grid_columnconfigure(i, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        input_frame.pack(side=TOP, expand=TRUE, anchor='center')
        self.config_frame.pack(side=TOP, expand=TRUE, anchor='center')

        self.update_config_frame()

    




    def update_config_frame(self):
        for widget in self.config_frame.winfo_children():
            widget.destroy()

        
        


    def create_group_frame(self):
        self.group_frames = {}  # dict of {group name : frame id}

        for group in self.groups:
            frame = Frame(self.config_frame, borderwidth=3, relief='groove')
            Label(frame, text=group).pack(side=TOP, anchor='center')

            self.create_cage_frame(group)
            frame.pack(side=TOP, expand=TRUE, fill=BOTH, anchor='center')

            self.group_frames[group] = frame
           





    def create_cage_frame(self, group):
        cages = self.db.get_cages()
        self.cage_frames = {}   # dict of {cage num : frame id}
        print(cages)    # prints 3 empty lists
        




    # def create_cage_frame(self, frame, animal, row_num):
    
        # cage_frame = Frame(frame, relief='ridge')
        # label = Label(cage_frame, text=('Cage ' + str(animal[2])), anchor='center')
        # label.grid(row=0, column=0, padx=self.pad, pady=self.pad, 
        #             ipadx=self.ipad, ipady=2)

        # anim_frame = self.create_animal_frame(animal, cage_frame)
        # anim_frame.grid(row=row_num+1, column=0, padx=self.pad, pady=self.pad, 
        #             ipadx=self.ipad, ipady=self.ipad)

        # Label(anim_frame, text='Animal ID').grid(row=0, column=0)
        # Label(anim_frame, text='Weight').grid(row=0, column=1)
        
        # self.cage_frames.append(cage_frame)
        # return cage_frame


    def create_animal_frame(self, animal, frame):
        
        anim_frame = Frame(frame)
        id_label = Label(anim_frame, text=str(animal[0]), anchor='center') 
        meas_label = Label(anim_frame, text=str(animal[4]), anchor='center')

        id_label.grid(row=1, column=0, padx=self.pad, pady=2, ipadx=self.ipad, ipady=self.ipad)
        meas_label.grid(row=1, column=1, padx=self.pad, pady=2, ipadx=self.ipad, ipady=self.ipad)
        
        self.anim_frames.append(anim_frame)
        return anim_frame


    # def update_frame(self):
    #     for widget in self.config_frame.winfo_children():
    #         widget.destroy()
    #     self.group_frames = []
    #     self.anim_frames = []
    #     self.cage_frames = []
    #     self.create_group_frame()


    def clear_entry(self, event, input):
        if input == 'id':
            self.id_input.delete(0, END)
        else:
            self.cage_input.delete(0, END)


    def auto_group(self):
        # TO-DO : re-group by weight
        self.update_config_frame()
        pass

    
    def move_animal(self, id: int, cage: int):
        # TO-DO : change in temp variable

        self.clear_entry(None, 'cage')
        self.clear_entry(None, 'id')

        self.update_config_frame()


    def raise_warning(self, option: int):
        message = Tk()
        message.title("WARNING")
        message.geometry('320x100')
        message.resizable(False, False)

        if option == 1:
            label = Label(message, text='Animal ID and Cage ID must be integers.')
            label.grid(row=0, column=0, padx=10, pady=10)
        elif option == 2:
            label = Label(message, text='Not a valid Animal ID.')
            label.grid(row=0, column=0, padx=10, pady=10)
        elif option == 3:
            label = Label(message, text='Not a valid Cage ID.')
            label.grid(row=0, column=0, padx=10, pady=10)

        ok_button = Button(message, text="OK", width=10, 
                        command= lambda: [message.destroy()])
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        message.mainloop()


    def check_move_input(self):
        # valid_animal = False
        # valid_cage = False
        valid_animal = True
        valid_cage = True

        # TO-DO : call database/local variable check if valid

        if self.id_input.get() == '' or self.cage_input.get() == '':
            self.raise_warning(1)
        elif isinstance(int(self.id_input.get()), int) == False or isinstance(int(self.cage_input.get()), int) == False:
            self.raise_warning(1)
        elif valid_animal == False:
            self.raise_warning(2)
        elif valid_cage == False:
            self.raise_warning(3)
        elif  isinstance(int(self.id_input.get()), int) and isinstance(int(self.cage_input.get()), 
                int) and valid_animal and valid_cage:
            self.move_animal(self.id_input.get(), self.cage_input.get())


    def save_to_database(self):
        # TO-DO : save to database
        # TO-DO : return to menu
        pass

