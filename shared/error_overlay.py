from customtkinter import *


# command=lambda: fading_border_effect(welcome_frame)
# Function to gradually change border thickness for the fading effect (with red color)
# this is currently not utilised anywhere
def fading_border_effect(frame: CTk, color: str):
    def fade_in_out(step):
        # Get current thickness
        current_thickness = frame.cget('borderwidth')
        print(current_thickness)

        # Gradually adjust the border thickness
        if step < 13:  # Gradually increase thickness
            new_thickness = current_thickness + 2
        elif step >= 13 and step < 26:  # Gradually decrease thickness
            new_thickness = current_thickness - 2
        else:
            frame.configure(fg_color='gray')
            return  # Stop the effect after the transition is complete

        # Apply new border thickness and set color to red
        frame.configure(fg_color=color, borderwidth=new_thickness)

        # Call the fade_in_out function again after 100ms, slow down the effect
        frame.after(100, fade_in_out, step + 1)  # Update the step count

    # Start the effect with an initial step value of 0
    fade_in_out(0)