"""
Modernized, responsive welcome screen.

- Clean two-section layout (logo + buttons)
- Fully responsive with grid weights and minimum size
- Compatible with all screen sizes on launch
"""

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage
from PIL import Image
from shared.tk_models import get_resource_path
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from ui.commands import create_file, open_file, open_test


def setup_welcome_screen(root, main_frame):
    """Builds a responsive, visually consistent welcome screen."""
    experiments_frame = ExperimentsUI(root, main_frame)
    experiments_frame.configure(fg_color="#f5f6fa")

    # --- Configure grid layout with minimum heights ---
    experiments_frame.grid_rowconfigure(0, weight=1, minsize=150)  # Logo
    experiments_frame.grid_rowconfigure(1, weight=2, minsize=300)  # Buttons
    experiments_frame.grid_rowconfigure(2, weight=1, minsize=80)   # Tagline
    experiments_frame.grid_columnconfigure(0, weight=1)

    # --- Logo section ---
    logo_path = get_resource_path("shared/images/MouseLogo.png")
    logo_image = CTkImage(Image.open(logo_path), size=(500, 150))

    logo_label = CTkLabel(
        experiments_frame,
        image=logo_image,
        text="",
        fg_color="transparent"
    )
    logo_label.grid(row=0, column=0, pady=(40, 10), sticky="n")

    # --- Button container ---
    welcome_card = CTkFrame(
        experiments_frame,
        fg_color="white",
        corner_radius=25,
        border_width=1,
        border_color="#d1d5db"
    )
    welcome_card.grid(row=1, column=0, padx=60, pady=20, sticky="nsew")
    welcome_card.grid_rowconfigure((0, 1, 2), weight=1)
    welcome_card.grid_columnconfigure(0, weight=1)

    # --- Unified button style ---
    button_style = {
        "corner_radius": 20,
        "font": ("Segoe UI Semibold", 26),
        "text_color": "white",
        "fg_color": "#2563eb",     # Modern blue
        "hover_color": "#1e40af",  # Slightly darker hover
        "height": 300
    }

    # --- Buttons (stay centered + expand if resized) ---
    CTkButton(welcome_card, text="New Experiment",
              command=lambda: create_file(root, experiments_frame),
              **button_style).grid(row=0, column=0, padx=80, pady=15, sticky="nsew")

    CTkButton(welcome_card, text="Open Experiment",
              command=lambda: open_file(root, experiments_frame),
              **button_style).grid(row=1, column=0, padx=80, pady=15, sticky="nsew")

    CTkButton(welcome_card, text="Test Serials",
              command=lambda: open_test(root),
              **button_style).grid(row=2, column=0, padx=80, pady=15, sticky="nsew")

    return experiments_frame
