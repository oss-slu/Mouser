from tkinter import *
from tkinter.ttk import *

from tk_models import *
from authentication import *

# from scroll_tkmodels_test import *

class LoginFrame(MouserPage):
    def __init__(self, parent: Tk, next_page: Frame):
        super().__init__(parent, "Login")
        self.next_page = next_page

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

    def login(self):
        email = self.email.get()
        password = self.password.get()
        success = login(email, password)
        if success:
            raise_frame(self.next_page)


if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')
    root.resizable(False, False)

    main_frame = MouserPage(root, "Main")
    login_frame = LoginFrame(root, main_frame)

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
