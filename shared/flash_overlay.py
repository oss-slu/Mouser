from customtkinter import *

class FlashOverlay:
    '''A reusable flash overlay that can be used to show temporary full-screen messages'''

    def __init__(self, parent: CTk, message: str, duration: int = 1000,
                 bg_color: str = "#00FF00", text_color: str = "white",
                 font: tuple = ("Arial", 32, "bold")):

        self.parent = parent
        self.duration = duration

        # Create flash overlay frame
        self.flash_frame = CTkFrame(parent, fg_color=bg_color)
        self.flash_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Add message
        self.label = CTkLabel(
            self.flash_frame,
            text=message,
            font=font,
            text_color=text_color
        )
        self.label.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Schedule the fade out
        self.parent.after(self.duration, self._fade_out)

    def _fade_out(self):
        '''Removes the flash overlay'''
        if self.flash_frame.winfo_exists():
            self.flash_frame.destroy()

    def destroy(self):
        '''Manually destroy the overlay before the duration'''
        if self.flash_frame.winfo_exists():
            self.flash_frame.destroy()