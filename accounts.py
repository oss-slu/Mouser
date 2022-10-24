from tkinter import *
from tkinter.ttk import *
from tk_models import *
import copy

users = {
    'example.student@slu.edu': {
        "first": "Example",
        "last": "Student",
        "role": "generic"
    },
    'another.person@slu.edu': {
        "first": "Another",
        "last": "Person",
        "role": "admin"
    },
    'test@slu.edu': {
        "first": "Test",
        "last": "Person",
        "role": "generic"
    }
}

roles = ["generic", "admin"]


class ConfigureUsersFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "User Configuration", previous_page)

        Label(self, text="Email:").place(
            relx=0.12, rely=0.30)

        self.user_select = Combobox(self, width=27)
        self.user_select['values'] = tuple(users.keys())
        self.user_select['state'] = 'readonly'
        self.user_select.place(relx=0.25, rely=0.30)
        self.user_select.bind('<<ComboboxSelected>>', self.display_information)

        self.name_header = Label(self)
        self.name_label = Label(self)
        self.access_header = Label(self)
        self.access_select = Combobox(self)
        self.discard_changes_button = Button(self)
        self.save_changes_button = Button(self)

    def display_information(self, event):

        selected = self.user_select.get()
        self.selected = selected
        self.changed_data = copy.deepcopy(users)

        self.access_header.destroy()
        self.access_header = Label(self, text="Access:")
        self.access_header.place(relx=0.12, rely=0.50)

        self.access_select.destroy()
        self.access_select = Combobox(self, width=27)
        self.access_select['values'] = tuple(roles)
        self.access_select['state'] = 'readonly'
        self.access_select.set(users[selected]["role"])
        self.access_select.place(relx=0.25, rely=0.50)
        self.access_select.bind('<<ComboboxSelected>>', self.set_data)

        self.name_header.destroy()
        self.name_header = Label(self, text="Name:")
        self.name_header.place(relx=0.12, rely=0.40)

        self.name_label.destroy()
        name_text = users[selected]["first"] + " " + users[selected]["last"]
        self.name_label = Label(self, text=name_text)
        self.name_label.place(relx=0.25, rely=0.40)

        self.discard_changes_button.destroy()
        self.discard_changes_button = Button(
            self, text="Discard", compound=TOP, width=15, command=lambda: self.discard_changes())
        self.discard_changes_button.place(relx=0.20, rely=0.70)
        self.discard_changes_button["state"] = "disabled"

        self.save_changes_button.destroy()
        self.save_changes_button = Button(
            self, text="Save", compound=TOP, width=15, command=lambda: self.save_changes())
        self.save_changes_button.place(relx=0.50, rely=0.70)
        self.save_changes_button["state"] = "disabled"

    def set_data(self, event):
        self.changed_data[self.selected]["role"] = self.access_select.get()
        self.detect_changes(None)

    def detect_changes(self, event):
        user = users[self.selected]
        changed = False
        for key in user.keys():
            if (user[key] != self.changed_data[self.selected][key]):
                changed = True
        if (changed):
            self.user_select['state'] = "disabled"
            self.discard_changes_button["state"] = "normal"
            self.save_changes_button["state"] = "normal"
        else:
            self.user_select['state'] = "readonly"
            self.discard_changes_button["state"] = "disabled"
            self.save_changes_button["state"] = "disabled"

    def save_changes(self):
        global users
        users = self.changed_data
        self.detect_changes(None)

    def discard_changes(self):
        self.changed_data = copy.deepcopy(users)
        self.access_select.set(self.changed_data[self.selected]["role"])
        self.detect_changes(None)


class ChangePasswordFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Change Password", previous_page)


class ConfigureOrganizationFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Organization Configuration", previous_page)


class AccountsFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Accounts", previous_page)

        gears_image = PhotoImage(file="./images/gears.png")
        user_settings_frame = ConfigureUsersFrame(parent, self)
        create_nav_button(self, "Configure Users", gears_image,
                          user_settings_frame, 0.33, 0.33)

        lock_image = PhotoImage(file="./images/lock.png")
        change_password_frame = ChangePasswordFrame(parent, self)
        create_nav_button(self, "Change Password", lock_image,
                          change_password_frame, 0.67, 0.33)

        pencil_image = PhotoImage(file="./images/pencil.png")
        organization_settings_frame = ConfigureOrganizationFrame(parent, self)
        create_nav_button(self, "Configure Organization", pencil_image,
                          organization_settings_frame, 0.33, 0.67)
