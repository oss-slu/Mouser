import shutil
import tempfile
import os
from tkinter.filedialog import *
from customtkinter import *
from CTkMenuBar import *
from CTkMessagebox import CTkMessagebox
from shared.tk_models import *
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from shared.password_utils import PasswordManager
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from PIL import Image

def open_file(): 
    '''Command for 'Open' option in menu bar.

    Opens a .mouser file
    '''
    file_path = askopenfilename(filetypes=[("Database files","*.mouser")])
    if file_path:
        if "Protected" in file_path:
            password_prompt = CTkToplevel(root)
            password_prompt.title("Enter Password")
            password_prompt.geometry("300x100")

            password_label = CTkLabel(password_prompt, text="Enter password:")
            password_label.pack(pady=10)

            password_entry = CTkEntry(password_prompt, show="*")
            password_entry.pack(pady=5)

            def handle_password():
                password = password_entry.get()
                try:
                    manager = PasswordManager(password)
                    decrypted_data = manager.decrypt_file(file_path)
                    temp_folder_name = "Mouser"
                    temp_folder_path = os.path.join(tempfile.gettempdir(), temp_folder_name)
                    os.makedirs(temp_folder_path, exist_ok=True)
                    temp_file_name =  os.path.basename(file_path)
                    temp_file_path = os.path.join(temp_folder_path, temp_file_name)
                    if os.path.exists(temp_file_path):
                        page = ExperimentMenuUI(root, temp_file_name, experiments_frame)
                        page.raise_frame()
                    else:
                        with open(temp_file_path, "wb") as temp_file:
                            temp_file.write(decrypted_data)
                            temp_file.seek(0)
                            page = ExperimentMenuUI(root, temp_file.name, experiments_frame)
                            page.raise_frame()

                        password_prompt.destroy()

                except Exception as e:# pylint: disable= broad-exception-caught
                    CTkMessagebox(
                        message="Incorrect password",
                        title="Error",
                        icon="cancel"
                    )

            password_button = CTkButton(password_prompt, text="OK", command=handle_password)
            password_button.pack()
        else:
            page = ExperimentMenuUI(root, file_path, experiments_frame)
            page.raise_frame()

# Command for 'New' option in menu bar
def create_file():
    print("create_file is called")  # Debugging print statement
    try:
        page = NewExperimentUI(root, experiments_frame)
        page.raise_frame()
        print("NewExperimentUI should now be visible")  # Debugging print statement
    except Exception as e:
        print(f"Error in create_file: {e}")  # Print any error


temp_folder_name = "Mouser"
temp_folder_path = os.path.join(tempfile.gettempdir(), temp_folder_name)
if os.path.exists(temp_folder_path):
    shutil.rmtree(temp_folder_path)

root = CTk()
root.title("Mouser")
root.geometry('900x600')
root.minsize(900, 600)


# Adds menu bar to root and binds the function to file_menu
menu_bar = CTkMenuBar(root)
file_menu = menu_bar.add_cascade("File")
file_dropdown = CustomDropdownMenu(widget=file_menu)
file_dropdown.add_option(option="New", command=create_file)
file_dropdown.add_option(option="Open", command=open_file)

root.config(menu=menu_bar)
main_frame = MouserPage(root, "Mouser")
experiments_frame = ExperimentsUI(root, main_frame)
def on_mouse_button_click():
    print("on_mouse_button_click is called")  # Debugging print statement
    experiments_frame.raise_frame()


mouse_image = CTkImage(light_image=Image.open("./shared/images/MouserLogos.png"), size=(550, 200))
mouse_button = CTkButton(main_frame, image=mouse_image, command=on_mouse_button_click)
mouse_button.grid(row=1, column=0, pady=(20, 10))


# Update the command of mouse_button to use on_mouse_button_click
mouse_button.configure(command=on_mouse_button_click)


# Display mouse image button on main frame and set the command to on_mouse_button_click

create_nav_button(main_frame, "Welcome to Mouser! Please click the File Drop Down option in the top left to create or open a new Experiment.\n", mouse_image,experiments_frame, 0.5, 0.33)
raise_frame(main_frame)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
# Ensure the main_frame widget expands to fill the grid cell it's in, which helps with alignment.
main_frame.grid_rowconfigure(1, weight=1)  # Adjust '1' if other rows are used; make it expandable
main_frame.grid_columnconfigure(0, weight=1)  # Make the column containing the label expandable

root.mainloop()

