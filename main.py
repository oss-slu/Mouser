'''Main functionality of Program.'''
import tempfile
from tkinter.filedialog import *
from customtkinter import *
from CTkMenuBar import *
from CTkMessagebox import CTkMessagebox
from shared.tk_models import *
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from shared.password_utils import PasswordManager


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
                        os.remove(temp_file_path)

                    with open(temp_file_path, "wb") as temp_file:
                        print(3.5)
                        #print(decrypted_data)
                        temp_file.write(decrypted_data) # error here
                        print(3.75)
                        temp_file.seek(0)
                        print(3.99)
                        page = ExperimentMenuUI(root, temp_file.name, experiments_frame)
                        print(1)
                        page.raise_frame()
                        print(4)
                    password_prompt.destroy()
                    print(5)

                except Exception as e:# pylint: disable= broad-exception-caught
                    print(e)
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
    '''Command for the 'New' option in the menue bar.
    
    Navigates to the NewExperimentUI page.'''
    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()

root = CTk()
root.title("Mouser")
root.geometry('900x600')
root.minsize(900,600)

# Adds menu bar to root and binds the function to file_menu
menu_bar = CTkMenuBar(root)
file_menu = menu_bar.add_cascade("File")
file_dropdown = CustomDropdownMenu(widget=file_menu)
file_dropdown.add_option(option="New", command = create_file)
file_dropdown.add_option(option="Open", command = open_file)

root.config(menu=menu_bar)

main_frame = MouserPage(root, "Mouser")

experiments_frame = ExperimentsUI(root, main_frame)

raise_frame(experiments_frame)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()
