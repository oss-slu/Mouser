'''Data collection ui module.'''
import os
from datetime import date
from tkinter.ttk import Treeview, Style
from customtkinter import *

from shared.tk_models import *

from databases.experiment_database import ExperimentDatabase
from databases.data_collection_database import DataCollectionDatabase
from shared.audio import AudioManager
from shared.scrollable_frame import ScrolledFrame

#pylint: disable= undefined-variable
class DataCollectionUI(MouserPage):
    def __init__(self, parent: CTk, prev_page: CTkFrame = None, database_name=""):
        super().__init__(parent, "Data Collection", prev_page)
        temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
        os.makedirs(temp_folder_path, exist_ok=True)
        temp_file_name =  os.path.basename(filepath)
        temp_file_path = os.path.join(temp_folder_path, temp_file_name)

    with open(filepath, 'rb') as file:
        data = file.read()

    with open(temp_file_path, 'wb') as file:
        file.write(data)
        file.seek(0)

    return temp_file_path

        self.database = ExperimentDatabase("databases/experiments/" + database_name + ".db")
        self.measurement_items = self.database.get_measurement_items()
        self.measurement_strings = [item[1] for item in self.measurement_items]
        self.measurement_ids = [str(item[1]).lower().replace(" ", "_") for item in self.measurement_items]

        self.data_database = DataCollectionDatabase(database_name, self.measurement_strings)

        # Setup the start button
        self.auto_increment_button = CTkButton(self, text="Start", width=200, height=40, command=self.auto_increment)
        self.auto_increment_button.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.auto_inc_id = -1

        self.animals = self.database.get_animals()
        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.50, rely=0.65, anchor=CENTER)


        columns = ['animal_id'] + self.measurement_ids
        self.table = Treeview(self.table_frame, columns=columns, show='headings', selectmode="browse", height=len(self.animals))
        style = Style()
        style.configure("Treeview", font=("Arial", 18), rowheight=40)
        style.configure("Treeview.Heading", font=("Arial", 18))

        for i, column in enumerate(columns):
            text = "Animal ID" if i == 0 else self.measurement_strings[i-1]
            self.table.heading(column, text=text)

        self.table.grid(row=0, column=0, sticky='nsew')

        self.date_label = CTkLabel(self, text="Current Date: " + str(date.today()), font=("Arial", 18))
        self.date_label.place(relx=0.5, rely=0.25, anchor=CENTER)

        for animal in self.animals:
            values = [animal[0]] + [0] * len(self.measurement_ids)
            self.table.insert('', 'end', values=values)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)
        self.changer = ChangeMeasurementsDialog(parent, self, self.measurement_strings)

    def item_selected(self, _):
        self.auto_inc_id = -1
        self.changing_value = self.table.selection()[0]
        self.open_changer()

    def open_changer(self):
        animal_id = self.table.item(self.changing_value)["values"][0]
        self.changer.open(animal_id)

    def auto_increment(self):
        if self.auto_inc_id == -1 or self.auto_inc_id >= len(self.table.get_children()) - 1:
            self.auto_inc_id = 0
        else:
            self.auto_inc_id += 1
        self.open_auto_increment_changer()

    def open_auto_increment_changer(self):
        self.changing_value = self.table.get_children()[self.auto_inc_id]
        self.open_changer()

    def change_selected_value(self, values):
        item = self.table.item(self.changing_value)
        new_values = [item['values'][0]] + list(values)
        self.table.item(self.changing_value, values=tuple(new_values))
        self.data_database.set_data_for_entry(tuple([self.current_date] + new_values))

    def close_connection(self):
        self.database.close()

class ChangeMeasurementsDialog():
    def __init__(self, parent: CTk, data_collection: DataCollectionUI, measurement_items):
        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = measurement_items

    def open(self, animal_id):
        self.root = CTkToplevel(self.parent)
        self.root.title("Modify Measurements")
        self.root.geometry('600x600')
        self.root.resizable(False, False)

        id_label = CTkLabel(self.root, text="Animal ID: " + str(animal_id), font=("Arial", 18))
        id_label.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.textboxes = []
        for i, item in enumerate(self.measurement_items, start=1):
            posY = 0.1 + i * 0.1
            entry = CTkEntry(self.root, width=40)
            entry.place(relx=0.60, rely=posY, anchor=CENTER)
            self.textboxes.append(entry)
            
            header = CTkLabel(self.root, text=item + ": ", font=("Arial", 18))
            header.place(relx=0.28, rely=posY, anchor=E)

        self.submit_button = CTkButton(self.root, text="Submit", width=100, command=self.finish)
        self.submit_button.place(relx=0.97, rely=0.97, anchor=SE)
        self.root.mainloop()

    def finish(self):
        values = [entry.get() for entry in self.textboxes]
        self.data_collection.change_selected_value(values)
        self.close()

    def close(self):
        self.root.destroy()

class ChangeMeasurementsDialog():
    '''Change Measurement Dialog window.'''
    def __init__(self, parent: CTk, data_collection: DataCollectionUI, measurement_items: list):

        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = measurement_items

    def open(self, animal_id):
        '''Opens the change measurement dialog window.'''
        self.root = root = CTkToplevel(self.parent)
        root.title("Modify Measurements")
        root.geometry('600x600')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        id_label = CTkLabel(root, text="Animal ID: "+str(animal_id), font=("Arial", 18))
        id_label.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.textboxes = []
        count = len(self.measurement_items) + 1

        for i in range(1, count):

            pos_y = i / count
            entry = CTkEntry(root, width=40)
            entry.place(relx=0.60, rely=pos_y, anchor=CENTER)
            entry.bind("<KeyRelease>", self.check_if_num)
            self.textboxes.append(entry)

            header = CTkLabel(root, text=self.measurement_items[i-1]+": ", font=("Arial", 18))
            header.place(relx=0.28, rely=pos_y, anchor=E)

            if i == 1:
                entry.focus()

        self.error_text = CTkLabel(root, text="One or more values are not a number")
        self.submit_button = CTkButton(root, text="Submit", compound=TOP, width=15, command= self.finish)
        self.submit_button.place(relx=0.97, rely=0.97, anchor=SE)

        self.root.mainloop()

    def check_if_num(self, _):
        '''Checks if the values are numbers.'''
        errors = 0
        values = self.get_all_values()
        for value in values:
            try:
                float(value)
            except ValueError:
                self.show_error()
                errors += 1
        if errors == 0:
            self.error_text.place_forget()
            self.submit_button["state"] = "normal"

    def show_error(self):
        '''Displays an error window.'''
        self.error_text.place(relx=0.5, rely=0.85, anchor=CENTER)
        self.submit_button["state"] = "disabled"
        AudioManager.play(filepath="sounds/error.wav")

    def get_all_values(self):
        '''Returns the values of all entries in self.textboxes as an array.'''
        values = []
        for entry in self.textboxes:
            value = str(entry.get())
            value = value.strip()
            if value == "":
                value = "0"
            values.append(value)
        return tuple(values)

    def finish(self):
        '''Cleanup when done with change value dialog.'''
        values = self.get_all_values()
        self.close()
        self.data_collection.change_selected_value(values)

    def close(self):
        '''Closes change value dialog window.'''
        self.root.destroy()
