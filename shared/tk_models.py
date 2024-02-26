'''Contains shared tkinter models used througout the program.'''
from tkinter import PhotoImage
from customtkinter import *
from abc import ABC, abstractmethod

current_frame: CTkFrame = None

def raise_frame(frame: CTkFrame): #pylint: disable= redefined-outer-name
    '''Raises passed frame.'''
    global current_frame
    if current_frame:
        current_frame.pack_forget()
    current_frame = frame
    current_frame.pack()

def create_nav_button(parent: CTkFrame, name: str, button_image: PhotoImage, frame: CTkFrame, relx: float, rely: float): #pylint: disable= line-too-long,redefined-outer-name
    '''Makes a navigation button to the various sub-menus of the program.'''

    button = CTkButton(parent, text=name, image=button_image,
                    compound=TOP, width=25, command=lambda: raise_frame(frame))
    button.place(relx=relx, rely=rely, anchor=CENTER)
    button.image = button_image



class MenuButton(CTkButton):
    '''A standard button that navigates backwards in the program.'''
    def __init__(self, page: CTkFrame, previous_page: CTkFrame):

        super().__init__(page, text="Back to Menu", compound=TOP,
                         width=15, command = self.navigate)
        self.place(relx=0.15, rely=0.15, anchor=CENTER)
        self.previous_page = previous_page



    def navigate(self):
        '''Raises the previous_page in the stacking order.'''
        raise_frame(self.previous_page)



class ChangePageButton(CTkButton):
    '''A standard button that navigates somewhere else in the program.'''
    def __init__(self, page: CTkFrame, next_page: CTkFrame, previous: bool = True):
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
        raise_frame(self.next_page)


class MouserPage(CTkFrame):

    '''Standard pageframe used throughout the program.'''
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

        self.menu_button = None
        self.next_button = None
        self.previous_button = None

        if menu_page:
            self.menu_button = MenuButton(self, menu_page)

        self.check_window_size()

    def raise_frame(self):
        '''Raises the page frame in the stacking order.'''
        raise_frame(self)

    def set_next_button(self, next_page):

        '''Sets next_button to be a ChangePageButton that navigates to next_page.'''
        if self.next_button:
            self.next_button.destroy()
        self.next_button = ChangePageButton(self, next_page, False)

    def set_previous_button(self, previous_page):
        '''Sets previous_button to be a ChangePageButton that navigates to previous_page.'''
        if self.previous_button:
            self.previous_button.destroy()
        self.previous_button = ChangePageButton(self, previous_page, False)

    def set_menu_button(self, menu_page):
        '''Sets menu_button to be a ChangePageButton that navigates to menu_page.'''
        if self.menu_button:
            self.menu_button.destroy()
        self.menu_button = MenuButton(self, menu_page)

    def check_window_size(self):
        '''Checks to see if the window size and page size match.If they don't, resizes the page to match'''
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

        self.canvas.coords(self.rectangle, 0, 0, root_width, 50)
        self.canvas.coords(self.title_label, (root_width/2), 13)


class ChangeableFrame(ABC, CTkFrame):
    '''Abstract class.'''
    @abstractmethod
    def update_frame(self):
        '''Abstract update_frame.'''
        pass # pylint: disable= unnecessary-pass

if __name__ == '__main__':
    root = CTk()
    root.title("Template Test")
    root.geometry('600x600')

    main_frame = MouserPage(root, "Main")
    frame = MouserPage(root, "Template")

    main_frame.set_next_button(frame)
    frame.set_previous_button(frame)

    main_frame.raise_frame()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()