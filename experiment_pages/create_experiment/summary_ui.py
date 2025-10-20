'''Experiment Summary UI (modernized, fully functional).'''
from customtkinter import *
from shared.tk_models import *
from shared.scrollable_frame import ScrolledFrame
from shared.experiment import Experiment
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND
from tkinter import filedialog

class SummaryUI(MouserPage):  # pylint: disable= undefined-variable
    '''Displays experiment details before final creation.'''

    def __init__(self, experiment: Experiment, parent: CTk, prev_page: CTkFrame, menu_page: CTkFrame):
        super().__init__(parent, "New Experiment - Summary", prev_page)
        self.experiment = experiment
        self.menu_page = menu_page

        # ----------------------------
        # Top Navigation Buttons
        # ----------------------------
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

        # "Create" button (formerly Next)
        self.create_button = CTkButton(
            self,
            text="Create",
            corner_radius=12,
            height=50,
            width=180,
            font=("Segoe UI Semibold", 18),
            text_color="white",
            fg_color="#2563eb",
            hover_color="#1e40af",
            command=self.create_experiment
        )
        self.create_button.place_configure(relx=0.93, rely=0.13, anchor="e")

        # ----------------------------
        # Scrollable Summary Frame
        # ----------------------------
        scroll_canvas = ScrolledFrame(self)
        scroll_canvas.place(relx=0.5, rely=0.58, relheight=0.7, relwidth=0.9, anchor="center")

        # Main container card
        self.main_frame = CTkFrame(
            scroll_canvas,
            corner_radius=16,
            border_width=1,
            border_color="#d1d5db",
            fg_color=("white", "#2c2c2c")
        )
        self.main_frame.pack(expand=True, pady=10, padx=10, fill="x")

        # Title
        CTkLabel(
            self.main_frame,
            text="Experiment Summary",
            font=("Segoe UI Semibold", 22)
        ).pack(pady=(15, 10))

        # Summary container
        self.summary_card = CTkFrame(
            self.main_frame,
            corner_radius=12,
            fg_color=("white", "#1f2937")
        )
        self.summary_card.pack(padx=40, pady=(5, 15), fill="x")

        # Display experiment info
        self.display_summary()

    # ------------------------------------------------------------
    # Core Methods
    # ------------------------------------------------------------
    def display_summary(self):
        '''Populates the summary UI with experiment details.'''
        details = {
            "Experiment Name": self.experiment.get_name(),
            "Investigators": ", ".join(self.experiment.get_investigators()),
            "Species": self.experiment.get_species(),
            "Measurement Items": self.experiment.get_measurement_items(),
            "Number of Animals": self.experiment.get_num_animals(),
            "Animals per Cage": self.experiment.get_max_animals(),
            "Group Names": ", ".join(self.experiment.group_names)
            if hasattr(self.experiment, "group_names") else "",
            "Uses RFID": "Yes" if self.experiment.uses_rfid() else "No",
        }

        # Inner grid layout for summary
        grid = CTkFrame(self.summary_card, fg_color="transparent")
        grid.pack(pady=(10, 10), padx=15, anchor="w")

        font_label = CTkFont("Segoe UI", 16, "bold")
        font_value = CTkFont("Segoe UI", 16)

        for i, (label, value) in enumerate(details.items()):
            CTkLabel(grid, text=f"{label}:", font=font_label).grid(
                row=i, column=0, sticky="w", padx=10, pady=5)
            CTkLabel(grid, text=value or "—", font=font_value).grid(
                row=i, column=1, sticky="w", padx=10, pady=5)

    def update_page(self):
        '''Refresh summary when experiment data changes.'''
        for widget in self.summary_card.winfo_children():
            widget.destroy()
        self.display_summary()

    def create_experiment(self):
        '''Handles final experiment creation.'''
        # Save the experiment to file
        save_dir = filedialog.askdirectory(title="Select Directory to Save Experiment")
        if save_dir:
            self.experiment.save_to_database(save_dir)

        AudioManager.play(SUCCESS_SOUND)

        # Confirmation popup
        popup = CTkToplevel(self)
        popup.title("Experiment Created")
        popup.geometry("320x160")
        popup.resizable(False, False)

        CTkLabel(popup, text="Experiment successfully created!", font=("Segoe UI", 16, "bold")).pack(pady=20)
        CTkButton(
            popup,
            text="OK",
            command=popup.destroy,
            corner_radius=8,
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
            width=80
        ).pack(pady=10)
