from tkinter import *
from tkinter.ttk import *
from tk_models import *
# from experiment_pages.change_rfid import *
import random
from playsound import playsound
import threading


def get_random_rfid():
    return random.randint(1000000, 9999999)


def play_sound_async(filename):
    threading.Thread(target=playsound, args=(filename,), daemon=True).start()


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

        self.changer = ChangeRFIDDialog(parent, self)
        self.change_rfid_button = Button(self, text="Change RFID", compound=TOP,
                                         width=15, command=self.open_change_rfid)
        self.change_rfid_button.place(relx=0.40, rely=0.85, anchor=CENTER)

        self.delete_button = Button(self, text="Remove Selection(s)", compound=TOP,
                                    width=20, command=self.remove_selected_items)
        self.delete_button.place(relx=0.70, rely=0.85, anchor=CENTER)

        self.item_selected(None)

    def right_click_menu(self, event):
        if len(self.table.selection()) != 0:
            try:
                self.right_click.tk_popup(event.x_root, event.y_root)
            finally:
                self.right_click.grab_release()

    def add_random_rfid(self):
        rfid = get_random_rfid()
        self.add_value(rfid)

    def add_value(self, rfid):
        value = (self.animal_id, rfid)
        self.table.insert('', END, values=value)
        self.animals.append(value)
        self.animal_id += 1
        self.animal_id_entry_text.set(str(self.animal_id))
        play_sound_async('./sounds/rfid_success.mp3')

    def change_selected_value(self, rfid):
        item = self.table.item(self.changing_value)
        self.table.item(self.changing_value, values=(
            item['values'][0], rfid))
        self.change_rfid_button["state"] = "normal"
        play_sound_async('./sounds/rfid_success.mp3')

    def item_selected(self, event):
        selected = self.table.selection()

        if len(selected) != 1:
            self.change_rfid_button["state"] = "disabled"
        else:
            self.change_rfid_button["state"] = "normal"

        if len(selected) == 0:
            self.delete_button["state"] = "disabled"
        else:
            self.delete_button["state"] = "normal"

    def remove_selected_items(self):
        for item in self.table.selection():
            self.table.delete(item)

    def open_change_rfid(self):
        self.changing_value = self.table.selection()[0]
        self.change_rfid_button["state"] = "disabled"
        self.changer.open()



class ChangeRFIDDialog():
    def __init__(self, parent: Tk, map_rfid: MapRFIDPage):
        self.parent = parent
        self.map_rfid = map_rfid

    def open(self):
        self.root = root = Toplevel(self.parent)
        root.title("Change RFID")
        root.geometry('400x400')
        root.resizable(False, False)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

        simulate_rfid_button = Button(root, text="Simulate RFID", compound=TOP,
                                      width=15, command=lambda: self.add_random_rfid())
        simulate_rfid_button.place(relx=0.50, rely=0.20, anchor=CENTER)

        self.root.mainloop()

    def add_random_rfid(self):
        rfid = get_random_rfid()
        self.map_rfid.change_selected_value(rfid)
        self.close()

    def close(self):
        self.root.destroy()


