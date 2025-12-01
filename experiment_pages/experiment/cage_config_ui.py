"""
Contains cage configuration page and behaviour.
"""

import traceback

from CTkMessagebox import CTkMessagebox
from customtkinter import *

from databases.database_controller import DatabaseController
from shared.audio import AudioManager
from shared.file_utils import ERROR_SOUND, SUCCESS_SOUND, save_temp_to_file
from shared.scrollable_frame import ScrolledFrame
from shared.tk_models import MouserPage

class CageConfigUI(MouserPage):
    """
    The Frame that allows users to configure cages and move/sort animals.
    """

    def __init__(self, root: CTk, file_path: str, menu_page: CTkFrame):
        super().__init__(root, "Cage Configuration", menu_page)

        self.root = root
        self.file_path = file_path
        self.menu_page = menu_page
        self.prev_page = menu_page


        # Load database from file path
        self.db = DatabaseController(file_path)

        self.pad_x = 10
        self.pad_y = 10

        # Main Scrollable Canvas
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.05, rely=0.20, relheight=0.75, relwidth=0.88)

        input_frame = CTkFrame(scroll_canvas)
        self.config_frame = CTkFrame(scroll_canvas)

        # Buttons
        CTkButton(input_frame, text="AutoSort", width=15, command=self.autosort).grid(
            row=0, column=0, padx=self.pad_x, pady=self.pad_y
        )
        CTkButton(input_frame, text="Randomize", width=15, command=self.randomize).grid(
            row=0, column=1, padx=self.pad_x, pady=self.pad_y
        )
        CTkButton(input_frame, text="Swap", width=15, command=self.perform_swap).grid(
            row=0, column=2, padx=self.pad_x, pady=self.pad_y
        )
        CTkButton(input_frame, text="Move Groups", width=15, command=self.move_animal).grid(
            row=0, column=3, padx=self.pad_x, pady=self.pad_y
        )

        # Entry fields
        self.id_input = CTkEntry(input_frame, width=110)
        self.cage_input = CTkEntry(input_frame, width=110)

        self.id_input.insert(END, "animal id")
        self.cage_input.insert(END, "group id")

        self.id_input.bind("<Button-1>", lambda _event, arg="id": self.clear_entry(arg))
        self.cage_input.bind("<Button-1>", lambda _event, arg="group": self.clear_entry(arg))

        for i in range(4):
            input_frame.grid_columnconfigure(i, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)

        input_frame.pack(side=TOP, fill=X, anchor="center")
        self.config_frame.pack(side=TOP, fill=BOTH, anchor="center")

        # Tracking selection
        self.animal_buttons = {}
        self.cage_buttons = {}
        self.selected_animals = set()
        self.selected_cage = None

        self.update_config_frame()


    def update_config_frame(self):
        """Refreshes the configuration frame."""
        for widget in self.config_frame.winfo_children():
            widget.destroy()
        self.create_cage_layout()

    def create_cage_layout(self):
        """Creates the layout showing all cages and animals."""
        cages = self.db.get_groups()
        label_style = CTkFont("Arial", 12)

        for cage_name in cages:
            cage_frame = CTkFrame(
                self.config_frame,
                border_width=3,
                border_color="#00e7ff",
                bg_color="#0097A7"
            )

            # Cage header
            cage_button = CTkButton(
                cage_frame,
                text=f"Group: {cage_name}",
                fg_color="#0097A7",
                hover_color="#00b8d4",
                text_color="white",
                font=label_style,
                command=lambda c=cage_name: self.select_cage(c)
            )
            cage_button.pack(side=TOP, padx=self.pad_x, pady=self.pad_y, anchor="center")
            self.cage_buttons[cage_name] = cage_button

            # Header label
            header_frame = CTkFrame(cage_frame)
            header_frame.pack(fill=X, pady=2)
            CTkLabel(header_frame, text="Animal ID").pack(side=LEFT, anchor="center")

            # Animal buttons
            animals = self.db.get_animals_in_group(cage_name)
            for animal in animals:
                animal_id = str(animal[0])

                animal_frame = CTkFrame(cage_frame)
                animal_button = CTkButton(
                    animal_frame,
                    text=animal_id,
                    fg_color="#0097A7",
                    hover_color="#00b8d4",
                    text_color="white",
                    command=lambda a=animal_id: self.toggle_animal_selection(a)
                )

                animal_button.pack(fill=X, pady=2)
                animal_frame.pack(fill=X, pady=1)

                self.animal_buttons[animal_id] = animal_button

            cage_frame.pack(side=LEFT, expand=TRUE, fill=BOTH, anchor="center")


    def select_cage(self, cage_name):
        """Handles cage selection."""
        button = self.cage_buttons.get(cage_name)
        if not button:
            return

        if self.selected_cage == cage_name:
            # Deselect
            self.selected_cage = None
            button.configure(fg_color="#0097A7")
            self.cage_input.delete(0, END)
            self.cage_input.insert(0, "cage id")
        else:
            # Deselect previous
            if self.selected_cage in self.cage_buttons:
                self.cage_buttons[self.selected_cage].configure(fg_color="#0097A7")

            self.selected_cage = cage_name
            button.configure(fg_color="#D5E8D4")
            self.cage_input.delete(0, END)
            self.cage_input.insert(0, cage_name)

    def toggle_animal_selection(self, animal_id):
        """Toggles selection state of an animal."""
        button = self.animal_buttons.get(animal_id)
        if not button:
            return

        if animal_id in self.selected_animals:
            self.selected_animals.remove(animal_id)
            button.configure(fg_color="#0097A7")
        else:
            self.selected_animals.add(animal_id)
            button.configure(fg_color="#D5E8D4")

    def clear_entry(self, entry_type):
        """Clears the associated entry field."""
        if entry_type == "id":
            self.id_input.delete(0, END)
        else:
            self.cage_input.delete(0, END)


    def randomize(self):
        """Randomizes cages."""
        self.db.randomize_cages()
        self.update_config_frame()
        self.save()
        AudioManager.play(SUCCESS_SOUND)

    def autosort(self):
        """Autosorts animals after confirmation."""
        confirm = CTkMessagebox(
            title="Confirm AutoSort",
            message=(
                "Are you sure you want to AutoSort?\n"
                "This will remove measurements used to sort from the database."
            ),
            option_1="No",
            option_2="Yes"
        )

        if confirm.get() == "Yes":
            self.db.autosort()
            self.update_config_frame()
            self.save()
            AudioManager.play(SUCCESS_SOUND)

    def perform_swap(self):
        """Swaps two selected animals."""
        if len(self.selected_animals) != 2:
            self.raise_warning("Please select exactly two animals to swap.")
            return

        selected = list(self.selected_animals)
        animal_id1 = selected[0]
        animal_id2 = selected[1]

        cage1 = self.db.get_animal_current_cage(animal_id1)
        cage2 = self.db.get_animal_current_cage(animal_id2)

        if cage1 == cage2:
            self.raise_warning("Both animals are in the same cage.")
            return

        self.db.update_animal_cage(animal_id1, cage2)
        self.db.update_animal_cage(animal_id2, cage1)

        self.selected_animals.clear()
        self.update_config_frame()
        self.save()
        AudioManager.play(SUCCESS_SOUND)

    def move_animal(self):
        """Moves selected animals to a specified cage."""
        if not self.selected_animals:
            self.raise_warning("Please select at least one animal to move.")
            return

        if not self.selected_cage:
            self.raise_warning("Please select a target cage.")
            return

        target_cage = self.selected_cage
        target_group = self.db.get_cage_number(target_cage)

        current_count = len(self.db.get_animals_in_group(target_cage))
        if current_count + len(self.selected_animals) > self.db.get_cage_max():
            self.raise_warning(
                f"Moving these animals would exceed "
                f"the max capacity of {self.db.get_cage_max()}."
            )
            return

        animals_moved = False
        for animal_id in list(self.selected_animals):
            curr = self.db.get_animal_current_cage(animal_id)
            if curr != target_group:
                self.db.update_animal_cage(animal_id, target_group)
                animals_moved = True

        if not animals_moved:
            self.raise_warning("No animals were moved.")
            return

        # Reset selection
        self.selected_animals.clear()
        self.selected_cage = None

        if target_cage in self.cage_buttons:
            self.cage_buttons[target_cage].configure(fg_color="#0097A7")

        self.update_config_frame()
        self.save()
        AudioManager.play(SUCCESS_SOUND)


    def raise_warning(self, message):
        """Displays a warning dialog."""
        message_window = CTk()
        message_window.title("WARNING")
        message_window.geometry("320x100")
        message_window.resizable(False, False)

        CTkLabel(message_window, text=message).grid(row=0, column=0, padx=10, pady=10)

        CTkButton(
            message_window,
            text="OK",
            width=10,
            command=message_window.destroy
        ).grid(row=2, column=0, padx=10, pady=10)

        AudioManager.play(ERROR_SOUND)
        message_window.mainloop()


    def save_to_database(self):
        """Saves updates to database."""
        if self.db.check_num_in_cage_allowed():
            self.db.update_experiment()
            if self.prev_page:
                self.prev_page.raise_frame()
        else:
            self.raise_warning(
                f"Number of animals per group must not exceed {self.db.get_cage_max()}"
            )

    def save(self):
        """Commits DB changes and writes file to disk."""
        try:
            current_file = self.db.db.db_file
            self.db.commit()

            save_temp_to_file(current_file, self.file_path)

        except FileNotFoundError:
            print("Error during save:")
            print(traceback.format_exc())

    def close_connection(self):
        """Closes DB connection."""
        self.db.close()

    def raise_frame(self):
        """Compatibility override for pylint."""
        super().raise_frame()

