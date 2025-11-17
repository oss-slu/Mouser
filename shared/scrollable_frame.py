'''Scrollable frames for Mouser'''
from tkinter.ttk import Widget

from customtkinter import *


class ScrolledFrame:
    '''A frome with horizontal and verticel scrollbars.'''
    def __init__(self, master):
        self.outer_frame = CTkFrame(master)

        self.vert_scrollbar = CTkScrollbar(self.outer_frame, orientation=VERTICAL)
        self.horz_scrollbar = CTkScrollbar(self.outer_frame, orientation=HORIZONTAL)

        self.vert_scrollbar.pack(fill=Y, side=RIGHT)
        self.horz_scrollbar.pack(fill=X, side=BOTTOM)

        self.canvas = CTkCanvas(self.outer_frame, highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vert_scrollbar.set
        self.canvas['xscrollcommand'] = self.horz_scrollbar.set

        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vert_scrollbar['command'] = self.canvas.yview
        self.horz_scrollbar['command'] = self.canvas.xview

        self.inner = CTkFrame(self.canvas)

        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(Widget))


    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer_frame, item)
        # all other attributes (_w, children, etc) are passed to self.inner
        return getattr(self.inner, item)

    def _on_frame_configure(self, _=None):
        _, _, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        width = self.canvas.winfo_width()
        self.canvas.config(scrollregion = (0,0, max(x2, width), max(y2, height)))

    def _bind_mouse(self, _=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, _=None):
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units" )
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units" )

    def __str__(self):
        return str(self.outer_frame)
