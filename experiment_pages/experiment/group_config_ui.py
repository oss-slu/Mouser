'''Group configuration module.'''
from customtkinter import *
from shared.tk_models import *
from shared.scrollable_frame import ScrolledFrame
from experiment_pages.create_experiment.summary_ui import SummaryUI
from shared.experiment import Experiment


class GroupConfigUI(MouserPage): # pylint: disable= undefined-variable
    '''Group Congifuratin User Interface and Window.'''

    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):

        super().__init__(parent, "New Experiment - Group Configuration", prev_page)
        self.experiment = experiment

        self.next_page = SummaryUI(self.experiment, parent, self, menu_page)
        self.set_next_button(self.next_page)

        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.1, rely=0.25, relheight=0.75, relwidth=0.88)

        self.main_frame = CTkFrame(scroll_canvas)
        self.main_frame.grid(row=0, column=0, sticky='NESW')

        self.group_frame = CTkFrame(self.main_frame)
        self.item_frame = CTkFrame(self.main_frame)

        self.group_frame.pack(side=TOP)
        self.item_frame.pack(side=TOP)

        self.create_group_entries(int(self.experiment.get_num_groups()))
        self.create_item_frame(self.experiment.get_measurement_items())

        self.experiment = experiment
        self.selected_animals = []
        self.swap_button = CTkButton(self.main_frame, text="Swap", state="disabled", command=self.perform_swap)
        self.swap_button.pack(side=BOTTOM, pady=10)

        for i in range(0,2):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i, weight=1)


    def set_next_button(self, next_page):
        '''Sets the page that the next button navigaties too.'''
        if self.next_button: #pylint: disable= access-member-before-definition
            self.next_button.destroy() #pylint: disable= access-member-before-definition

        self.next_button = ChangePageButton(self, next_page, False)# pylint: disable= undefined-variable
        self.next_button.configure(command= lambda: [self.save_experiment(), self.next_button.navigate()])
        self.next_button.place(relx=0.85, rely=0.15)



    def create_group_entries(self, num):
        '''Creates the widgit for group entries.'''
        CTkLabel(self.group_frame, text="Group Name").grid(row=0, column=0, padx=10, pady=10)
        self.group_input = []
        for i in range(0, num):
            name = CTkEntry(self.group_frame, width = 160)
            name.grid(row=i+1, column=0, padx=10, pady=10)
            self.group_input.append(name)

    def create_item_frame(self, items):
        '''Creates a grid of all each item in items.'''
        self.button_vars = []
        self.item_auto_buttons = []
        self.item_man_buttons = []

        type_label = CTkLabel(self.item_frame, text="Input Method")
        type_label.grid(row=0, column=0, columnspan=3, pady=8)

        for i in range(0, len(items)): # pylint: disable= consider-using-enumerate
            self.type = BooleanVar()
            self.button_vars.append(self.type)

            CTkLabel(self.item_frame, text=items[i]).grid(row=i+1, column=0, padx=10, pady=10, sticky=W)
            auto = CTkRadioButton(self.item_frame, text='Automatic', variable=self.type, value=1)
            man = CTkRadioButton(self.item_frame, text='Manual', variable=self.type, value=0)

            auto.grid(row=i+1, column=1, padx=10, pady=10)
            man.grid(row=i+1, column=2, padx=10, pady=10)

            self.item_auto_buttons.append(auto)
            self.item_man_buttons.append(man)

    def update_page(self):
        '''Updates page to reflect current state of the experiment.'''
        if self.experiment.check_num_groups_change():
            for widget in self.group_frame.winfo_children():
                widget.destroy()
            self.create_group_entries(int(self.experiment.get_num_groups()))
            self.experiment.set_group_num_changed_false()

        if self.experiment.check_measurement_items_changed():
            for widget in self.item_frame.winfo_children():
                widget.destroy()
            self.create_item_frame(self.experiment.get_measurement_items())
            self.experiment.set_measurement_items_changed_false()

    def select_for_swap(self, animal_id):
        if animal_id in self.selected_animals:
            self.selected_animals.remove(animal_id)
        else:
            self.selected_animals.append(animal_id)
            if len(self.selected_animals) == 2:
                self.swap_button['state'] = 'normal'
            elif len(self.selected_animals) < 2:
                self.swap_button['state'] = 'disabled'

    def perform_swap(self):
        if len(self.selected_animals) == 2:
            self.selected_animals.swap_animals(self.selected_animals[0], self.selected_animals[1]) 
            self.update_ui_after_swap()
            self.selected_animals = []  # Reset selection
            self.swap_button['state'] = 'disabled'

    def update_ui_after_swap(self):
        # Code to refresh the UI elements showing animal group/cage assignments
        pass

    def save_experiment(self):
        '''Saves the experiment file to a the database file.'''
        group_names = []
        for entry in self.group_input:
            group_names.append(entry.get())
            self.experiment.group_names = group_names
        # pylint: disable= consider-using-enumerate
        items = self.experiment.get_measurement_items()
        measurement_collect_type = []
        for i in range(0, len(items)):
            measurement_collect_type.append((items[i], self.button_vars[i].get()))
        # pylint: enable= consider-using-enumerate
        self.experiment.data_collect_type = measurement_collect_type
        self.next_page.update_page()
