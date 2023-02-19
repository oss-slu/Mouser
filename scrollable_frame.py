import tkinter as tk


class ScrolledFrame:
    def __init__(self, master, **kwargs):
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        background = kwargs.pop('bg', kwargs.pop('background', None))

        self.outer_frame = tk.Frame(master, **kwargs)

        self.vert_scrollbar = tk.Scrollbar(self.outer_frame, orient=tk.VERTICAL)
        self.horz_scrollbar = tk.Scrollbar(self.outer_frame, orient=tk.HORIZONTAL)

        self.vert_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
        self.horz_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)

        self.canvas = tk.Canvas(self.outer_frame, highlightthickness=0, width=width, height=height, bg=background)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = self.vert_scrollbar.set
        self.canvas['xscrollcommand'] = self.horz_scrollbar.set
        
        self.canvas.bind("<Enter>", self._bind_mouse)
        self.canvas.bind("<Leave>", self._unbind_mouse)
        self.vert_scrollbar['command'] = self.canvas.yview
        self.horz_scrollbar['command'] = self.canvas.xview

        self.inner = tk.Frame(self.canvas, bg=background)
        
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind("<Configure>", self._on_frame_configure)

        self.outer_attr = set(dir(tk.Widget))

    def __getattr__(self, item):
        if item in self.outer_attr:
            # geometry attributes etc (eg pack, destroy, tkraise) are passed on to self.outer
            return getattr(self.outer_frame, item)
        else:
            # all other attributes (_w, children, etc) are passed to self.inner
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        x1, y1, x2, y2 = self.canvas.bbox("all")
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion = (0,0, x2, max(y2, height)))

    def _bind_mouse(self, event=None):
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event=None):
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

