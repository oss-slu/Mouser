from tkinter import *
from tkinter.ttk import *
from tk_models import *
from getmac import get_mac_address as gma
from database_apis.users_database import UsersDatabase

class LoginFrame(MouserPage):
    def __init__(self, parent: Tk, next_page: Frame):           #if authentication success, move to main frame
        super().__init__(parent, "Login")
        self.next_page = next_page
        
        self.users_database = UsersDatabase()

        self.email = Entry(self, width=40)
        self.email.place(relx=0.50, rely=0.30, anchor=CENTER)
        email_header = Label(self, text="Email:", font=("Arial", 12))
        email_header.place(relx=0.28, rely=0.30, anchor=E)

        self.password = Entry(self, width=40, show="•")
        self.password.place(relx=0.50, rely=0.40, anchor=CENTER)
        password_header = Label(self, text="Password:", font=("Arial", 12))
        password_header.place(relx=0.28, rely=0.40, anchor=E)

        login_button = Button(self, text="Log In", compound=TOP,
                              width=15, command=lambda: self.login())
        login_button.place(relx=0.50, rely=0.50, anchor=CENTER)

        self.auto_login_check = IntVar()
        self.auto_login_checkButton = Checkbutton(self, variable = self.auto_login_check, 
                                                  onvalue = 1, offvalue = 0, text = "Enable Automatic Login", 
                                                width = 24)
        self.auto_login_checkButton.place(relx = 0.50, rely=0.60, anchor=CENTER)
        
        

    def login(self):
        email = self.email.get()
        password = self.password.get()
        success = self.users_database.login(email, password)
        if success:
            if self.auto_login_check.get():
                self.users_database.add_auto_login_information(gma())
            raise_frame(self.next_page)

    def auto_login(self):
        if self.users_database.auto_login(gma()):
            raise_frame(self.next_page)

    def remove_outdated_auto_login(self):
        self.users_database.remove_auto_login_credentials()

        


if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')
    root.resizable(False, False)

    main_frame = MouserPage(root, "Main")
    login_frame = LoginFrame(root, main_frame)

    login_frame.remove_outdated_auto_login()
    login_frame.auto_login()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
