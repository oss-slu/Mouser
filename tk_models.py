from tkinter import *
from tkinter.ttk import *


def raise_frame(frame: Frame):
    frame.tkraise()


def create_nav_button(parent: Frame, name: str, button_image: PhotoImage, frame: Frame, relx: float, rely: float):
    button = Button(parent, text=name, image=button_image,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image


class MenuButton(Button):
    def __init__(self, page: Frame, previous_page: Frame):
        super().__init__(page, text="Back to Menu", compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.place(relx=0.15, rely=0.10, anchor=CENTER)
        self.previous_page = previous_page

    def navigate(self):
        self.previous_page.tkraise()


class ChangePageButton(Button):
    def __init__(self, page: Frame, next_page: Frame, previous: bool = True):
        text = "Next"
        x = 0.75
        if previous:
            text = "Previous"
            x = 0.25
        super().__init__(page, text=text, compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.place(relx=x, rely=0.85, anchor=CENTER)
        self.next_page = next_page

    def navigate(self):
        self.next_page.tkraise()


class MouserPage(Frame):
    def __init__(self, parent: Tk, title: str, menu_page: Frame = None):
        super().__init__(parent)
        self.title = title

        canvas = Canvas(self, width=600, height=600)
        canvas.grid(row=0, column=0, columnspan=4)
        rectangle = canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        titleLabel = canvas.create_text(300, 13, anchor="n")
        canvas.itemconfig(titleLabel, text=title, font=("Arial", 18))

        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.menu_button = MenuButton(self, menu_page) if menu_page else None
        self.next_button = None
        self.previous_button = None

    def raise_frame(self):
        self.tkraise()

    def set_next_button(self, next_page):
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)

    def set_previous_button(self, previous_page):
        if self.previous_button:
            self.previous_button.destroy()
        self.previous_button = ChangePageButton(self, previous_page)

    def set_menu_button(self, menu_page):
        if self.menu_button:
            self.menu_button.destroy()
        self.menu_button = MenuButton(self, menu_page, False)


if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')

    main_frame = MouserPage(root, "Main")
    frame = MouserPage(root, "Template")

    main_frame.set_next_button(frame)
    frame.set_previous_button(main_frame)

    main_frame.raise_frame()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()
