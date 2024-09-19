'''Data collection ui module.'''
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
    '''Page Frame for Data Collection.'''

    def __init__(self, parent: CTk, prev_page: CTkFrame = None, database_name = ""):

        super().__init__(parent, "Data Collection", prev_page)

        self.database = ExperimentDatabase(database_name)
        self.measurement_items = self.database.get_measurement_items()
        self.measurement_strings = []
        self.measurement_ids = []
        for item in self.measurement_items:
            self.measurement_strings.append(item[1])
            self.measurement_ids.append(str(item[1]).lower().replace(" ", "_"))

        self.data_database = DataCollectionDatabase(database_name, self.measurement_strings)

        self.auto_increment_button = CTkButton(self,
                                               text="Start",
                                               compound=TOP,
                                               width=15,
                                               command= self.auto_increment)
        self.auto_increment_button.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.auto_inc_id = -1

        self.animals = self.database.get_animals()
        self.table_frame = CTkFrame(self)
        self.table_frame.place(relx=0.50, rely=0.65, anchor=CENTER)
        


        columns = ['animal_id']
        for measurement_id in self.measurement_ids:
            columns.append(measurement_id)

        self.table = Treeview(self.table_frame,
                              columns=columns, show='headings',
                              selectmode="browse",
                              height=len(self.animals))
        style = Style()
        style.configure("Treeview", font=("Arial", 18), rowheight=40)
        style.configure("Treeview.Heading", font=("Arial", 18))

        for i, column in enumerate(columns):
            text = "Animal ID"
            if i != 0:
                text = self.measurement_strings[i-1]
            self.table.heading(column, text=text)
            print(text)

        self.table.grid(row=0, column=0, sticky='nsew')

        self.date_label = CTkLabel(self)

        for animal in self.animals:
            value = (animal[0], 0, 0)
            self.table.insert('', END, values=value)

        self.get_values_for_date(None)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        self.changer = ChangeMeasurementsDialog(parent, self, self.measurement_strings)


    def item_selected(self, _):
        '''On item selection.

        Records the value selected and opens the changer frame.'''
        self.auto_inc_id = -1
        self.changing_value = self.table.selection()[0]
        self.open_changer()

    def open_changer(self):
        '''Opens the changer frame for the selected animal id.'''
        animal_id = self.table.item(self.changing_value)["values"][0]
        self.changer.open(animal_id)

    def auto_increment(self):
        '''Automatically increments changer to hit each animal.'''
        self.auto_inc_id = 0
        self.open_auto_increment_changer()

    def open_auto_increment_changer(self):
        '''Opens auto changer dialog.'''
        if self.table.get_children() :
            self.changing_value = self.table.get_children()[self.auto_inc_id]
            self.open_changer()
        else:
            print("No animals in databse!")
        

    def change_selected_value(self, values):
        '''Changes the selected value in the table and database.'''
        item = self.table.item(self.changing_value)

        new_values = []

        animal_id = item["values"][0]

        old_measurements = item["values"][1:]

        for val in values:
            new_values.append(val)
        self.table.item(self.changing_value, values=tuple([animal_id] + new_values))


        if("None" in old_measurements):
            self.database.add_data_entry(date.today(), animal_id, new_values)
        else:
            self.database.change_data_entry(date.today(), animal_id, new_values)

        if self.auto_inc_id >= 0 and self.auto_inc_id < len(self.table.get_children()) - 1:
            self.auto_inc_id += 1
            self.open_auto_increment_changer()
        AudioManager.play(filepath="shared/sounds/rfid_success.wav") #play succsess sound

    def get_values_for_date(self, _):
        '''Gets the data for the current date.'''
        self.current_date = str(date.today())
        self.date_label.destroy()
        date_text = "Current Date: " + self.current_date
        self.date_label = CTkLabel(self, text=date_text, font=("Arial", 18))
        self.date_label.place(relx=0.5, rely=0.25, anchor=CENTER)

        values = self.database.get_data_for_date(self.current_date)


        for child in self.table.get_children():
            animal_id = self.table.item(child)["values"][0]
            for val in values:
                if str(val[1]) == str(animal_id):
                    self.table.item(child, values=tuple(val[1:]))
                    break
            else:
                new_values = [animal_id]
                for _ in self.measurement_items:
                    new_values.append(None)
                self.table.item(child, values=tuple(new_values))

    def close_connection(self):
        '''Closes database file.'''
        self.database.close()

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
        AudioManager.play(filepath="shared/sounds/error.wav")

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

