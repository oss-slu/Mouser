from tkinter import *
from tkinter.ttk import *
# from tk_models import *


class AccountsFrame(Frame):
    def __init__(self, parent: Tk, previousPage: Frame):
        super().__init__(parent)
        titleLabel = Label(self, text="Accounts", font=("Arial", 25))
        titleLabel.grid(row=0, column=0, columnspan=4, sticky=N)
        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # back = BackButton(self, previousPage)

    # def navigateToPage(self, pageNum: int):
    #     if pageNum == 0:


if __name__ == '__main__':
    root = Tk()
    root.title("Accounts Test")
    root.geometry('600x600')
    mainFrame = Frame(root)
    mainFrame.grid(row=0, column=0, sticky="NESW")
    mainFrame.grid_rowconfigure(0, weight=1)
    mainFrame.grid_columnconfigure(0, weight=1)
    frame = AccountsFrame(root, mainFrame)
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.mainloop()
