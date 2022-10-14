from tkinter import *
from tkinter.ttk import *
from tk_models import *
import os

users = {
    'example.student@slu.edu': {
        "first": "Example",
        "last": "Student"
    },
    'another.person@slu.edu': {
        "first": "Another",
        "last": "Person"
    },
    'test@slu.edu': {
        "first": "Test",
        "last": "Person"
    }
}


class ConfigureUsersFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "User Configuration", True, previous_page)

        Label(self, text="Select a User:").place(
            relx=0.15, rely=0.30, anchor=CENTER)

        self.user_select = Combobox(self, width=27)
        self.user_select['values'] = tuple(users.keys())
        self.user_select['state'] = 'readonly'
        self.user_select.place(relx=0.40, rely=0.30, anchor=CENTER)
        self.user_select.bind('<<ComboboxSelected>>', self.display_information)

        self.first_name_label = Label(self)
        self.last_name_label = Label(self)

    def display_information(self, event):
        selected = self.user_select.get()

        self.first_name_label.destroy()
        first_name_text = "First Name:      " + users[selected]["first"]
        self.first_name_label = Label(self, text=first_name_text)
        self.first_name_label.place(
            relx=0.25, rely=0.50)

        self.last_name_label.destroy()
        last_name_text = "Last Name:      " + users[selected]["last"]
        self.last_name_label = Label(self, text=last_name_text)
        self.last_name_label.place(
            relx=0.25, rely=0.55)


class ChangePasswordFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Change Password", True, previous_page)


class ConfigureOrganizationFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Organization Configuration", True, previous_page)


class AccountsFrame(MouserPage):
    def __init__(self, parent: Tk, previous_page: Frame):
        super().__init__(parent, "Accounts", True, previous_page)

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
