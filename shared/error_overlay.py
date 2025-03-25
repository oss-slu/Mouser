from customtkinter import *

# Function to gradually change border thickness for the fading effect (with red color)
# this is currently not utilised anywhere
def fading_border_effect(frame):
    def fade_in_out(step):
        # Get current thickness
        current_thickness = frame.cget('border_width')

        # Gradually adjust the border thickness
        if step < 13:  # Gradually increase thickness
            new_thickness = current_thickness + 2
        elif step >= 13 and step < 26:  # Gradually decrease thickness
            new_thickness = current_thickness - 2
        else:
            frame.lower()
            return  # Stop the effect after the transition is complete

        # Apply new border thickness and set color to red
        frame.configure(border_color='red', border_width=new_thickness)

        # Call the fade_in_out function again after 100ms, slow down the effect
        frame.after(100, fade_in_out, step + 1)  # Update the step count

    # Start the effect with an initial step value of 0
    fade_in_out(0)
    frame.lift()