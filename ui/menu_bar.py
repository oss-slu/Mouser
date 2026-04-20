"""
Builds the application menu bar using CTkMenuBar.

Required structure (applied across all UI pages):
- File: New Experiment, Open Experiment
- Info: User Manual (opens local HTML manual)
"""

from CTkMenuBar import CTkMenuBar, CustomDropdownMenu

from ui.commands import create_file, open_file, open_documentation_popup


def _get_widget_bg(widget):
    try:
        return widget.cget("fg_color")
    except Exception:  # pylint: disable=broad-exception-caught
        return None


def _guess_page_background(page_frame):
    """Best-effort guess of the visible page background color.

    Many pages (e.g. welcome screen) draw a full-size child frame on top of the
    base page. In those cases, syncing to the child looks more natural than
    syncing to the base page frame color.
    """
    # Prefer a full-bleed child frame placed in the main grid cell.
    try:
        for child in page_frame.winfo_children():
            try:
                if child.winfo_manager() != "grid":
                    continue
                grid = child.grid_info()
                if int(grid.get("row", -1)) != 0 or int(grid.get("column", -1)) != 0:
                    continue
                sticky = str(grid.get("sticky", "")).lower()
                if not all(x in sticky for x in ("n", "s", "e", "w")):
                    continue
                bg = _get_widget_bg(child)
                if bg not in (None, "", "transparent"):
                    return bg
            except Exception:  # pylint: disable=broad-exception-caught
                continue
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    return _get_widget_bg(page_frame)


def sync_menu_background(root, page_frame):
    """Sync the window/menu background to the currently visible page.

    CTkMenuBar is attached to the root window, so the simplest way to make the
    menubar "match" each page is to set the root's background to the page's
    fg_color and keep the menu bar itself transparent.
    """
    menu_bar = getattr(root, "_mouser_menu_bar", None)
    if menu_bar is None:
        return

    bg = _guess_page_background(page_frame)
    if bg in (None, ""):
        return

    if isinstance(bg, (tuple, list)) and len(bg) >= 2:
        try:
            from customtkinter import get_appearance_mode  # pylint: disable=import-outside-toplevel

            bg = bg[1] if get_appearance_mode().lower() == "dark" else bg[0]
        except Exception:  # pylint: disable=broad-exception-caught
            bg = bg[0]

    try:
        root.configure(fg_color=bg)
    except Exception:  # pylint: disable=broad-exception-caught
        pass

    try:
        menu_bar.configure(bg_color=bg)
    except Exception:  # pylint: disable=broad-exception-caught
        pass


def build_menu(root, experiments_frame):
    """Constructs the main menu bar and attaches it to the root window."""
    existing_menu = getattr(root, "_mouser_menu_bar", None)
    if existing_menu is not None:
        try:
            existing_menu.destroy()
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        try:
            delattr(root, "_mouser_menu_bar")
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    menu_bar = CTkMenuBar(
        root,
        bg_color=_guess_page_background(experiments_frame) or "transparent",
        height=30,
        padx=8,
        pady=3,
    )

    file_menu = menu_bar.add_cascade(
        "File",
        fg_color=("#2563eb", "#1d4ed8"),
        hover_color=("#1d4ed8", "#2563eb"),
        text_color=("#ffffff", "#ffffff"),
        corner_radius=8,
    )
    file_dropdown = CustomDropdownMenu(
        widget=file_menu,
        bg_color=("#ffffff", "#0f172a"),
        fg_color=("#ffffff", "#0f172a"),
        border_color=("#cbd5e1", "#374151"),
        separator_color=("#e5e7eb", "#1f2937"),
        text_color=("#0f172a", "#f9fafb"),
        hover_color=("#e2e8f0", "#1f2937"),
    )
    file_dropdown.add_option("New Experiment", lambda: create_file(root, experiments_frame))
    file_dropdown.add_option("Open Experiment", lambda: open_file(root, experiments_frame))

    info_menu = menu_bar.add_cascade(
        "Info",
        fg_color=("#7c3aed", "#6d28d9"),
        hover_color=("#6d28d9", "#7c3aed"),
        text_color=("#ffffff", "#ffffff"),
        corner_radius=8,
    )
    info_dropdown = CustomDropdownMenu(
        widget=info_menu,
        bg_color=("#ffffff", "#0f172a"),
        fg_color=("#ffffff", "#0f172a"),
        border_color=("#cbd5e1", "#374151"),
        separator_color=("#e5e7eb", "#1f2937"),
        text_color=("#0f172a", "#f9fafb"),
        hover_color=("#e2e8f0", "#1f2937"),
    )
    info_dropdown.add_option("User Manual", lambda: open_documentation_popup(root))

    root._mouser_menu_bar = menu_bar
    sync_menu_background(root, experiments_frame)
