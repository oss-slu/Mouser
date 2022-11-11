from tkinter import *
from tkinter.ttk import *



class MenuButton(Button):
    def __init__(self, page: Frame, previous_page: Frame):
        super().__init__(page, text="Back to Menu", compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.grid(row=0, column=0)
        self.previous_page = previous_page

    def navigate(self):
        self.previous_page.tkraise()


class ChangePageButton(Button):
    def __init__(self, page: Frame, next_page: Frame, row_num:int, col_num:int, previous: bool = True):
        text = "Next"
        # x = 0.75
        if previous:
            text = "Previous"
            # x = 0.25
        super().__init__(page, text=text, compound=TOP,
                         width=15, command=lambda: self.navigate())
        self.grid(row=row_num, column=col_num)
        self.next_page = next_page

    def navigate(self):
        self.next_page.tkraise()        


class GridMouserPage(Frame):
    def __init__(self, parent: Tk, title: str, rows:int, cols:int, menu_page: Frame = None):
        super().__init__(parent)
        self.title = title

        canvas = Canvas(self, width=600, height=600)
        canvas.grid(row=rows, column=cols, sticky='NESW')
        canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        titleLabel = canvas.create_text(300, 13, anchor="n")
        canvas.itemconfig(titleLabel, text=title, font=("Arial", 18))

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



