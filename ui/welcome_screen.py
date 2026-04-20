"""
Modernized, responsive welcome screen (light, card-based).

- Brand header (logo + title + subtitle)
- 2x2 colorful action cards with hover affordance
- Menu bar shown on all pages
- Functionality unchanged (callbacks preserved)
"""

import platform

from customtkinter import CTkFrame, CTkLabel, CTkImage, CTkButton
from PIL import Image

from experiment_pages.experiment.select_experiment_ui import ExperimentsUI
from shared.tk_models import get_resource_path
from ui.commands import create_file, open_file, open_test, open_serial_port_setting


# Unicode escapes ensure icons render regardless of file encoding.
ICON_NEW = "\U0001F9EA"  # 🧪
ICON_OPEN = "\U0001F4C4"  # 📄
ICON_EQUIP = "\U0001F512"  # 🔒
ICON_SERIAL = "\U0001F50C"  # 🔌
ICON_ARROW = "\u276F"  # ❯


def _contain_size(src_width, src_height, max_width, max_height):
    if src_width <= 0 or src_height <= 0 or max_width <= 0 or max_height <= 0:
        return 1, 1

    scale = min(max_width / src_width, max_height / src_height, 1.0)
    return max(1, int(src_width * scale)), max(1, int(src_height * scale))


def _emoji_font_family():
    system = platform.system()
    if system == "Windows":
        return "Segoe UI Emoji"
    if system == "Darwin":
        return "Apple Color Emoji"
    return "Noto Color Emoji"


def _metrics():
    system = platform.system()
    if system == "Darwin":
        return {
            "title": 44,
            "subtitle": 14,
            "card_title": 18,
            "card_desc": 13,
            "badge_icon": 20,
            "arrow": 15,
            "padx": 60,
            "card_w": 390,
            "card_h": 210,
            "card_gap": 16,
        }
    if system == "Windows":
        return {
            "title": 42,
            "subtitle": 13,
            "card_title": 17,
            "card_desc": 12,
            "badge_icon": 19,
            "arrow": 14,
            "padx": 52,
            "card_w": 370,
            "card_h": 200,
            "card_gap": 14,
        }
    return {
        "title": 36,
        "subtitle": 12,
        "card_title": 16,
        "card_desc": 12,
        "badge_icon": 18,
        "arrow": 13,
        "padx": 44,
        "card_w": 340,
        "card_h": 185,
        "card_gap": 12,
    }


def _hide_menu_bar(root):
    existing_menu = getattr(root, "_mouser_menu_bar", None)
    if existing_menu is not None:
        try:
            existing_menu.destroy()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        try:
            root.config(menu="")
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        try:
            delattr(root, "_mouser_menu_bar")
        except Exception:  # pylint: disable=broad-exception-caught
            pass


def _make_action_card(
    parent,
    *,
    icon,
    title,
    description,
    card_bg,
    card_hover_bg,
    border_color,
    border_hover_color,
    accent_solid,
    command,
):
    m = _metrics()

    accent_darker = {
        "#4f46e5": "#4338ca",
        "#16a34a": "#15803d",
        "#d97706": "#b45309",
        "#7c3aed": "#6d28d9",
    }.get(accent_solid, accent_solid)

    card = CTkFrame(
        parent,
        fg_color=card_bg,
        corner_radius=26,
        border_width=2,
        border_color=border_color,
        width=m["card_w"],
        height=m["card_h"],
    )
    card.grid_propagate(False)
    card.grid_rowconfigure(0, weight=1)
    card.grid_columnconfigure(0, weight=1)

    inner = CTkFrame(card, fg_color="transparent")
    inner.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
    inner.grid_columnconfigure(0, weight=1)
    inner.grid_rowconfigure(0, weight=0)
    inner.grid_rowconfigure(1, weight=0)
    inner.grid_rowconfigure(2, weight=1)
    inner.grid_rowconfigure(3, weight=0)

    badge = CTkFrame(inner, fg_color=accent_solid, corner_radius=14, width=46, height=46)
    badge.grid(row=0, column=0, pady=(0, 12))
    badge.grid_propagate(False)
    CTkLabel(
        badge,
        text=icon,
        font=(_emoji_font_family(), m["badge_icon"]),
        text_color="#ffffff",
    ).place(relx=0.5, rely=0.5, anchor="center")

    title_label = CTkLabel(
        inner,
        text=title,
        font=("Segoe UI Black", m["card_title"]),
        text_color="#0f172a",
        anchor="center",
        justify="center",
    )
    title_label.grid(row=1, column=0, sticky="ew", pady=(0, 8))

    desc_label = CTkLabel(
        inner,
        text=description,
        font=("Segoe UI", m["card_desc"]),
        text_color=accent_solid,
        anchor="center",
        justify="center",
        wraplength=m["card_w"] - 90,
    )
    desc_label.grid(row=2, column=0, sticky="ew")

    arrow_button = CTkButton(
        inner,
        text=ICON_ARROW,
        width=36,
        height=36,
        corner_radius=18,
        fg_color=accent_solid,
        hover_color=accent_darker,
        text_color="#ffffff",
        font=("Segoe UI Semibold", m["arrow"] + 2),
        border_width=1,
        border_color="#ffffff",
        command=command,
    )
    arrow_button.grid(row=3, column=0, pady=(14, 0))

    def set_hover(is_hover):
        card.configure(
            fg_color=card_hover_bg if is_hover else card_bg,
            border_color=border_hover_color if is_hover else border_color,
        )

    def on_click(_event=None):
        command()

    def is_pointer_inside_card():
        try:
            widget = card.winfo_containing(card.winfo_pointerx(), card.winfo_pointery())
        except Exception:  # pylint: disable=broad-exception-caught
            return False

        while widget is not None:
            if widget == card:
                return True
            widget = getattr(widget, "master", None)
        return False

    def on_enter(_event=None):
        set_hover(True)

    def on_leave(_event=None):
        card.after(10, lambda: set_hover(is_pointer_inside_card()))

    for widget in (card, inner, badge, title_label, desc_label, arrow_button):
        widget.bind("<Button-1>", on_click)
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        try:
            widget.configure(cursor="hand2")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    return card


def setup_welcome_screen(root, main_frame):
    """Builds a responsive welcome screen (functionality unchanged)."""
    experiments_frame = ExperimentsUI(root, main_frame)
    experiments_frame.configure(fg_color="#f7f8ff")

    m = _metrics()

    # MouserPage includes a legacy canvas in row=0/col=0 that resizes to the full
    # window height; keep all content in that same cell as an overlay.
    # Solid base background for the entire welcome screen (covers the full page).
    content = CTkFrame(experiments_frame, fg_color="#ccd7e8", corner_radius=0)
    content.grid(row=0, column=0, sticky="nsew")
    content.grid_rowconfigure(0, weight=0, minsize=255)  # header
    content.grid_rowconfigure(1, weight=1, minsize=(m["card_h"] * 2) + 120)  # cards
    content.grid_rowconfigure(2, weight=0, minsize=24)  # footer
    content.grid_columnconfigure(0, weight=1)

    # Soft background accents (subtle "blobs") behind the content.
    bg_blob_1 = CTkFrame(content, fg_color="#e0e7ff", corner_radius=220)
    bg_blob_1.place(relx=-0.10, rely=-0.10, relwidth=0.62, relheight=0.55)
    bg_blob_2 = CTkFrame(content, fg_color="#dcfce7", corner_radius=220)
    bg_blob_2.place(relx=0.55, rely=0.45, relwidth=0.60, relheight=0.60)
    bg_blob_3 = CTkFrame(content, fg_color="#fff7ed", corner_radius=220)
    bg_blob_3.place(relx=0.20, rely=0.70, relwidth=0.45, relheight=0.40)
    try:
        bg_blob_1.lower()
        bg_blob_2.lower()
        bg_blob_3.lower()
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    header = CTkFrame(content, fg_color="transparent")
    header.grid(row=0, column=0, padx=20, pady=(4, 0), sticky="n")

    logo_path = get_resource_path("shared/images/MouseLogo.png")
    with Image.open(logo_path) as logo_pil:
        logo_pil = logo_pil.convert("RGBA")

    logo_w, logo_h = _contain_size(logo_pil.width, logo_pil.height, max_width=150, max_height=150)
    logo_image = CTkImage(light_image=logo_pil, dark_image=logo_pil, size=(logo_w, logo_h))

    logo_badge = CTkFrame(header, fg_color="#4f46e5", corner_radius=24, width=160, height=160)
    logo_badge.pack(pady=(0, 12))
    logo_badge.pack_propagate(False)
    CTkLabel(logo_badge, image=logo_image, text="", fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")

    CTkLabel(header, text="MOUSER", font=("Segoe UI Black", m["title"]), text_color="#0f172a").pack()
    CTkLabel(
        header,
        text="LAB MANAGEMENT SYSTEM",
        font=("Segoe UI Semibold", m["subtitle"]),
        text_color="#6366f1",
    ).pack(pady=(4, 10))

    cards_area = CTkFrame(content, fg_color="transparent")
    cards_area.grid(row=1, column=0, padx=m["padx"], pady=(0, 2), sticky="nsew")
    cards_area.grid_rowconfigure(0, weight=1)
    cards_area.grid_columnconfigure(0, weight=1)

    cards = CTkFrame(cards_area, fg_color="transparent", width=(m["card_w"] * 2) + m["card_gap"], height=(m["card_h"] * 2) + m["card_gap"])
    cards.place(relx=0.5, rely=0.0, anchor="n")
    cards.grid_propagate(False)
    cards.grid_columnconfigure(0, weight=0, minsize=m["card_w"])
    cards.grid_columnconfigure(1, weight=0, minsize=m["card_w"])
    cards.grid_rowconfigure(0, weight=0, minsize=m["card_h"])
    cards.grid_rowconfigure(1, weight=0, minsize=m["card_h"])

    _make_action_card(
        cards,
        icon=ICON_NEW,
        title="New Experiment",
        description="Create and configure a new experiment.",
        card_bg="#eef2ff",
        card_hover_bg="#e0e7ff",
        border_color="#c7d2fe",
        border_hover_color="#4f46e5",
        accent_solid="#4f46e5",
        command=lambda: create_file(root, experiments_frame),
    ).grid(row=0, column=0, padx=(0, m["card_gap"]), pady=(0, m["card_gap"]), sticky="nsew")

    _make_action_card(
        cards,
        icon=ICON_OPEN,
        title="Open Experiment",
        description="Open an existing experiment file.",
        card_bg="#ecfdf5",
        card_hover_bg="#dcfce7",
        border_color="#bbf7d0",
        border_hover_color="#16a34a",
        accent_solid="#16a34a",
        command=lambda: open_file(root, experiments_frame),
    ).grid(row=0, column=1, padx=(0, 0), pady=(0, m["card_gap"]), sticky="nsew")

    _make_action_card(
        cards,
        icon=ICON_EQUIP,
        title="Equipment Testing",
        description="Validate connected equipment and readiness.",
        card_bg="#fffbeb",
        card_hover_bg="#fef3c7",
        border_color="#fde68a",
        border_hover_color="#d97706",
        accent_solid="#d97706",
        command=lambda: open_test(root),
    ).grid(row=1, column=0, padx=(0, m["card_gap"]), pady=(0, 0), sticky="nsew")

    def open_serial_settings():
        controller = getattr(root, "rfid_serial_port_controller", None)
        open_serial_port_setting(controller)

    _make_action_card(
        cards,
        icon=ICON_SERIAL,
        title="Serial Port Testing",
        description="Configure and verify serial port connections.",
        card_bg="#f5f3ff",
        card_hover_bg="#ede9fe",
        border_color="#ddd6fe",
        border_hover_color="#7c3aed",
        accent_solid="#7c3aed",
        command=open_serial_settings,
    ).grid(row=1, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")

    CTkLabel(
        content,
        text="v2.0 \u00b7 Mouser Lab Suite",
        font=("Segoe UI", m["card_desc"]),
        text_color="#94a3b8",
    ).grid(row=2, column=0, pady=(0, 4))

    try:
        experiments_frame.canvas.lower()
        content.lift()
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    return experiments_frame
