from tkinter import *
from tkinter.ttk import *


def raise_frame(frame: Frame):
    frame.tkraise()


def create_nav_button(parent: Frame, name: str, button_image: PhotoImage, frame: Frame, relx: float, rely: float):
    button = Button(parent, text=name, image=button_image,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image


class BackButton(Button):
    def __init__(self, page: Frame, previous_page: Frame):
        super().__init__(page, text="Back", compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.place(relx=0.15, rely=0.10, anchor=CENTER)
        self.previous_page = previous_page

    def navigate(self):
        self.previous_page.tkraise()


class MouserPage(Frame):
    def __init__(self, parent: Tk, title: str, back_button: bool = False, previous_page: Frame = None, font=("Arial", 25)):
        super().__init__(parent)
        self.title = title
        title_label = Label(self, text=title, font=font)
        title_label.grid(row=0, column=0, columnspan=4, sticky=N)
        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        if (back_button):
            self.back_button = BackButton(self, previous_page)
        else:
            self.back_button = None

    def raiseFrame(self):
        self.tkraise()


if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')

    main_frame = MouserPage(root, "Main")
    frame = MouserPage(root, "Template", True, main_frame)
    frame.raiseFrame()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
