from tkinter import *
from tkinter.ttk import *
from scroll_tkmodels_test import *

from login import LoginFrame
from accounts import AccountsFrame
from experiment_pages.select_experiment_ui import ExperimentsUI


from scroll_canvas import ScrollCanvas


class MouserWindow():
    def __init__(self):

        self.root = Tk()
        self.root.title("Mouser")
        self.root.geometry('600x600')
        self.root.resizable(False, False)

        self.canvas = ScrollCanvas(self.root, 'testing')
        self.scroll_frame = Frame(self.canvas)
        self.scrollbar = Scrollbar(self.canvas, orient=VERTICAL, command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=TOP, fill=BOTH, expand=1)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.canvas_frame = self.canvas.create_window((300,50), window=self.scroll_frame, anchor="n")

        main_frame = MouserPage(self.scroll_frame, self.canvas, "Mouser")
        login_frame = LoginFrame(self.scroll_frame, self.canvas, main_frame)
        accounts_frame = AccountsFrame(self.scroll_frame, main_frame)
        experiments_frame = ExperimentsUI(self.scroll_frame, self.canvas, main_frame)

        mouse_image = PhotoImage(file="./images/flask.png")
        user_image = PhotoImage(file="./images/user_small.png")

        create_nav_button(main_frame, "Experiments", mouse_image, experiments_frame, 0.5, 0.33)
        create_nav_button(main_frame, "Accounts", user_image, accounts_frame, 0.5, 0.67)

        raise_frame(login_frame)

        self.root.bind("<Configure>", self.canvas.on_frame_configure)
        self.root.bind_all("<MouseWheel>", self.mouse_scroll)


    def mouse_scroll(self, event):
            if event.delta:
                self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            else:
                if event.num == 5:
                    move = 1
                else:
                    move = -1

                self.canvas.yview_scroll(move, "units")


    def open_window(self):
        self.root.mainloop()


if __name__ =='__main__':
    root = MouserWindow()
    root.open_window()

