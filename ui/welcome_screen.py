"""
Creates the welcome screen layout including logo and main navigation buttons.
Sets up the initial frame (ExperimentsUI) and populates it with:
- 'New Experiment' button
- 'Open Experiment' button
- 'Test Serials' button

Each button callback uses lambda to pass necessary context (root, frame).
Modularized from main.py for clarity and separation of UI layout.
"""

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage
from PIL import Image
from shared.tk_models import get_resource_path
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from ui.commands import create_file, open_file, open_test


def setup_welcome_screen(root, main_frame):
    experiments_frame = ExperimentsUI(root, main_frame)

    mouse_image = CTkImage(
        light_image=Image.open(get_resource_path("shared/images/MouseLogo.png")),
        size=(850, 275)
    )
    mouse_label = CTkLabel(experiments_frame, image=mouse_image)
    mouse_label.grid(row=1, column=0, pady=(20, 10))

    welcome_frame = CTkFrame(experiments_frame)
    welcome_frame.place(relx=0.5, rely=0.50, anchor="center")

    image_label = CTkLabel(welcome_frame, image=mouse_image, text="")
    image_label.pack(pady=(20, 10))

    height = main_frame.winfo_screenheight() / 6
    width = main_frame.winfo_screenwidth() * 0.9

    CTkButton(
        welcome_frame,
        text="New Experiment",
        font=("Georgia", 80),
        command=lambda: create_file(root, experiments_frame),
        width=width,
        height=height
    ).pack(pady=(10, 5), padx=20, fill='x', expand=True)

    CTkButton(
        welcome_frame,
        text="Open Experiment",
        font=("Georgia", 80),
        command=lambda: open_file(root, experiments_frame),
        width=width,
        height=height
    ).pack(pady=(5, 10), padx=20, fill='x', expand=True)

    CTkButton(
        welcome_frame,
        text="Test Serials",
        font=("Georgia", 80),
        command=lambda: open_test(root),
        width=width,
        height=height
    ).pack(pady=(5, 10), padx=20, fill='x', expand=True)

    return experiments_frame
