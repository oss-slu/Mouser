from customtkinter import CTkLabel, CTkToplevel

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.mouse_inside = False

        # Bind events to track entry/exit
        widget.bind("<Enter>", self.on_enter_widget)
        widget.bind("<Leave>", self.on_leave_widget)

    def on_enter_widget(self, event=None):
        self.mouse_inside = True
        self.show_tip()

    def on_leave_widget(self, event=None):
        self.mouse_inside = False
        self.widget.after(100, self.check_mouse)

    def on_enter_tip(self, event=None):
        self.mouse_inside = True

    def on_leave_tip(self, event=None):
        self.mouse_inside = False
        self.widget.after(100, self.check_mouse)

    def check_mouse(self):
        if not self.mouse_inside:
            self.hide_tip()

    def show_tip(self):
        if self.tip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 20

        self.tip_window = tw = CTkToplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = CTkLabel(
            tw,
            text=self.text,
            justify="left",
            bg_color="lightyellow",
            text_color="black",
            corner_radius=4,
            padx=6,
            pady=3
        )
        label.pack()

        # Bind tooltip events
        tw.bind("<Enter>", self.on_enter_tip)
        tw.bind("<Leave>", self.on_leave_tip)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None