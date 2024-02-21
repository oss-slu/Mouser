from tkinter import PhotoImage
from customtkinter import *
from abc import ABC, abstractmethod

current_frame: CTkFrame = None

def raise_frame(frame: CTkFrame):
    global current_frame
    if current_frame:
        current_frame.pack_forget()
    current_frame = frame
    current_frame.pack()

def create_nav_button(parent: CTkFrame, name: str, button_image: PhotoImage, frame: CTkFrame, relx: float, rely: float):
    button = CTkButton(parent, text=name, image=button_image,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image


class MenuButton(CTkButton):
    def __init__(self, page: CTkFrame, previous_page: CTkFrame):
        super().__init__(page, text="Back to Menu", compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.place(relx=0.15, rely=0.15, anchor=CENTER)
        self.previous_page = previous_page

    def navigate(self):
        raise_frame(self.previous_page)


class ChangePageButton(CTkButton):
    def __init__(self, page: CTkFrame, next_page: CTkFrame, previous: bool = True):
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
        raise_frame(self.next_page)


class MouserPage(CTkFrame):
    def __init__(self, parent: CTk, title: str, menu_page: CTkFrame = None):
        super().__init__(parent)
        self.root = parent
        self.title = title

        self.canvas = CTkCanvas(self, width=600, height=600)
        self.canvas.grid(row=0, column=0, columnspan= 4)
        self.rectangle = self.canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        self.title_label = self.canvas.create_text(300, 13, anchor="n")
        self.canvas.itemconfig(self.title_label, text=title, font=("Arial", 18))

        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)

        self.menu_button = MenuButton(self, menu_page) if menu_page else None
        self.next_button = None
        self.previous_button = None

        self.check_window_size()

    def raise_frame(self):
        raise_frame(self)

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
        self.menu_button = MenuButton(self, menu_page)

    def check_window_size(self):
        root = self.winfo_toplevel()
        if root.winfo_height() != self.canvas.winfo_height():
            self.resize_canvas_height(root.winfo_height())
        if root.winfo_width() != self.canvas.winfo_width():
            self.resize_canvas_width(root.winfo_width())

        self.after(10, self.check_window_size)

    def resize_canvas_height(self, root_height):
        self.canvas.config(height=root_height)

    def resize_canvas_width(self, root_width):
        self.canvas.config(width=root_width)

        self.canvas.coords(self.rectangle, 0, 0, root_width, 50)
        self.canvas.coords(self.title_label, (root_width/2), 13)


class ChangeableFrame(ABC, CTkFrame):

    @abstractmethod
    def update_frame(self):
        pass


if __name__ == '__main__':
    root = CTk()
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
