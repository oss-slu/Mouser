'''Flash Overlay module for displaying temporary messages.'''
import threading
from customtkinter import *

class FlashOverlay:
    '''A reusable flash overlay that can be used to show temporary full-screen messages'''
    def __init__(self, parent, message, duration=1000, bg_color="#00FF00", text_color="black"):
        self._lock = threading.Lock()
        self.parent = parent
        self.message = message
        self.duration = duration
        self.bg_color = bg_color
        self.text_color = text_color
        self.overlay = None
        self._create_overlay()

    def _create_overlay(self):
        '''Creates and displays the overlay message.'''
        with self._lock:
            # Create the overlay frame that covers the entire parent window
            self.overlay = CTkFrame(self.parent)
            self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)  # Cover entire parent

            # Create a semi-transparent background
            self.overlay.configure(fg_color=self.bg_color)

            # Create the message label
            label = CTkLabel(
                self.overlay,
                text=self.message,
                font=("Arial", 24, "bold"),
                text_color=self.text_color,
                corner_radius=10
            )
            label.place(relx=0.5, rely=0.5, anchor=CENTER)  # Center the message

            # Schedule the removal of the overlay
            self.parent.after(self.duration, self.remove)

    def remove(self):
        '''Removes the overlay from the screen.'''
        with self._lock:
            if self.overlay and self.overlay.winfo_exists():
                try:
                    self.overlay.destroy()
                except Exception as e:
                    print(f"Error removing overlay: {e}")
                finally:
                    self.overlay = None

    def update_message(self, new_message, new_duration=None):
        '''Updates the message and optionally the duration.'''
        with self._lock:
            if self.overlay and self.overlay.winfo_exists():
                # Update the message
                for widget in self.overlay.winfo_children():
                    if isinstance(widget, CTkLabel):
                        widget.configure(text=new_message)

                # Update duration if provided
                if new_duration is not None:
                    self.duration = new_duration
                    # Cancel existing removal and schedule new one
                    self.parent.after_cancel(self.overlay.after_id)
                    self.parent.after(self.duration, self.remove)

    def is_visible(self):
        '''Returns whether the overlay is currently visible.'''
        with self._lock:
            return self.overlay is not None and self.overlay.winfo_exists()

    def force_remove(self):
        '''Forces immediate removal of the overlay.'''
        self.remove()