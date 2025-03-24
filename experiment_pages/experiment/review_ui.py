
#pylint: skip-file
from databases.experiment_database import ExperimentDatabase
from shared.tk_models import *

class ReviewUI(MouserPage):
    '''Review User Interface for experiment summary.'''
    def __init__(self, parent: CTk, prev_page: CTkFrame, database_name: str = ""):
        super().__init__(parent, "Review Experiment - Summary", prev_page)
        
        self.database = ExperimentDatabase(database_name)

        self.main_frame = CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=0, sticky='NESW')
        self.main_frame.place(relx=0.5, rely=0.5, anchor=CENTER) #pylint: disable = undefined-variable

        # Example usage with getter
        name_label = CTkLabel(
            self.main_frame,
            text=f"Experiment name: " + database_name,
        )
        name_label.place(relx=0.5, rely=0.1, anchor=CENTER) #pylint: disable = undefined-variable

        # Adding additional text
        additional_text_label = CTkLabel(
            self.main_frame,
            text="Additional information goes here."
        )
        additional_text_label.place(relx=0.5, rely=0.2, anchor=CENTER) #pylint: disable = undefined-variable

        self.create_summary_frame()


    def create_summary_frame(self):
        '''Creates and populates the summary frame with experiment data.'''
        pad_x, pad_y = 10, 10
        font = CTkFont("Arial", 14)

        # Experiment name
        name = self.database.get_experiment_id()
        CTkLabel(self.main_frame, text=f"Experiment ID: {name}", font=font).grid(row=0, column=0, sticky=W, padx=pad_x, pady=pad_y)

        # Investigators
        inv_raw = self.database._c.execute("SELECT investigators FROM experiment").fetchone()
        investigators = inv_raw[0].split(",") if inv_raw and inv_raw[0] else []
        CTkLabel(self.main_frame, text="Investigators:", font=font).grid(row=1, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="\n".join(investigators)).grid(row=1, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Species
        species = self.database._c.execute("SELECT species FROM experiment").fetchone()[0]
        CTkLabel(self.main_frame, text="Species:", font=font).grid(row=2, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text=species).grid(row=2, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Measurement item
        measurement = self.database.get_measurement_name()
        CTkLabel(self.main_frame, text="Measurement Item:", font=font).grid(row=3, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text=measurement).grid(row=3, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Number of animals
        num_animals = self.database.get_total_number_animals()
        CTkLabel(self.main_frame, text="Number of Animals:", font=font).grid(row=4, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text=str(num_animals)).grid(row=4, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Animals per cage
        cage_max = self.database.get_cage_capacity(1)  # assuming all groups have same cage cap
        CTkLabel(self.main_frame, text="Animals per Cage:", font=font).grid(row=5, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text=str(cage_max)).grid(row=5, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Group names
        groups = self.database.get_groups()
        CTkLabel(self.main_frame, text="Group Names:", font=font).grid(row=6, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="\n".join(groups)).grid(row=6, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Uses RFID
        rfid = self.database.experiment_uses_rfid()
        CTkLabel(self.main_frame, text="Uses RFID:", font=font).grid(row=7, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="Yes" if rfid else "No").grid(row=7, column=1, sticky=W, padx=pad_x, pady=pad_y)

        # Measurement Type
        type_val = self.database.get_measurement_type()
        CTkLabel(self.main_frame, text="Measurement Type:", font=font).grid(row=8, column=0, sticky=W, padx=pad_x, pady=pad_y)
        CTkLabel(self.main_frame, text="Automatic" if type_val == 1 else "Manual").grid(row=8, column=1, sticky=W, padx=pad_x, pady=pad_y)
