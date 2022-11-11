from tkinter import *
from tkinter.ttk import *
from tk_models import *
import random


class MapRFIDPage(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame = None):
        super().__init__(parent, "Map RFID", previous_page)
        self.animals = []
        self.animal_id = 1

        self.animal_id_entry_text = StringVar(value="1")

        self.animal_id_entry = Entry(
            self, width=40, textvariable=self.animal_id_entry_text)
        self.animal_id_entry.place(relx=0.50, rely=0.20, anchor=CENTER)
        animal_id_header = Label(self, text="Animal ID:", font=("Arial", 12))
        animal_id_header.place(relx=0.28, rely=0.20, anchor=E)

        simulate_rfid_button = Button(self, text="Simulate RFID", compound=TOP,
                                      width=15, command=lambda: self.add_random_rfid())
        simulate_rfid_button.place(relx=0.80, rely=0.20, anchor=CENTER)

        self.table_frame = Frame(self)
        self.table_frame.place(relx=0.15, rely=0.40)

        columns = ('animal_id', 'rfid')
        self.table = Treeview(
            self.table_frame, columns=columns, show='headings')

        self.table.heading('animal_id', text='Animal ID')
        self.table.heading('rfid', text='RFID')

        self.table.grid(row=0, column=0, sticky='nsew')
        scrollbar = Scrollbar(
            self.table_frame, orient=VERTICAL, command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky='ns')

        self.table.bind('<<TreeviewSelect>>', self.item_selected)

        self.right_click = Menu(self, tearoff=0)
        self.right_click.add_command(
            label="Remove Selection(s)", command=self.remove_selected_items)
        self.table.bind("<Button-3>", self.right_click_menu)

    def right_click_menu(self, event):
        if len(self.table.selection()) != 0:
            try:
                self.right_click.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click.grab_release()

    def add_random_rfid(self):
        rfid = random.randint(1000000, 9999999)
        self.add_value(rfid)

    def add_value(self, rfid):
        value = (self.animal_id, rfid)
        self.table.insert('', END, values=value)
        self.animals.append(value)
        self.animal_id += 1
        self.animal_id_entry_text.set(str(self.animal_id))

    def item_selected(self, event):
        for selected_item in self.table.selection():
            item = self.table.item(selected_item)
            record = item['values']

    def remove_selected_items(self):
        for item in self.table.selection():
            self.table.delete(item)


if __name__ == '__main__':
    root = Tk()
    root.title("")
    root.geometry('600x600')
    root.resizable(False, False)

    rfid = MapRFIDPage(root)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
