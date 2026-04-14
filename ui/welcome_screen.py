"""
Modernized, responsive welcome screen.

- Clean two-section layout (logo + buttons)
- Fully responsive with grid weights and minimum size
- Compatible with all screen sizes on launch
"""

import platform

from customtkinter import CTkFrame, CTkLabel, CTkButton, CTkImage
from PIL import Image
from shared.tk_models import get_resource_path
from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from ui.commands import create_file, open_file, open_test


def _contain_size(src_width, src_height, max_width, max_height):
    if src_width <= 0 or src_height <= 0 or max_width <= 0 or max_height <= 0:
        return 1, 1

    scale = min(max_width / src_width, max_height / src_height, 1.0)
    return max(1, int(src_width * scale)), max(1, int(src_height * scale))


def setup_welcome_screen(root, main_frame):
    """Builds a responsive, visually consistent welcome screen."""
    experiments_frame = ExperimentsUI(root, main_frame)
    experiments_frame.configure(fg_color="#f5f6fa")

    # --- Configure grid layout with minimum heights ---
    experiments_frame.grid_rowconfigure(0, weight=1, minsize=260)  # Logo
    experiments_frame.grid_rowconfigure(1, weight=2, minsize=300)  # Buttons
    experiments_frame.grid_rowconfigure(2, weight=1, minsize=80)   # Tagline
    experiments_frame.grid_columnconfigure(0, weight=1)

    # --- Logo section ---
    logo_path = get_resource_path("shared/images/MouseLogo.png")
    with Image.open(logo_path) as logo_pil:
        logo_pil = logo_pil.convert("RGBA")

    logo_w, logo_h = _contain_size(logo_pil.width, logo_pil.height, max_width=560, max_height=220)
    logo_image = CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(logo_w, logo_h))

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
    current_os = platform.system()
    if current_os == "Darwin":
        button_font_size = 26
        button_height = 72
    elif current_os == "Windows":
        button_font_size = 22
        button_height = 62
    else:
        button_font_size = 20
        button_height = 58

    button_style = {
        "corner_radius": 20,
        "font": ("Segoe UI Semibold", button_font_size),
        "text_color": "white",
        "fg_color": "#2563eb",     # Modern blue
        "hover_color": "#1e40af",  # Slightly darker hover
        "height": button_height
    }

    # --- Buttons (stay centered + expand if resized) ---
    CTkButton(welcome_card, text="New Experiment",
              command=lambda: create_file(root, experiments_frame),
              **button_style).grid(row=0, column=0, padx=80, pady=12, sticky="ew")

    CTkButton(welcome_card, text="Open Experiment",
              command=lambda: open_file(root, experiments_frame),
              **button_style).grid(row=1, column=0, padx=80, pady=12, sticky="ew")

    CTkButton(welcome_card, text="Test Serials",
              command=lambda: open_test(root),
              **button_style).grid(row=2, column=0, padx=80, pady=12, sticky="ew")

    return experiments_frame
