from tkinter import *
from tkinter.ttk import *
from datetime import date

from tk_models import *

from database_apis.experiment_database import ExperimentDatabase
from database_apis.data_collection_database import DataCollectionDatabase

class DataCollectionUI(MouserPage):
    def __init__(self, parent: Tk, prev_page: Frame = None, database_name = ""):
        super().__init__(parent, "Data Collection", prev_page)
        
        self.database = ExperimentDatabase("databases/experiments/" + database_name + ".db")
        self.measurement_items = self.database.get_measurement_items()
        self.measurement_strings = []
        self.measurement_ids = []
        for item in self.measurement_items:
            self.measurement_strings.append(item[1])
            self.measurement_ids.append(str(item[1]).lower().replace(" ", "_"))
            
        self.data_database = DataCollectionDatabase(database_name, self.measurement_strings)
        
        self.auto_increment_button = Button(self, text="Start", compound=TOP, width=15, command=lambda: self.auto_increment())
        self.auto_increment_button.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.auto_inc_id = -1
        
        self.animals = self.database.get_animals()
        self.table_frame = Frame(self)
        self.table_frame.place(relx=0.50, rely=0.65, anchor=CENTER)
        
        columns = ['animal_id']
        for id in self.measurement_ids:
            columns.append(id)
            
        
        self.table = Treeview(self.table_frame, columns=columns, show='headings', selectmode="browse", height=len(self.animals))
        style = Style()
        style.configure("Treeview", font=("Arial", 18), rowheight=40)
        style.configure("Treeview.Heading", font=("Arial", 18))

        for i, column in enumerate(columns):
            text = "Animal ID"
            if i != 0:
                text = self.measurement_strings[i-1]
            self.table.heading(column, text=text)

        self.table.grid(row=0, column=0, sticky='nsew')

        self.date_label = Label(self)
        
        for animal in self.animals:
            value = (animal[0], 0, 0)
            self.table.insert('', END, values=value)
            
        self.get_values_for_date(None)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)
        
        self.changer = ChangeMeasurementsDialog(parent, self, self.measurement_strings)
    
    def item_selected(self, event):
        self.auto_inc_id = -1
        self.changing_value = self.table.selection()[0]
        self.open_changer()
        
    def open_changer(self):
        animal_id = self.table.item(self.changing_value)["values"][0]
        self.changer.open(animal_id)
        
    def auto_increment(self):
        self.auto_inc_id = 0
        self.open_auto_increment_changer()
        
    def open_auto_increment_changer(self):
        self.changing_value = self.table.get_children()[self.auto_inc_id]
        self.open_changer()
        
    def change_selected_value(self, values):
        item = self.table.item(self.changing_value)
        new_values = [self.current_date, item['values'][0]]
        for val in values:
            new_values.append(val)
        self.table.item(self.changing_value, values=tuple(new_values[1:]))
        self.data_database.set_data_for_entry(tuple(new_values))
        if self.auto_inc_id >= 0 and self.auto_inc_id < len(self.table.get_children()) - 1:
            self.auto_inc_id += 1
            self.open_auto_increment_changer()
        
    def get_values_for_date(self, event):
        self.current_date = str(date.today())
        self.date_label.destroy()
        date_text = "Current Date: " + self.current_date
        self.date_label = Label(self, text=date_text, font=("Arial", 18))
        self.date_label.place(relx=0.5, rely=0.25, anchor=CENTER)
        values = self.data_database.get_data_for_date(self.current_date)
        for child in self.table.get_children():
            animal_id = self.table.item(child)["values"][0]
            for val in values:
                if str(val[1]) == str(animal_id):
                    self.table.item(child, values=tuple(val[1:]))
                    break
            else:
                new_values = [animal_id]
                for item in self.measurement_items:
                    new_values.append(0)
                self.table.item(child, values=tuple(new_values))
                
    def close_connection(self):
        self.database.close()

class ChangeMeasurementsDialog():
    def __init__(self, parent: Tk, data_collection: DataCollectionUI, measurement_items: list):
        self.parent = parent
        self.data_collection = data_collection
        self.measurement_items = measurement_items

    def open(self, animal_id):
        self.root = root = Toplevel(self.parent)
        root.title("Modify Measurements")
        root.geometry('600x600')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        id_label = Label(root, text="Animal ID: "+str(animal_id), font=("Arial", 18))
        id_label.place(relx=0.5, rely=0.1, anchor=CENTER)
        
        self.textboxes = []
        count = len(self.measurement_items) + 1

        for i in range(1, count):
            posY = i / count
            entry = Entry(root, width=40)
            entry.place(relx=0.60, rely=posY, anchor=CENTER)
            entry.bind("<KeyRelease>", self.check_if_num)
            self.textboxes.append(entry)
            
            header = Label(root, text=self.measurement_items[i-1]+": ", font=("Arial", 18))
            header.place(relx=0.28, rely=posY, anchor=E)
            
            if i == 1:
                entry.focus()
                
        self.error_text = Label(root, text="One or more values are not a number")
        self.submit_button = Button(root, text="Submit", compound=TOP, width=15, command=lambda: self.finish())
        self.submit_button.place(relx=0.97, rely=0.97, anchor=SE)

        self.root.mainloop()

    def check_if_num(self, event):
        errors = 0
        values = self.get_all_values()
        for value in values:
            try:
                num = float(value)
            except ValueError:
                self.show_error()
                errors += 1
        if errors == 0:
            self.error_text.place_forget()
            self.submit_button["state"] = "normal"
            
    def show_error(self):
        self.error_text.place(relx=0.5, rely=0.85, anchor=CENTER)
        self.submit_button["state"] = "disabled"
        
    def get_all_values(self):
        values = []
        for entry in self.textboxes:
            value = str(entry.get())
            value = value.strip()
            if value == "":
                value = "0"
            values.append(value)
        return tuple(values)

    def finish(self):
        values = self.get_all_values()
        self.close()
        self.data_collection.change_selected_value(values)

    def close(self):
        self.root.destroy()
        