from tkinter import *
from tkinter.ttk import *


def raise_frame(frame: Frame):
    frame.tkraise()


def create_nav_button(parent: Frame, name: str, buttonImage: PhotoImage, frame: Frame, relx: float, rely: float):
    button = Button(parent, text=name, image=buttonImage,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)


class BackButton(Button):
    def __init__(self, page: Frame, previousPage: Frame):
        super().__init__(page, text="Back", compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.place(relx=0.15, rely=0.05, anchor=CENTER)
        self.previousPage = previousPage

    def navigate(self):
        self.previousPage.tkraise()


class MouserPage(Frame):
    def __init__(self, parent: Tk, title: str, backButton: bool = False, previousPage: Frame = None, font=("Arial", 25)):
        super().__init__(parent)
        self.title = title
        titleLabel = Label(self, text=title, font=font)
        titleLabel.grid(row=0, column=0, columnspan=4, sticky=N)
        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        if (backButton):
            self.backButton = BackButton(self, previousPage)
        else:
            self.backButton = None

    def raiseFrame(self):
        self.tkraise()


if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')

    mainFrame = MouserPage(root, "Main")
    frame = MouserPage(root, "Template", True, mainFrame)
    frame.raiseFrame()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
