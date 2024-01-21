from tkinter  import *
from tkinter.ttk import *
from abc import ABC, abstractmethod
from PIL import Image, ImageTk

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
        self.place(relx=0.15, rely=0.15, anchor=CENTER)
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
    def __init__(self, parent: Tk, title: str, is_main_page: bool = True, menu_page: Frame = None):
        super().__init__(parent)
        self.title = title
        self.is_main_page = is_main_page
        self.canvas = Canvas(self, width=800, height=800)
        self.canvas.grid(row=0, column=0, columnspan= 5)
        self.rectangle = self.canvas.create_rectangle(0, 0, 600, 50, fill='#0097A7')
        self.title_label = self.canvas.create_text(300, 13, anchor="n")
        self.canvas.itemconfig(self.title_label, text=title, font=("Arial", 18))
       
        if self.is_main_page:
            self.display_welcome_elements()
            
        self.grid(row=0, column=0, sticky="NESW")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.grid_rowconfigure(0, weight=1)
        self.canvas.grid_columnconfigure(0, weight=1)
        
        #self.menu_button = MenuButton(self, menu_page) if menu_page else None
        self.next_button = None
        self.previous_button = None

        self.check_window_size()
        

    def raise_frame(self):
        self.tkraise()

    def display_welcome_elements(self):
        # Add a welcome message
        if self.is_main_page:
            self.welcome_label = Label(self.canvas, text="Welcome to Mouser!", font=("Arial", 16))
            self.canvas.create_window(300, 55, anchor="n", window=self.welcome_label)
            self.welcome_label.place()
        
        # Add an image
        image_path = "images/mouse_small.png"  # Change this to the path of your image file
        self.img = Image.open(image_path)
        self.img = self.img.resize((50,50))
        self.img = ImageTk.PhotoImage(self.img)
        self.image_label = Label(self.canvas, image=self.img)
        self.image_label.image = self.img
        self.canvas.create_window(550, 0, anchor="n", window=self.image_label)
        self.image_label.place()
        #Add minor instructions
        #self.instructions_label = Label(self.canvas, text="To create/open experiments, use the 'File' menu.",
         #                               font=("Arial", 12))
        #self.canvas.create_window(100,140, anchor="n", window=self.instructions_label)

    def hide_welcome_elements(self):
        if hasattr(self, 'welcome_label'):
            self.welcome_label.grid_forget()

        if hasattr(self, 'image_label'):
            self.image_label.grid_forget()

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

        x0, y0, x1, y2 = self.canvas.coords(self.rectangle)
        x3, y3 = self.canvas.coords(self.title_label)
        self.canvas.coords(self.rectangle, x0, y0, root_width, y2)
        self.canvas.coords(self.title_label, (root_width/2), y3)


class ChangeableFrame(ABC, Frame):

    @abstractmethod
    def update_frame(self):
        pass


if __name__ == '__main__':
    root = Tk()
    root.title("Template Test")
    root.geometry('600x600')

    main_frame = MouserPage(root, "Main", is_main_page)
    
    frame = MouserPage(root, "Template")

    main_frame.set_next_button(frame)
    frame.set_previous_button(main_frame)

    main_frame.raise_frame()

    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    root.mainloop()