from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import *
from tkinter.messagebox import showerror
from login import LoginFrame
from tk_models import *
from experiment_pages.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.new_experiment_ui import NewExperimentUI
from experiment_pages.select_experiment_ui import ExperimentsUI
from io import StringIO
from experiment_pages.password_utils import PasswordManager
import tempfile
import os

# Command for 'Open' option in menu bar
def open_file():
    file_path = askopenfilename(filetypes=[("Database files","*.mouser")])
    if file_path:
        if "Protected" in file_path:
            password_prompt = Toplevel(root)
            password_prompt.title("Enter Password")
            password_prompt.geometry("300x100")

            password_label = Label(password_prompt, text="Enter password:")
            password_label.pack(pady=10)

            password_entry = Entry(password_prompt, show="*")
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
                        temp_file.write(decrypted_data)
                        temp_file.seek(0)
                        page = ExperimentMenuUI(root, temp_file.name, experiments_frame)
                        page.tkraise()
                    password_prompt.destroy()
                except Exception as e:
                    showerror("Error", "Incorrect password")

            password_button = Button(password_prompt, text="OK", command=handle_password)
            password_button.pack()
        else:
            page = ExperimentMenuUI(root, file_path, experiments_frame)
            page.tkraise()

# Command for 'New' option in menu bar
def create_file():
    page = NewExperimentUI(root, experiments_frame)
    page.raise_frame()

root = Tk()
root.title("Mouser")
root.geometry('600x600')
root.minsize(600,600)

# Adds menu bar to root and binds the function to file_menu
menu_bar = Menu(root)
file_menu = Menu(menu_bar, tearoff= 0)
file_menu.add_command(label = "New", command = create_file)
file_menu.add_command(label = "Open", command = open_file)
menu_bar.add_cascade(label = "File", menu=file_menu)
root.config(menu=menu_bar)

main_frame = MouserPage(root, "Mouser")
login_frame = LoginFrame(root, main_frame)

experiments_frame = ExperimentsUI(root, main_frame)

raise_frame(experiments_frame)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()


