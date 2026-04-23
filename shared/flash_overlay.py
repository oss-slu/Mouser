'''Custom Flash Screen to show statuses to the user'''
from customtkinter import *

class FlashOverlay:
    '''A reusable flash overlay that can be used to show temporary full-screen messages'''

    def __init__(self, parent: CTk, message: str, duration: int = 1000,
                 bg_color: str = "#00FF00", text_color: str = "white",
                 font: tuple = ("Arial", 32, "bold")):

        self.parent = parent
        self.duration = duration
        self._z_job = None

        # Suspend periodic nav-button lifting while overlay is visible.
        self._set_overlay_nav_lock(+1)

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
        try:
            self.flash_frame.lift()
            self.label.lift()
        except Exception:
            pass

        # Keep overlay above all page widgets (including nav buttons) for full duration.
        self._keep_on_top()

        # Schedule the fade out
        self.parent.after(self.duration, self._fade_out)

    def _set_overlay_nav_lock(self, delta: int):
        """Reference-count overlay visibility to coordinate with page nav lifting."""
        try:
            count = int(getattr(self.parent, "_active_flash_overlays", 0) or 0)
            count = max(0, count + int(delta))
            setattr(self.parent, "_active_flash_overlays", count)
            setattr(self.parent, "_nav_lift_suspended", bool(count > 0))
        except Exception:
            pass

    def _keep_on_top(self):
        """Continuously re-lift the overlay while active."""
        if not self.flash_frame.winfo_exists():
            return
        try:
            self.flash_frame.lift()
            self.label.lift()
        except Exception:
            pass
        try:
            self._z_job = self.parent.after(20, self._keep_on_top)
        except Exception:
            self._z_job = None

    def _fade_out(self):
        '''Removes the flash overlay'''
        if self.flash_frame.winfo_exists():
            self.flash_frame.destroy()
        if self._z_job is not None:
            try:
                self.parent.after_cancel(self._z_job)
            except Exception:
                pass
            self._z_job = None
        self._set_overlay_nav_lock(-1)

    def destroy(self):
        '''Manually destroy the overlay before the duration'''
        if self.flash_frame.winfo_exists():
            self.flash_frame.destroy()
        if self._z_job is not None:
            try:
                self.parent.after_cancel(self._z_job)
            except Exception:
                pass
            self._z_job = None
        self._set_overlay_nav_lock(-1)
