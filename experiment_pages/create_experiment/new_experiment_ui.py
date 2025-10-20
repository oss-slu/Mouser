'''New Experiment Module (modernized UI with original functionality preserved)'''
from os.path import *
from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkEntry, CTkRadioButton, CTkButton, StringVar, BooleanVar, W, END
)
from shared.tk_models import MouserPage, ChangePageButton  # keep existing navigation widgets
from shared.scrollable_frame import ScrolledFrame
from experiment_pages.experiment.group_config_ui import GroupConfigUI
from shared.experiment import Experiment
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND, ERROR_SOUND
import inspect


class NewExperimentUI(MouserPage):  # pylint: disable= undefined-variable
    '''New Experiment user interface (visual refresh only, no logic removed).'''

    def __init__(self, parent: CTk, menu_page: CTkFrame = None):
        super().__init__(parent, "New Experiment", menu_page)

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
            # Optional: reposition so it looks consistent with other screens
            self.menu_button.place_configure(relx=0.15, rely=0.18, anchor="w")

        # Original model/state
        self.input = Experiment()
        self.menu_page = menu_page  # keep a handle for safe navigation
        self.next_button = None

        # ---- LAYOUT: scrollable content area (unchanged structure) ----
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.12, rely=0.25, relheight=0.75, relwidth=0.88)

        # A main container card to improve visuals (flat, rounded, bordered)
        self.main_frame = CTkFrame(
            scroll_canvas,
            fg_color=("white", "#2c2c2c"),
            corner_radius=16,
            border_width=1,
            border_color="#d1d5db"
        )
        self.main_frame.grid(row=10, column=3, sticky='NESW', padx=12, pady=12)

        # Sub-frames (kept as-is to avoid breaking any downstream assumptions)
        self.invest_frame = CTkFrame(self.main_frame, height=0, fg_color="transparent")
        self.item_frame = CTkFrame(self.main_frame, height=0, fg_color="transparent")
        self.rfid_frame = CTkFrame(self.main_frame, height=0, fg_color="transparent")

        self.invest_frame.grid(row=2, column=1, sticky='NESW')
        self.item_frame.grid(row=5, column=1, sticky='NESW')
        self.rfid_frame.grid(row=6, column=1, sticky='NESW')

        # Paddings
        pad_x = 10
        pad_y = 10

        self.items = ''
        self.added_invest = []

        # ---- FORM LABELS (same fields, improved spacing/clarity) ----
        CTkLabel(self.main_frame, text='Experiment Name').grid(
            row=0, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Password").grid(
            row=0, column=2, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text='Investigators').grid(
            row=1, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text='Species').grid(
            row=3, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text='Measurement Items').grid(
            row=4, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="RFID").grid(
            row=6, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Number of Animals").grid(
            row=7, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Number of Groups").grid(
            row=8, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))
        CTkLabel(self.main_frame, text="Max Animals per Cage").grid(
            row=9, column=0, sticky=W, padx=pad_x, pady=(pad_y, 2))

        # ---- INPUTS (unchanged variables, just consistent sizing) ----
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

        # RFID radios (unchanged behavior)
        self.rfid = BooleanVar(value=True)
        CTkRadioButton(self.rfid_frame, text='Yes', variable=self.rfid, value=1).grid(
            row=0, column=0, padx=pad_x, pady=pad_y)
        CTkRadioButton(self.rfid_frame, text='No', variable=self.rfid, value=0).grid(
            row=0, column=1, padx=pad_x, pady=pad_y)

        # Add investigator button (same lambda behavior)
        add_invest_button = CTkButton(
            self.main_frame, text='+', width=28,
            command=lambda: [self.add_investigator(), self.investigators.delete(0, END)],
            corner_radius=8, fg_color="#2563eb", hover_color="#1e40af", text_color="white"
        )
        add_invest_button.grid(row=1, column=2, padx=pad_x, pady=pad_y)

        # (Kept commented measurement item add button as-is)
        # add_item_button = CTkButton(self.main_frame, text='+', width=3,
        #     command=lambda: [self.add_measurement_item(), self.measure_items.delete(0, END)])
        # add_item_button.grid(row=4, column=2, padx=pad_x, pady=pad_y)

        # Grid weights unchanged
        for i in range(0, 10):
            if i < 3:
                self.main_frame.grid_columnconfigure(i, weight=1)
            self.main_frame.grid_rowconfigure(i, weight=1)

        # --- NEXT BUTTON: created here (no pre-instantiation of next page) ---
        self.create_next_button()

        # Bind entries last (enables/disables next button)
        self.bind_all_entries()

    # ---------------------------
    # UI helpers (visual only)
    # ---------------------------
    def create_next_button(self):
        """Create the Next button that performs validation, saves, and navigates."""
        if self.next_button:
            self.next_button.destroy()

        # Use existing ChangePageButton so placement/UX is unchanged
        self.next_button = ChangePageButton(self, next_page=None, previous=False)  # type: ignore
        # Disable until form is valid; command runs validation+navigation
        self.next_button.configure(
            command=lambda: [self.check_animals_divisible(), self._go_next()],
            state="disabled"
        )
        self.next_button.place(relx=0.85, rely=0.15)

        self.next_button.configure(
            corner_radius=12,
            height=50,
            width=180,
            font=("Segoe UI Semibold", 18),
            text_color="white",
            fg_color="#2563eb",
            hover_color="#1e40af"
        )
        self.next_button.place_configure(relx=0.87, rely=0.18, anchor="e")

    # ---------------------------
    # Original behavior preserved
    # ---------------------------
    def bind_all_entries(self):
        self.exper_name.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.password.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.species.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.measure_items.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.animal_num.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.group_num.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.num_per_cage.bind("<KeyRelease>", lambda event: self.enable_next_button())
        self.investigators.bind("<Return>", lambda event: [self.add_investigator(), self.investigators.delete(0, END)])

    def enable_next_button(self):
        """Enable the 'Next' button once minimum required fields are filled."""
        # Strip whitespace from all required entries
        exper_name = self.exper_name.get().strip()
        species = self.species.get().strip()
        animal_num = self.animal_num.get().strip()
        group_num = self.group_num.get().strip()
        num_per_cage = self.num_per_cage.get().strip()

        # Enable only when all five key fields have valid input
        if exper_name and species and animal_num and group_num and num_per_cage:
            self.next_button.configure(state="normal")
            print("Next button enabled — ready to continue.")
        else:
            self.next_button.configure(state="disabled")
            print("Waiting for required inputs...")

    def set_next_button(self, next_page):
        """Kept for backward compatibility; now routed to create_next_button()."""
        # This method is part of the original API. We keep it but delegate.
        self.create_next_button()

    def update_invest_frame(self):
        '''Updates investigator frame.'''
        for widget in self.invest_frame.winfo_children():
            widget.destroy()

        funcs = []
        buttons = []
        for investigator in self.added_invest:
            CTkLabel(self.invest_frame, text=investigator).grid(
                row=self.added_invest.index(investigator), column=1, sticky=W, padx=10)
            rem_button = CTkButton(self.invest_frame, text='-', width=28,
                                   corner_radius=8, fg_color="#ef4444", hover_color="#b91c1c",
                                   text_color="white")
            rem_button.grid(row=self.added_invest.index(investigator), column=2, padx=10)
            buttons.append(rem_button)
            funcs.append(lambda x=investigator: self.remove_investigator(x))

        for index, f in enumerate(funcs):
            buttons[index].configure(command=f)

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

    # ---------------------------
    # Warning / validation (same)
    # ---------------------------
    def raise_warning(self, option: int):
        '''Raises an error window that can be dismissed with any key or mouse press.'''

        def dismiss_warning(event=None):
            print(f"Event triggered: {event}")  # Debugging to confirm key press is detected
            message.destroy()

        message = CTk()
        message.title("WARNING")
        message.geometry('320x180')
        message.resizable(True, True)

        if option == 2:
            CTkLabel(message, text='Number of animals, groups, or maximum').grid(row=0, column=0, padx=10)
            CTkLabel(message, text='animals per cage must be greater than 0.').grid(row=1, column=0, padx=10)
        elif option == 3:
            CTkLabel(message, text='Experiment name used. Please use another name.').grid(
                row=0, column=0, padx=10, pady=10)
        elif option == 4:
            CTkLabel(message, text='''Unequal Group Size: Please allow the total number of animals to be
            less than or equal to the total number of
            animals allowed in groups.''').grid(row=0, column=0, padx=10, pady=10)

        AudioManager.play(ERROR_SOUND)
        message.bind("<KeyPress>", dismiss_warning)
        message.bind("<Button>", dismiss_warning)
        CTkButton(message, text="OK", width=10, command=dismiss_warning).grid(row=2, column=0, padx=10, pady=10)
        message.focus_force()
        message.mainloop()

    def check_animals_divisible(self):
        '''If the total number of animals is greater than the total number
        of animals allowed in all combined cages, raise warning.'''
        if (self.animal_num.get() == '' or self.group_num.get() == '' or self.animal_num.get() == ''):
            self.raise_warning(2)
        elif (int(self.animal_num.get()) == 0 or int(self.group_num.get()) == 0 or int(self.animal_num.get()) == 0):
            self.raise_warning(2)
        elif int(self.animal_num.get()) > (int(self.group_num.get()) * int(self.num_per_cage.get())):
            self.raise_warning(4)
        else:
            self.save_input()

    def save_input(self):
        '''Saves experiment to a file (original behavior preserved).'''
        self.input.set_name(self.exper_name.get())
        if self.password.get():
            self.input.set_password(self.password.get())
        self.input.set_unique_id()

        # Combine added investigators with any remaining text in the text box
        all_investigators = self.added_invest.copy()
        if self.investigators.get().strip():
            all_investigators.append(self.investigators.get().strip())
        self.input.set_investigators(all_investigators)

        self.input.set_species(self.species.get())
        self.input.set_measurement_item(self.measure_items.get())
        self.input.set_uses_rfid(self.rfid.get())
        self.input.set_num_animals(self.animal_num.get())
        self.input.set_num_groups(self.group_num.get())
        self.input.set_max_animals(self.num_per_cage.get())

        # In the original flow, GroupConfigUI read from self.input after this call.
        # We keep this behavior intact. Navigation now happens in _go_next().
        AudioManager.play(SUCCESS_SOUND)

    # ---------------------------
    # Navigation (robust to signature changes)
    # ---------------------------
    def _go_next(self):
        """
        Dynamically instantiate GroupConfigUI in a backwards-compatible way:
        1) Try legacy signature: (input_obj, parent, current_page, menu_page)
        2) Fallback to modern signature: (root, file_path, menu_page) if present
        """
        try:
            # Legacy constructor form (what your current file expects)
            page = GroupConfigUI(self.input, self.root, self, self.menu_page)
            page.raise_frame()
            return
        except TypeError:
            # Modernized form (if your GroupConfigUI was updated elsewhere)
            # We don't have file_path in this screen; pass None safely.
            try:
                page = GroupConfigUI(self.root, None, self)  # type: ignore[arg-type]
                page.raise_frame()
                return
            except TypeError as e:
                # Final fallback: attempt to match based on parameter names
                sig = inspect.signature(GroupConfigUI.__init__)
                params = list(sig.parameters.keys())
                # Heuristic mapping based on common names
                kwargs = {}
                if "experiment" in params or "input_obj" in params:
                    kwargs.update({"experiment": self.input})
                if "root" in params or "parent" in params:
                    kwargs.update({"root": self.root})
                if "menu_page" in params:
                    kwargs.update({"menu_page": self})
                # Try kwargs-only instantiation if possible
                try:
                    page = GroupConfigUI(**kwargs)  # type: ignore
                    page.raise_frame()
                    return
                except Exception as inner_e:  # noqa: BLE001
                    print("Navigation error:", inner_e)
                    raise e
