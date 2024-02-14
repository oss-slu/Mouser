'''Contains shared tkinter models used througout the program.'''
from tkinter import *
from tkinter.ttk import *
from abc import ABC, abstractmethod

def raise_frame(raised_frame: Frame):
    '''Raises the frame in the stacking order.'''
    raised_frame.tkraise()


def create_nav_button(parent: Frame, name: str, button_image: PhotoImage, raised_frame: Frame, relx: float, rely: float):
    '''Makes a navigation button to the various sub-menus of the program.'''
    button = Button(parent, text=name, image=button_image,
                    compound=TOP, width=25, command = lambda: raise_frame(raised_frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image


class MenuButton(Button):
    '''A standard button that navigates backwards in the program.'''
    def __init__(self, page: Frame, previous_page: Frame):
        super().__init__(page, text="Back to Menu", compound=TOP,
                         width=15, command = self.navigate)
        self.place(relx=0.15, rely=0.15, anchor=CENTER)
        self.previous_page = previous_page

    def navigate(self):
        '''Raises the previous_page in the stacking order.'''
        self.previous_page.tkraise()


class ChangePageButton(Button):
    '''A standard button that navigates somewhere else in the program.'''
    def __init__(self, page: Frame, next_page: Frame, previous: bool = True):
        text = "Next"
        x = 0.75
        if previous:
            text = "Previous"
            x = 0.25
        super().__init__(page, text=text, compound=TOP,
                         width=15, command = self.navigate)
        self.place(relx=x, rely=0.85, anchor=CENTER)
        self.next_page = next_page

    def navigate(self):
        '''Raises the next_page in the stacking order.'''
        self.next_page.tkraise()


class MouserPage(Frame):
    '''Standard pageframe used throught the program.'''
    def __init__(self, parent: Tk, title: str, menu_page: Frame = None):
        super().__init__(parent)
        self.title = title

        self.canvas = Canvas(self, width=600, height=600)
        self.canvas.grid(row=0, column=0, columnspan= 4)
        self.rectangle = self.canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        self.title_label = self.canvas.create_text(300, 13, anchor="n")
        self.canvas.itemconfig(self.title_label, text=title, font=("Arial", 18))
        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)

        self.menu_button = MenuButton(self, menu_page) if menu_page else None
        self.next_button = None
        self.previous_button = None

        self.check_window_size()

    def raise_frame(self):
        '''Raises the page frame in the stacking order.'''
        self.tkraise()

    def set_next_button(self, next_page):
        '''Sets next_button to be a ChangePageButton that naviages to next_page.'''
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)

    def set_previous_button(self, previous_page):
        '''Sets previous_button to be a ChangePageButton that naviages to previous_page.'''
        if self.previous_button:
            self.previous_button.destroy()
        self.previous_button = ChangePageButton(self, previous_page)

    def set_menu_button(self, menu_page):
        '''Sets menu_button to be a ChangePageButton that naviages to menu_page.'''
        if self.menu_button:
            self.menu_button.destroy()
        self.menu_button = MenuButton(self, menu_page)

    def check_window_size(self):
        '''checks to see if the window size and page size match.
        If they don't, resizes the page to match.
        '''
        window = self.winfo_toplevel()
        if window.winfo_height() != self.canvas.winfo_height():
            self.resize_canvas_height(window.winfo_height())
        if window.winfo_width() != self.canvas.winfo_width():
            self.resize_canvas_width(window.winfo_width())

        self.after(10, self.check_window_size)

    def resize_canvas_height(self, root_height):
        '''Resizes page height.'''
        self.canvas.config(height=root_height)

    def resize_canvas_width(self, root_width):
        '''Resizes page width.'''
        self.canvas.config(width=root_width)

        x0, y0, _, y2 = self.canvas.coords(self.rectangle)
        _, y3 = self.canvas.coords(self.title_label)
        self.canvas.coords(self.rectangle, x0, y0, root_width, y2)
        self.canvas.coords(self.title_label, (root_width/2), y3)


class ChangeableFrame(ABC, Frame):
    '''Abstract class.'''

    @abstractmethod
    def update_frame(self):
        '''Abstract update_frame.'''
        pass

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
