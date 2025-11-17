'''New Experiment Module — full functional version with modernized layout.'''
from os.path import *
from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkEntry, CTkRadioButton, CTkButton, StringVar, BooleanVar, W, END
)
from shared.tk_models import MouserPage, ChangePageButton
from shared.scrollable_frame import ScrolledFrame
from experiment_pages.experiment.group_config_ui import GroupConfigUI
from shared.experiment import Experiment
from shared.audio import AudioManager
from shared.file_utils import ERROR_SOUND
import inspect


class NewExperimentUI(MouserPage):
    '''New Experiment user interface (full logic preserved, modern layout).'''

    def __init__(self, parent: CTk, menu_page: CTkFrame = None):
        super().__init__(parent, "New Experiment", menu_page)

        # ----------------------------
        # Global Style + Navigation UI
        # ----------------------------
        # Restyle Back to Menu button
        if hasattr(self, "menu_button") and self.menu_button:
            self.menu_button.configure(
                corner_radius=12,
                height=50,
                width=180,
                font=("Segoe UI Semibold", 18),
                text_color="white",
                fg_color="#2563eb",
                hover_color="#1e40af"
            )
            self.menu_button.place_configure(relx=0.05, rely=0.13, anchor="w")

        # Model + state
        self.input = Experiment()
        self.menu_page = menu_page
        self.next_button = None
        self.added_invest = []

        # ----------------------------
        # Scrollable Main Layout
        # ----------------------------
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.5, rely=0.65, relheight=0.90, relwidth=0.9, anchor="center")

        self.main_frame = CTkFrame(
            scroll_canvas,
            fg_color=("white", "#2c2c2c"),
            corner_radius=16,
            border_width=1,
            border_color="#d1d5db"
        )
        self.main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        pad_x, pad_y = 10, 10

        # ----------------------------
        # Form Labels
        # ----------------------------
        CTkLabel(self.main_frame, text='Experiment Name').grid(row=0, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Password").grid(row=0, 
                    column=2, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text='Investigators').grid(row=1, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text='Species').grid(row=3, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text='Measurement Items').grid(row=4, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="RFID").grid(row=6, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Number of Animals").grid(row=7, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Number of Groups").grid(row=8, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Max Animals per Cage").grid(row=9, 
                    column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))

        # ----------------------------
        # Input Fields
        # ----------------------------
        self.exper_name = CTkEntry(self.main_frame, width=180)
        self.password = CTkEntry(self.main_frame, width=160, show="*")
        self.investigators = CTkEntry(self.main_frame, width=180)
        self.species = CTkEntry(self.main_frame, width=180)
        self.measure_items = CTkEntry(self.main_frame, width=180, textvariable=StringVar(value="Weight"))
        self.animal_num = CTkEntry(self.main_frame, width=140)
        self.group_num = CTkEntry(self.main_frame, width=140)
        self.num_per_cage = CTkEntry(self.main_frame, width=140)

        self.exper_name.grid(row=0, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.password.grid(row=0, column=3, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.investigators.grid(row=1, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.species.grid(row=3, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.measure_items.grid(row=4, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.animal_num.grid(row=7, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.group_num.grid(row=8, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))
        self.num_per_cage.grid(row=9, column=1, sticky=W, padx=pad_x, pady=(2, pad_y))

        # ----------------------------
        # Investigator controls
        # ----------------------------
        self.invest_frame = CTkFrame(self.main_frame, fg_color="transparent")
        self.invest_frame.grid(row=2, column=1, sticky='nw')
        self.invest_frame.grid_propagate(False)
        self.invest_frame.configure(height=1)


        add_invest_button = CTkButton(
            self.main_frame,
            text='+',
            width=28,
            command=lambda: [self.add_investigator(), self.investigators.delete(0, END)],
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white"
        )
        add_invest_button.grid(row=1, column=2, padx=pad_x, pady=pad_y)

        # ----------------------------
        # RFID Options
        # ----------------------------
        self.rfid = BooleanVar(value=True)
        self.rfid_frame = CTkFrame(self.main_frame, fg_color="transparent")
        self.rfid_frame.grid(row=6, column=1, sticky="w")
        CTkRadioButton(self.rfid_frame, text='Yes', variable=self.rfid, value=1).grid(row=0, 
                        column=0, padx=pad_x, pady=pad_y)
        CTkRadioButton(self.rfid_frame, text='No', variable=self.rfid, value=0).grid(row=0, 
                        column=1, padx=pad_x, pady=pad_y)

        # Configure grid scaling
        for i in range(0, 10):
            self.main_frame.grid_rowconfigure(i, weight=0)
            self.main_frame.grid_columnconfigure(i, weight=1)

        # ----------------------------
        # Create Next button (aligned top-right)
        # ----------------------------
        self.create_next_button()

        # Enable field tracking
        self.bind_all_entries()

    # ------------------------------------------------------------
    # Navigation + Buttons
    # ------------------------------------------------------------
    def create_next_button(self):
        '''Create the Next button that validates and navigates.'''
        if self.next_button:
            self.next_button.destroy()

        self.next_button = ChangePageButton(self, next_page=None, previous=False)
        self.next_button.configure(
            corner_radius=12,
            height=50,
            width=180,
            font=("Segoe UI Semibold", 18),
            text_color="white",
            fg_color="#2563eb",
            hover_color="#1e40af",
            command=lambda: [self.check_animals_divisible(), self._go_next()],
            state="disabled"
        )
        self.next_button.place_configure(relx=0.93, rely=0.13, anchor="e")

    def bind_all_entries(self):
        '''Function to bind all enteries'''
        fields = [
            self.exper_name, self.password, self.species, self.measure_items,
            self.animal_num, self.group_num, self.num_per_cage
        ]
        for f in fields:
            f.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.investigators.bind("<Return>", lambda event: [self.add_investigator(),
                                                           self.investigators.delete(0, END)])

    def enable_next_button(self):
        '''Function to enable all buttons'''
        required = [
            self.exper_name.get().strip(),
            self.species.get().strip(),
            self.animal_num.get().strip(),
            self.group_num.get().strip(),
            self.num_per_cage.get().strip()
        ]
        if all(required):
            self.next_button.configure(state="normal")
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
        self.next_button.configure(command= lambda: [self.check_animals_divisible(),
                                                     self.next_button.navigate()], state="disabled")
        self.next_button.place(relx=0.85, rely=0.15)

    def update_invest_frame(self):
        '''Clear widget in the invest frame'''
        for widget in self.invest_frame.winfo_children():
            widget.destroy()

        funcs, buttons = [], []
        for investigator in self.added_invest:
            CTkLabel(self.invest_frame, text=investigator).grid(
                row=self.added_invest.index(investigator), column=1, sticky=W, padx=10
            )
            rem_button = CTkButton(
                self.invest_frame,
                text='-',
                width=28,
                corner_radius=8,
                fg_color="#ef4444",
                hover_color="#b91c1c",
                text_color="white"
            )
            rem_button.grid(row=self.added_invest.index(investigator), column=2, padx=10)
            buttons.append(rem_button)
            funcs.append(lambda x=investigator: self.remove_investigator(x))
        for i, f in enumerate(funcs):
            buttons[i].configure(command=f)
        # Adjust frame height dynamically
        self.invest_frame.configure(height=(len(self.added_invest) * 40) or 1)

    def add_investigator(self):
        '''Function to add the investigator to the frame'''
        val = self.investigators.get()
        if val and val not in self.added_invest:
            self.added_invest.append(val)
            self.update_invest_frame()

    def remove_investigator(self, person):
        '''Update invest frame'''
        if person in self.added_invest:
            self.added_invest.remove(person)
            self.update_invest_frame()

    # ------------------------------------------------------------
    # Validation / Warnings
    # ------------------------------------------------------------
    def raise_warning(self, option: int):
        def dismiss(event=None):
            message.destroy()

        message = CTk()
        message.title("WARNING")
        message.geometry('340x180')
        message.resizable(False, False)

        texts = {
            2: "Number of animals, groups, or max animals per cage must be > 0.",
            3: "Experiment name used. Please use another name.",
            4: "Unequal Group Size: Please ensure total animals ≤ group capacity."
        }
        CTkLabel(message, text=texts.get(option, "Warning")).grid(row=0, column=0, padx=10, pady=10)
        CTkButton(message, text="OK", width=10, command=dismiss).grid(row=1, column=0, pady=10)
        AudioManager.play(ERROR_SOUND)
        message.bind("<KeyPress>", dismiss)
        message.bind("<Button>", dismiss)
        message.focus_force()
        message.mainloop()

    def check_animals_divisible(self):
        if not all([self.animal_num.get(), self.group_num.get(), self.num_per_cage.get()]):
            self.raise_warning(2)
        elif int(self.animal_num.get()) == 0 or int(self.group_num.get()) == 0:
            self.raise_warning(2)
        elif int(self.animal_num.get()) > (int(self.group_num.get()) * int(self.num_per_cage.get())):
            self.raise_warning(4)
        else:
            self.save_input()

    # ------------------------------------------------------------
    # Save + Navigation
    # ------------------------------------------------------------
    def save_input(self):
        self.input.set_name(self.exper_name.get())
        if self.password.get():
            self.input.set_password(self.password.get())
        self.input.set_unique_id()
        investigators = self.added_invest.copy()
        if self.investigators.get().strip():
            investigators.append(self.investigators.get().strip())
        self.input.set_investigators(investigators)
        self.input.set_species(self.species.get())
        self.input.set_measurement_item(self.measure_items.get())
        self.input.set_uses_rfid(self.rfid.get())
        self.input.set_num_animals(self.animal_num.get())
        self.input.set_num_groups(self.group_num.get())
        self.input.set_max_animals(self.num_per_cage.get())
        AudioManager.play(SUCCESS_SOUND)

    def _go_next(self):
        try:
            page = GroupConfigUI(self.input, self.root, self, self.menu_page)
            page.raise_frame()
        except TypeError:
            try:
                page = GroupConfigUI(self.root, None, self)
                page.raise_frame()
            except Exception as e:
                print("Navigation error:", e)
