'''Contains cage configuration page and behaviour.'''
from customtkinter import *
from shared.tk_models import *
from shared.scrollable_frame import ScrolledFrame
from databases.database_controller import DatabaseController
from shared.audio import AudioManager

class CageConfigurationUI(MouserPage):
    '''The Frame that allows user to configure the cages.'''
    def __init__(self, database, parent: CTk, prev_page: CTkFrame = None):
        super().__init__(parent, "Cage Configuration", prev_page)

        self.prev_page = prev_page
        self.db = DatabaseController(database)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.05, rely=0.20, relheight=0.75, relwidth=0.88)

        input_frame = CTkFrame(scroll_canvas)
        self.config_frame = CTkFrame(scroll_canvas)

        random_button = CTkButton(input_frame, text='Randomize', width=15,
                            command=self.randomize)
        swap_button = CTkButton(input_frame, text='Swap', width=15,
                            command=self.perform_swap)
        auto_button = CTkButton(input_frame, text='AutoSort', width=15,
                                command=self.autosort)

        self.id_input = CTkEntry(input_frame, width=110)
        self.cage_input = CTkEntry(input_frame, width=110)

        self.id_input.insert(END, 'animal id')
        self.cage_input.insert(END, 'cage id')

        self.id_input.bind("<Button-1>", lambda arg='id': self.clear_entry(arg))
        self.cage_input.bind("<Button-1>", lambda arg='cage': self.clear_entry(arg))

        self.pad_x, self.pad_y = 10, 10

        auto_button.grid(row=0, column=0, padx=self.pad_x, pady=self.pad_y)
        random_button.grid(row=0, column=1, padx=self.pad_x, pady=self.pad_y)
        swap_button.grid(row=0, column=2, padx=self.pad_x, pady=self.pad_y)

        for i in range(0, 3):
            input_frame.grid_columnconfigure(i, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        input_frame.pack(side=TOP, fill=X, anchor='center')
        self.config_frame.pack(side=TOP, fill=BOTH, anchor='center')
        self.animal_buttons = {}
        self.selected_animals = set()

        self.update_config_frame()

    def update_config_frame(self):
        '''Updates the config frame to reflect new information.'''
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.create_cage_layout()

    def create_cage_layout(self):
        '''Creates the layout of all cages and their animals.'''
        cages = self.db.get_groups()  # Each group represents a cage
        label_style = CTkFont("Arial", 12)

        for cage_name in cages:
            cage_frame = CTkFrame(self.config_frame, border_width=3, border_color="#00e7ff", bg_color='#0097A7')

            # Cage header
            label = CTkLabel(cage_frame, text=f'Cage: {cage_name}', bg_color='#0097A7', font=label_style)
            label.pack(side=TOP, padx=self.pad_x, pady=self.pad_y, anchor='center')

            # Create header frame for labels
            header_frame = CTkFrame(cage_frame)
            CTkLabel(header_frame, text='Animal ID').pack(side=LEFT, anchor='center')

            # Get and display animals in this cage using the database controller
            animals = self.db.get_animals_in_group(cage_name)

            for animal in animals:
                animal_id = str(animal[0])
                # Create a new frame for each animal to hold the button
                animal_frame = CTkFrame(cage_frame)
                animal_button = CTkButton(
                    animal_frame,
                    text=animal_id,
                    command=lambda a=animal_id: self.toggle_animal_selection(a),
                    fg_color="#0097A7",
                    hover_color="#00b8d4",
                    text_color="white"
                )
                animal_button.pack(fill=X, pady=2)
                animal_frame.pack(fill=X, pady=1)
                self.animal_buttons[animal_id] = animal_button

            cage_frame.pack(side=LEFT, expand=TRUE, fill=BOTH, anchor='center')

    def toggle_animal_selection(self, animal_id):
        '''Toggles the selection state of an animal.'''
        button = self.animal_buttons.get(animal_id)
        if button:
            if animal_id in self.selected_animals:
                self.selected_animals.remove(animal_id)
                button.configure(fg_color="#0097A7")  # Reset to default blue
                print(f"Deselected animal: {animal_id}")
            else:
                if len(self.selected_animals) < 2:
                    self.selected_animals.add(animal_id)
                    button.configure(fg_color="#D5E8D4")  # Selected state green
                    print(f"Selected animal: {animal_id}")
            print(f"Currently selected animals: {self.selected_animals}")
        else:
            print(f"Error: No button found for Animal ID: {animal_id}")

    def clear_entry(self, input_type):
        '''Clears entry from input frames.'''
        if input_type == 'id':
            self.id_input.delete(0, END)
        else:
            self.cage_input.delete(0, END)

    def randomize(self):
        '''Autosorts the animals into cages.'''
        self.db.randomize_cages()
        self.update_config_frame()

    def autosort(self):
        '''Calls database's autosort function.'''
        self.db.autosort()
        self.update_config_frame()

    def perform_swap(self):
        '''Swaps two selected animals between cages.'''
        if len(self.selected_animals) != 2:
            self.raise_warning("Please select exactly two animals to swap.")
            return

        animal_id1, animal_id2 = self.selected_animals

        # Get the current cages through the database controller
        cage1 = self.db.get_animal_current_cage(animal_id1)
        cage2 = self.db.get_animal_current_cage(animal_id2)

        if cage1 == cage2:
            self.raise_warning("Both animals are in the same cage.")
            return

        # Perform the swap using the database controller
        self.db.update_animal_cage(animal_id1, cage2)  # Move animal 1 to cage 2
        self.db.update_animal_cage(animal_id2, cage1)  # Move animal 2 to cage 1

        self.selected_animals.clear()
        self.update_config_frame()

    def raise_warning(self, message):
        '''Raises a warning page with the given message.'''
        message_window = CTk()
        message_window.title("WARNING")
        message_window.geometry('320x100')
        message_window.resizable(False, False)

        label = CTkLabel(message_window, text=message)
        label.grid(row=0, column=0, padx=10, pady=10)

        ok_button = CTkButton(message_window, text="OK", width=10,
                            command=lambda: message_window.destroy())
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        AudioManager.play(filepath='sounds/error.wav')
        message_window.mainloop()

    def save_to_database(self):
        '''Saves updated values to database.'''
        if self.check_num_in_cage_allowed():
            self.db.update_experiment()
            raise_frame(self.prev_page)
        else:
            self.raise_warning(f'Number of animals in a cage must not exceed {self.db.get_cage_max()}')

    def check_num_in_cage_allowed(self):
        '''Checks if the number of animals in a cage is allowed.'''
        return self.db.check_num_in_cage_allowed()

    def close_connection(self):
        '''Closes database file.'''
        self.db.close()
