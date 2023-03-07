from tkinter import *
from tkinter.ttk import *
from tkcalendar import Calendar

from tk_models import *

from database_apis.experiment_database import ExperimentDatabase

class DataCollectionUI(MouserPage):
    def __init__(self, parent: Tk, prev_page: Frame = None, database_name = ""):
        super().__init__(parent, "Data Collection", prev_page)
        self.database = ExperimentDatabase("databases/experiments/" + database_name + ".db")
        self.animals = self.database.get_animals()
        self.table_frame = Frame(self)
        self.table_frame.place(relx=0.50, rely=0.75, anchor=CENTER)
        
        columns = ('animal_id', 'weight', 'tail_length')
        self.table = Treeview(
            self.table_frame, columns=columns, show='headings', selectmode="browse")

        self.table.heading('animal_id', text='Animal ID')
        self.table.heading('weight', text='Weight')
        self.table.heading('tail_length', text='Tail Length')

        self.table.grid(row=0, column=0, sticky='nsew')
        
        self.calendar = Calendar(self, selectmode = 'day')
        self.calendar.place(relx=0.50, rely=0.35, anchor=CENTER)
        
        for animal in self.animals:
            value = (animal[0], 0, 0)
            self.table.insert('', END, values=value)

        self.table.bind('<<TreeviewSelect>>', self.item_selected)
        
        self.changer = ChangeMeasurementsDialog(parent, self)
    
    def item_selected(self, event):
        self.changing_value = self.table.selection()[0]
        self.changer.open()
        
    def change_selected_value(self, values):
        item = self.table.item(self.changing_value)
        newValues = [item['values'][0]]
        for val in values:
            newValues.append(val)
        self.table.item(self.changing_value, values=tuple(newValues))

class ChangeMeasurementsDialog():
    def __init__(self, parent: Tk, data_collection: DataCollectionUI):
        self.parent = parent
        self.data_collection = data_collection

    def open(self):
        self.root = root = Toplevel(self.parent)
        root.title("Modify Measurements")
        root.geometry('400x400')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        self.textboxes = []
        valueList = ["Weight", "Tail Length"]
        count = len(valueList) + 1
        for i in range(1, count):
            posY = i / count
            entry = Entry(root, width=40)
            entry.place(relx=0.60, rely=posY, anchor=CENTER)
            entry.bind("<KeyRelease>", self.check_if_num)
            self.textboxes.append(entry)
            
            header = Label(root, text=valueList[i-1]+": ", font=("Arial", 12))
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
        self.data_collection.change_selected_value(self.get_all_values())
        self.close()

    def close(self):
        self.root.destroy()
        