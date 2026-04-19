"""
Modernized Experiment Menu UI.

- Acts as central hub for navigation between experiment pages
- Updated with responsive layout, consistent font hierarchy, and button palette
- Inline comments explain UI design; all logic preserved
"""

import sqlite3
import os
import platform
from datetime import datetime
from tkinter import messagebox

from customtkinter import CTkFrame, CTkButton, CTkFont, CTkLabel
from shared.experiment import Experiment  # pylint: disable=import-error
from databases.experiment_database import (  # pylint: disable=import-error
    ExperimentDatabase,
)
from shared.tk_models import MouserPage  # pylint: disable=import-error


# Use Unicode escapes so icons render regardless of file encoding.
ICON_RFID = "\U0001F3F7\ufe0f"  # 🏷️
ICON_COLLECT = "\u270D\ufe0f"  # ✍️
ICON_ANALYZE = "\U0001F50E"  # 🔎
ICON_SUMMARY = "\U0001F4D1"  # 📑
ICON_INVEST = "\U0001F9D1\u200d\U0001F52C"  # 🧑‍🔬
ICON_GROUP = "\U0001F465"  # 👥
ICON_CAGE = "\U0001F3E0"  # 🏠
ICON_DELETE = "\U0001F5D1\ufe0f"  # 🗑️
ICON_NOTEBOOK = "\U0001F4D3"  # 📓
ICON_PENCIL = "\u270F\ufe0f"  # ✏️


def _emoji_font_family():
    system = platform.system()
    if system == "Windows":
        return "Segoe UI Emoji"
    if system == "Darwin":
        return "Apple Color Emoji"
    return "Noto Color Emoji"


class _MenuTile(CTkFrame):
    """Clickable tile with separate icon + title (font sizes independent)."""

    def __init__(
        self,
        parent,
        *,
        icon_text: str,
        title_text: str,
        width: int,
        height: int,
        bg_color: str,
        hover_color: str,
        border_color: str,
        icon_font_size: int,
        title_font,
        command,
        text_color: str = "#0f172a",
        muted_color: str = "#94a3b8",
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            fg_color=bg_color,
            corner_radius=20,
            border_width=2,
            border_color=border_color,
        )
        self.grid_propagate(False)
        self._command = command
        self._enabled = True
        self._bg = bg_color
        self._hover = hover_color
        self._border = border_color
        self._text = text_color
        self._muted = muted_color

        self.grid_rowconfigure(0, weight=2)
        self.grid_rowconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)

        self.icon_label = CTkLabel(
            self,
            text=icon_text,
            font=(_emoji_font_family(), icon_font_size),
            text_color=text_color,
        )
        self.icon_label.grid(row=0, column=0, pady=(12, 4))

        self.title_label = CTkLabel(
            self,
            text=title_text,
            font=title_font,
            text_color=text_color,
            justify="center",
        )
        self.title_label.grid(row=1, column=0, pady=(0, 12))

        for widget in (self, self.icon_label, self.title_label):
            widget.bind("<Button-1>", self._on_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _set_hover(self, hovering: bool):
        if not self._enabled:
            return
        self.configure(fg_color=self._hover if hovering else self._bg)

    def _is_inside_self(self):
        try:
            x, y = self.winfo_pointerxy()
            w = self.winfo_containing(x, y)
        except Exception:  # pylint: disable=broad-exception-caught
            return False

        while w is not None:
            if w == self:
                return True
            w = getattr(w, "master", None)
        return False

    def _on_enter(self, _event=None):  # pylint: disable=unused-argument
        self._set_hover(True)

    def _on_leave(self, _event=None):  # pylint: disable=unused-argument
        # Avoid flicker when moving between child widgets inside the tile.
        self.after(1, lambda: self._set_hover(self._is_inside_self()))

    def _on_click(self, _event=None):  # pylint: disable=unused-argument
        if not self._enabled:
            return
        if callable(self._command):
            self._command()

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)
        if self._enabled:
            self.configure(fg_color=self._bg, border_color=self._border)
            self.icon_label.configure(text_color=self._text)
            self.title_label.configure(text_color=self._text)
        else:
            self.configure(fg_color="#f1f5f9", border_color="#e2e8f0")
            self.icon_label.configure(text_color=self._muted)
            self.title_label.configure(text_color=self._muted)


class ExperimentMenuUI(MouserPage):
    """Provides navigation options for the selected experiment."""

    def _persist_temp_to_original_if_available(self):
        """Persist temp DB back to the original experiment file when the app uses temp copies.

        `ui.commands.open_file` opens a temporary copy/decrypted file. Without persisting,
        any notes saved into the temp DB would be lost when the experiment is reopened.
        """
        try:
            # Import lazily to avoid circular imports (ui.commands imports this module).
            from ui.commands import save_file  # pylint: disable=import-outside-toplevel

            save_file()
        except Exception:  # pylint: disable=broad-exception-caught
            # If we can't persist (e.g., tests or non-standard entry), keep local temp state only.
            pass

    def _ensure_notebook_table(self):
        try:
            self.experiment_db._c.execute(  # pylint: disable=protected-access
                "CREATE TABLE IF NOT EXISTS notebook (key TEXT PRIMARY KEY, value TEXT)"
            )
            self.experiment_db._conn.commit()  # pylint: disable=protected-access
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def _notebook_get(self, key: str, default: str = "") -> str:
        try:
            self.experiment_db._c.execute(  # pylint: disable=protected-access
                "SELECT value FROM notebook WHERE key = ?",
                (key,),
            )
            row = self.experiment_db._c.fetchone()  # pylint: disable=protected-access
            if row and row[0] is not None:
                return str(row[0])
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        return default

    def _notebook_set(self, key: str, value: str) -> None:
        try:
            self.experiment_db._c.execute(  # pylint: disable=protected-access
                "INSERT INTO notebook(key, value) VALUES(?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )
            self.experiment_db._conn.commit()  # pylint: disable=protected-access
        except sqlite3.OperationalError:
            # SQLite < 3.24 fallback (no upsert).
            try:
                self.experiment_db._c.execute(  # pylint: disable=protected-access
                    "DELETE FROM notebook WHERE key = ?",
                    (key,),
                )
                self.experiment_db._c.execute(  # pylint: disable=protected-access
                    "INSERT INTO notebook(key, value) VALUES(?, ?)",
                    (key, value),
                )
                self.experiment_db._conn.commit()  # pylint: disable=protected-access
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    @staticmethod
    def _menu_button_metrics():
        """Tune button size by OS to keep visual proportions consistent."""
        system = platform.system()
        if system == "Darwin":
            return {"font_size": 22, "height": 58, "width": 520}
        if system == "Windows":
            return {"font_size": 18, "height": 50, "width": 470}
        return {"font_size": 17, "height": 48, "width": 450}

    def __init__(self, root=None, file_path=None, menu_page=None, original_file_path=None, **kwargs):
        # Backward-compatible argument names used in some call sites/tests.
        if root is None:
            root = kwargs.get("parent")
        if file_path is None:
            file_path = kwargs.get("name") or kwargs.get("file_path")
        if menu_page is None:
            menu_page = kwargs.get("prev_page")
        if original_file_path is None:
            original_file_path = kwargs.get("full_path") or kwargs.get("original_path") or kwargs.get("original_file_path")

        super().__init__(root, "Experiment Menu", menu_page)

        palette = {
            "bg": ("#f1f5f9", "#0b1220"),
            "text_muted": ("#64748b", "#94a3b8"),
            "card_border": ("#e2e8f0", "#223044"),
            "card_bg": ("#ffffff", "#0b1220"),
            "accent_blue": "#3b82f6",
            "accent_violet": "#8b5cf6",
            "accent_teal": "#14b8a6",
            "accent_amber": "#f59e0b",
            "accent_green": "#22c55e",
            "danger": "#ef4444",
        }
        self.ui_palette = palette

        # Keep the legacy canvas from showing as a contrasting box behind the page.
        self.configure(fg_color=palette["bg"])

        if hasattr(self, "menu_button") and self.menu_button:
            def safe_nav():
                prev = getattr(self.menu_button, "previous_page", None)
                if prev is not None and hasattr(prev, "raise_frame"):
                    prev.raise_frame()
                else:
                    self.back_to_welcome()

            self.menu_button.configure(
                text="⬅",
                corner_radius=12,
                height=40,
                width=54,
                font=CTkFont("Segoe UI Semibold", 20),
                text_color="white",
                fg_color=palette["accent_amber"],
                hover_color="#d97706",
                command=safe_nav,
            )
            self.menu_button.place_configure(relx=0.0, rely=0.0, x=16, y=8, anchor="nw")

        self.root = root
        self.file_path = file_path
        self.original_file_path = original_file_path or file_path
        self.menu_page = menu_page
        self.experiment_db = ExperimentDatabase(self.file_path)
        self._ensure_notebook_table()

        body_root = CTkFrame(self, fg_color="transparent")
        body_root.place(relx=0.5, rely=0.0, y=70, anchor="n", relwidth=0.95, relheight=0.86)
        body_root.grid_columnconfigure(0, weight=1)
        body_root.grid_columnconfigure(1, weight=0, minsize=320)
        body_root.grid_rowconfigure(1, weight=1)

        title_font = CTkFont(family="Segoe UI Semibold", size=26)
        subtitle_font = CTkFont(family="Segoe UI", size=14)
        experiment_font = CTkFont(family="Segoe UI Semibold", size=18)

        header = CTkFrame(body_root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        header.grid_columnconfigure(0, weight=1)
        CTkLabel(header, text="Experiment Menu", font=title_font, text_color=("black", "white")).grid(
            row=0, column=0, sticky="w"
        )
        CTkLabel(
            header,
            text="Configure, collect, analyze, and review your experiment",
            font=subtitle_font,
            text_color=palette["text_muted"],
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        experiment_name = ""
        try:
            experiment_name = (self.experiment_db.get_experiment_name() or "").strip()
        except Exception:  # pylint: disable=broad-exception-caught
            experiment_name = ""

        # Experiment name is shown in the sidebar notebook; keep header compact.

        # Content area (no outer "rectangle box").
        content = CTkFrame(body_root, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content.grid_rowconfigure(0, weight=0)
        content.grid_rowconfigure(1, weight=1)
        content.grid_columnconfigure(0, weight=1)

        # Centered fixed-width grid so tiles don't stretch too wide.
        grid_area = CTkFrame(content, fg_color="transparent")
        grid_area.grid(row=0, column=0, sticky="n", pady=(0, 10))

        metrics = self._menu_button_metrics()
        button_font = CTkFont("Segoe UI Semibold", metrics["font_size"])

        system = platform.system()
        if system == "Darwin":
            tile_width = 320
            tile_height = 132
            primary_height = 74
            grid_gap = 18
        elif system == "Windows":
            tile_width = 290
            tile_height = 122
            primary_height = 66
            grid_gap = 16
        else:
            tile_width = 270
            tile_height = 118
            primary_height = 64
            grid_gap = 14

        tile_title_font = CTkFont("Segoe UI Semibold", metrics["font_size"])

        # Soft card colors + matching hover colors (aligned with new experiment pages).
        tile_colors = {
            "collect": {"bg": "#ecfdf5", "hover": "#dcfce7", "border": palette["accent_green"]},
            "analyze": {"bg": "#eff6ff", "hover": "#dbeafe", "border": palette["accent_blue"]},
            "summary": {"bg": "#f5f3ff", "hover": "#ede9fe", "border": palette["accent_violet"]},
            "invest": {"bg": "#ecfeff", "hover": "#cffafe", "border": palette["accent_teal"]},
            "group": {"bg": "#fdf2f8", "hover": "#fce7f3", "border": "#ec4899"},
            "cage": {"bg": "#fffbeb", "hover": "#fef3c7", "border": palette["accent_amber"]},
        }

        icon_font_size = 34 if system == "Windows" else 36

        self.rfid_button = CTkButton(
            grid_area,
            text=f"{ICON_RFID}  Map RFID",
            command=self.open_map_rfid,
            corner_radius=22,
            width=(tile_width * 3) + (grid_gap * 2),
            height=primary_height,
            font=CTkFont("Segoe UI Semibold", metrics["font_size"] + 2),
            text_color=("white", "white"),
            fg_color=palette["accent_blue"],
            hover_color="#2563eb",
        )
        self.rfid_button.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(20, 26))

        # Cache label strings so disable_buttons_if_needed can restore them exactly.
        # Icon on first line, title on the next line(s).
        self._collection_label = "Data\nCollection"
        self._analysis_label = "Data\nAnalysis"

        c = tile_colors["collect"]
        self.collection_tile = _MenuTile(
            grid_area,
            icon_text=ICON_COLLECT,
            title_text=self._collection_label,
            width=tile_width,
            height=tile_height,
            bg_color=c["bg"],
            hover_color=c["hover"],
            border_color=c["border"],
            icon_font_size=icon_font_size,
            title_font=tile_title_font,
            command=self.open_data_collection,
        )
        self.collection_tile.grid(row=1, column=0, sticky="nsew", padx=(0, grid_gap), pady=(0, 14))

        c = tile_colors["analyze"]
        self.analysis_tile = _MenuTile(
            grid_area,
            icon_text=ICON_ANALYZE,
            title_text=self._analysis_label,
            width=tile_width,
            height=tile_height,
            bg_color=c["bg"],
            hover_color=c["hover"],
            border_color=c["border"],
            icon_font_size=icon_font_size,
            title_font=tile_title_font,
            command=self.open_data_analysis,
        )
        self.analysis_tile.grid(row=1, column=1, sticky="nsew", padx=(grid_gap // 2, grid_gap // 2), pady=(0, 14))

        c = tile_colors["summary"]
        self.summary_tile = _MenuTile(
            grid_area,
            icon_text=ICON_SUMMARY,
            title_text="Summary\nView",
            width=tile_width,
            height=tile_height,
            bg_color=c["bg"],
            hover_color=c["hover"],
            border_color=c["border"],
            icon_font_size=icon_font_size,
            title_font=tile_title_font,
            command=self.open_summary,
        )
        self.summary_tile.grid(row=1, column=2, sticky="nsew", padx=(grid_gap, 0), pady=(0, 14))

        c = tile_colors["invest"]
        self.investigators_tile = _MenuTile(
            grid_area,
            icon_text=ICON_INVEST,
            title_text="Investigators",
            width=tile_width,
            height=tile_height,
            bg_color=c["bg"],
            hover_color=c["hover"],
            border_color=c["border"],
            icon_font_size=icon_font_size,
            title_font=tile_title_font,
            command=self.open_investigators,
        )
        self.investigators_tile.grid(row=2, column=0, sticky="nsew", padx=(0, grid_gap), pady=(0, 14))

        c = tile_colors["group"]
        self.group_tile = _MenuTile(
            grid_area,
            icon_text=ICON_GROUP,
            title_text="Group\nConfiguration",
            width=tile_width,
            height=tile_height,
            bg_color=c["bg"],
            hover_color=c["hover"],
            border_color=c["border"],
            icon_font_size=icon_font_size,
            title_font=tile_title_font,
            command=self.open_group_config,
        )
        self.group_tile.grid(row=2, column=1, sticky="nsew", padx=(grid_gap // 2, grid_gap // 2), pady=(0, 14))

        c = tile_colors["cage"]
        self.cage_tile = _MenuTile(
            grid_area,
            icon_text=ICON_CAGE,
            title_text="Cage\nConfiguration",
            width=tile_width,
            height=tile_height,
            bg_color=c["bg"],
            hover_color=c["hover"],
            border_color=c["border"],
            icon_font_size=icon_font_size,
            title_font=tile_title_font,
            command=self.open_cage_config,
        )
        self.cage_tile.grid(row=2, column=2, sticky="nsew", padx=(grid_gap, 0), pady=(0, 14))

        self.delete_button = CTkButton(
            grid_area,
            text=f"{ICON_DELETE}  Delete Experiment",
            command=self.delete_warning,
            corner_radius=18,
            width=(tile_width * 3) + (grid_gap * 2),
            height=46,
            font=CTkFont("Segoe UI Semibold", metrics["font_size"] - 1),
            text_color=("white", "white"),
            fg_color=palette["danger"],
            hover_color="#b91c1c",
        )
        self.delete_button.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(6, 0))

        grid_area.grid_columnconfigure(0, minsize=tile_width, weight=0)
        grid_area.grid_columnconfigure(1, minsize=tile_width, weight=0)
        grid_area.grid_columnconfigure(2, minsize=tile_width, weight=0)

        # ----------------------------
        # Sidebar: Experiment Notebook
        # ----------------------------
        # Rectangular sidebar with a visible colored border (no rounded corners).
        sidebar_card = CTkFrame(
            body_root,
            fg_color=("#f8fafc", "#0b1220"),
            corner_radius=0,
            border_width=3,
            border_color=("#c7d2fe", "#4f46e5"),
            width=320,
        )
        sidebar_card.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(12, 0))
        sidebar_card.grid_propagate(False)
        sidebar_card.grid_rowconfigure(0, weight=1)
        sidebar_card.grid_columnconfigure(0, weight=1)

        # Sidebar content (non-scrollable per preference).
        sidebar = CTkFrame(sidebar_card, fg_color="transparent")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        sidebar.grid_columnconfigure(0, weight=1)

        sb_title_font = CTkFont("Segoe UI Semibold", 16)
        sb_sub_font = CTkFont("Segoe UI", 12)
        sb_label_font = CTkFont("Segoe UI Semibold", 11)
        sb_value_font = CTkFont("Segoe UI Semibold", 13)

        sb_header = CTkFrame(sidebar, fg_color="transparent")
        sb_header.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 8))
        sb_header.grid_columnconfigure(0, weight=1)

        CTkLabel(
            sb_header,
            text=f"{ICON_NOTEBOOK}  Experiment Notebook",
            font=sb_title_font,
            text_color=("black", "white"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        CTkLabel(
            sb_header,
            text="Your personal notes",
            font=sb_sub_font,
            text_color=palette["text_muted"],
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(2, 0))

        info = CTkFrame(sidebar, fg_color="transparent")
        info.grid(row=1, column=0, sticky="ew", padx=14)
        info.grid_columnconfigure(0, weight=1)

        def _info_block(start_row: int, label: str, value: str):
            CTkLabel(info, text=label, font=sb_label_font, text_color=palette["text_muted"], anchor="w").grid(
                row=start_row, column=0, sticky="w", pady=(10, 0)
            )
            CTkLabel(info, text=value, font=sb_value_font, text_color=("black", "white"), anchor="w").grid(
                row=start_row + 1, column=0, sticky="w"
            )

        _info_block(0, "EXPERIMENT", experiment_name or "Unnamed")

        CTkLabel(info, text="STATUS", font=sb_label_font, text_color=palette["text_muted"], anchor="w").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )
        pill = CTkFrame(info, fg_color="#dcfce7", corner_radius=999, border_width=1, border_color="#22c55e")
        pill.grid(row=3, column=0, sticky="w", pady=(4, 0))
        CTkLabel(pill, text="●  Active", font=CTkFont("Segoe UI Semibold", 12), text_color="#166534").pack(
            padx=10, pady=4
        )

        def _make_text_editor(parent, *, height_lines: int):
            # Tk Text inside a CTkFrame gives us reliable multiline editing without extra dependencies.
            from tkinter import Text  # pylint: disable=import-outside-toplevel

            wrapper = CTkFrame(
                parent,
                fg_color=("white", "#0b1220"),
                corner_radius=12,
                border_width=1,
                border_color=palette["card_border"],
            )
            wrapper.grid_columnconfigure(0, weight=1)
            wrapper.grid_rowconfigure(0, weight=1)
            text = Text(
                wrapper,
                height=height_lines,
                wrap="word",
                bd=0,
                highlightthickness=0,
                font=("Segoe UI", 11),
            )
            text.grid(row=0, column=0, sticky="nsew", padx=10, pady=8)
            try:
                text.configure(bg="#ffffff", fg="#0f172a", insertbackground="#0f172a")
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            return wrapper, text

        # Next step (editable + savable)
        next_step_section = CTkFrame(sidebar, fg_color="transparent")
        next_step_section.grid(row=2, column=0, sticky="ew", padx=14, pady=(8, 0))
        next_step_section.grid_columnconfigure(0, weight=1)

        next_step_header = CTkFrame(next_step_section, fg_color="transparent")
        next_step_header.grid(row=0, column=0, sticky="w", pady=(0, 6))
        CTkLabel(
            next_step_header,
            text=ICON_PENCIL,
            font=(_emoji_font_family(), 20),
            text_color="#f97316",
        ).pack(side="left")
        CTkLabel(
            next_step_header,
            text=" Next step",
            font=CTkFont("Segoe UI Semibold", 12),
            text_color="#f97316",
        ).pack(side="left")

        self.next_step_box, self.next_step_text = _make_text_editor(next_step_section, height_lines=4)
        self.next_step_box.grid(row=1, column=0, sticky="ew")

        def save_next_step():
            try:
                value = self.next_step_text.get("1.0", "end").strip()
            except Exception:  # pylint: disable=broad-exception-caught
                value = ""
            self._notebook_set("next_step", value)
            self._notebook_set("next_step_saved_at", datetime.now().isoformat(timespec="seconds"))
            self._persist_temp_to_original_if_available()
            next_saved_label.configure(text=f"saved {datetime.now().strftime('%I:%M %p').lstrip('0')}")
            try:
                next_saved_label.grid()
            except Exception:  # pylint: disable=broad-exception-caught
                pass

        try:
            self.next_step_text.delete("1.0", "end")
            existing_next = (self._notebook_get("next_step", "") or "").strip()
            if not existing_next:
                try:
                    if self.experiment_db.get_number_groups() == 0:
                        existing_next = "Configure group names before assigning cages."
                    elif self.experiment_db.experiment_uses_rfid() == 1 and not self.all_rfid_mapped():
                        existing_next = "Map RFID for all animals before starting data collection."
                    else:
                        existing_next = "Review experiment settings, then begin data collection."
                except Exception:  # pylint: disable=broad-exception-caught
                    existing_next = "Review experiment settings, then begin data collection."
            self.next_step_text.insert("1.0", existing_next)
            self.next_step_text.bind("<FocusOut>", lambda _e: save_next_step())
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        CTkButton(
            next_step_section,
            text="Save next step",
            height=34,
            corner_radius=12,
            fg_color="#f97316",
            hover_color="#ea580c",
            text_color="white",
            font=CTkFont("Segoe UI Semibold", 12),
            command=save_next_step,
        ).grid(row=2, column=0, sticky="ew", pady=(2, 0))

        next_saved_label = CTkLabel(
            next_step_section,
            text="",
            font=CTkFont("Segoe UI", 10),
            text_color=palette["text_muted"],
            anchor="w",
        )
        next_saved_label.grid(row=3, column=0, sticky="w", pady=(2, 0))
        # Hide the "saved ..." line until the user saves the next step.
        try:
            next_saved_label.grid_remove()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

        # My notes (editable + savable)
        notes_section = CTkFrame(sidebar, fg_color="transparent")
        notes_section.grid(row=3, column=0, sticky="ew", padx=14, pady=(2, 14))
        notes_section.grid_columnconfigure(0, weight=1)

        notes_header = CTkFrame(notes_section, fg_color="transparent")
        notes_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        notes_header.grid_columnconfigure(0, weight=1)
        notes_header.grid_columnconfigure(1, weight=0)

        CTkLabel(
            notes_header,
            text="MY NOTES",
            font=sb_label_font,
            text_color=palette["text_muted"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.notes_saved_label = CTkLabel(
            notes_header,
            text="",
            font=CTkFont("Segoe UI", 10),
            text_color=palette["text_muted"],
            anchor="e",
        )
        self.notes_saved_label.grid(row=0, column=1, sticky="e")

        self.notes_box, self.notes_text = _make_text_editor(notes_section, height_lines=7)
        self.notes_box.grid(row=1, column=0, sticky="ew")

        def refresh_notes_saved_label():
            saved = self._notebook_get("notes_saved_at", "")
            if not saved:
                self.notes_saved_label.configure(text="")
                return
            try:
                dt = datetime.fromisoformat(saved)
                self.notes_saved_label.configure(text=f"saved {dt.strftime('%I:%M %p').lstrip('0')}")
            except Exception:  # pylint: disable=broad-exception-caught
                self.notes_saved_label.configure(text="saved")

        def save_note():
            try:
                value = self.notes_text.get("1.0", "end").strip()
            except Exception:  # pylint: disable=broad-exception-caught
                value = ""
            self._notebook_set("my_notes", value)
            self._notebook_set("notes_saved_at", datetime.now().isoformat(timespec="seconds"))
            self._persist_temp_to_original_if_available()
            self.notes_saved_label.configure(text="saved just now")
            self.after(1500, refresh_notes_saved_label)

        try:
            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", self._notebook_get("my_notes", ""))
        except Exception:  # pylint: disable=broad-exception-caught
            pass
        refresh_notes_saved_label()

        CTkButton(
            notes_section,
            text="Save note",
            height=36,
            corner_radius=12,
            fg_color=palette["accent_blue"],
            hover_color="#2563eb",
            text_color="white",
            font=CTkFont("Segoe UI Semibold", 12),
            command=save_note,
        ).grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.disable_buttons_if_needed()

    def open_group_config(self):
        """Open Group Configuration Page for this experiment."""
        try:
            db = ExperimentDatabase(self.file_path)
        except sqlite3.DatabaseError:
            messagebox.showerror(
                "Open Experiment Error",
                "This experiment file could not be opened as a database.\n"
                "If it is password protected, please use the appropriate "
                "flow to unlock it.",
            )
            return

        exp = Experiment()
        exp.set_name(db.get_experiment_name() or "")
        exp.set_num_groups(str(db.get_number_groups()))
        exp.set_group_names(db.get_groups() or [])

        items = db.get_measurement_items()
        if items:
            if isinstance(items, (tuple, list)):
                exp.set_measurement_item(items[0])
            else:
                exp.set_measurement_item(items)

        exp.group_num_changed = False
        exp.measurement_items_changed = False
        exp.data_collect_type = db.get_measurement_type()

        def save_group_config(updated_experiment):
            group_names = updated_experiment.get_group_names()
            db.update_group_names(group_names)
            db.update_measurement_type(updated_experiment.get_measurement_type())

        from experiment_pages.experiment.group_config_ui import (  # pylint: disable=import-error,import-outside-toplevel
            GroupConfigUI,
        )

        page = GroupConfigUI(
            exp,
            self.root,
            self,
            self,
            edit_mode=True,
            save_callback=save_group_config,
        )
        page.raise_frame()

    def open_cage_config(self):
        """Open Cage Configuration Page."""
        try:
            # Validate that the experiment DB is readable before opening the page.
            # If the DB is encrypted/invalid, this prevents a silent callback failure.
            from databases.experiment_database import (  # pylint: disable=import-error,import-outside-toplevel
                ExperimentDatabase,
            )

            db = ExperimentDatabase(self.file_path)
            if db.get_number_groups() == 0:
                messagebox.showinfo(
                    "Groups Required",
                    "No groups are configured yet.\n\n"
                    "Create groups in Group Configuration before assigning cages.",
                )
                self.open_group_config()
                return

            from experiment_pages.experiment.cage_config_ui import (  # pylint: disable=import-error,import-outside-toplevel
                CageConfigUI,
            )

            page = CageConfigUI(self.file_path, self.root, self, self.file_path)
            page.raise_frame()
        except sqlite3.DatabaseError as exc:
            messagebox.showerror(
                "Cage Configuration Error",
                "This experiment file could not be opened as a database.\n\n"
                f"{exc}",
            )
        except Exception as exc:  # pylint: disable=broad-exception-caught
            messagebox.showerror(
                "Cage Configuration Error",
                f"Failed to open Cage Configuration page.\n\n{exc}",
            )

    def open_data_collection(self):
        """Open Data Collection Page."""
        if self.experiment_db.experiment_uses_rfid() == 1 and not self.all_rfid_mapped():
            messagebox.showinfo(
                "RFID Mapping Required",
                "This experiment uses RFID.\n\n"
                "Map RFID for all animals before starting Data Collection.",
            )
            return

        from experiment_pages.experiment.data_collection_ui import (  # pylint: disable=import-error,import-outside-toplevel
            DataCollectionUI,
        )

        try:
            page = DataCollectionUI(
                parent=self.root,
                prev_page=self,
                database_name=self.file_path,
                file_path=self.file_path,
                original_file_path=getattr(self, "original_file_path", None),
            )
            page.raise_frame()
        except Exception as e:  # pylint: disable=broad-exception-caught
            messagebox.showerror("Data Collection Error", f"Failed to open Data Collection page.\n\n{e}")

    def open_data_analysis(self):
        """Open Data Analysis Page."""
        from experiment_pages.experiment.data_analysis_ui import (  # pylint: disable=import-error,import-outside-toplevel
            DataAnalysisUI,
        )

        page = DataAnalysisUI(self.root, self, self.file_path)
        page.raise_frame()

    def open_map_rfid(self):
        """Open Map RFID Page."""
        from experiment_pages.experiment.map_rfid import (  # pylint: disable=import-error,import-outside-toplevel
            MapRFIDPage,
        )

        page = MapRFIDPage(self.file_path, self.root, self, self.file_path)
        page.raise_frame()

    def open_summary(self):
        """Open Experiment Summary Page."""
        from experiment_pages.experiment.review_ui import (  # pylint: disable=import-error,import-outside-toplevel
            ReviewUI,
        )

        page = ReviewUI(self.root, self, self.file_path)
        page.raise_frame()

    def open_investigators(self):
        """Open Investigators Page."""
        from experiment_pages.experiment.experiment_invest_ui import (  # pylint: disable=import-error,import-outside-toplevel
            InvestigatorsUI,
        )

        page = InvestigatorsUI(self.root, self, self.file_path)
        page.raise_frame()

    def all_rfid_mapped(self):
        """Return True if all expected animals have RFID mappings."""
        num_animals = self.experiment_db.get_total_number_animals()
        num_mapped = len(self.experiment_db.get_all_animal_ids())
        return num_animals == num_mapped

    def disable_buttons_if_needed(self):
        """Disable/enable actions based on RFID mapping requirement."""
        if hasattr(self, "group_tile"):
            self.group_tile.set_enabled(True)
        if self.experiment_db.experiment_uses_rfid() == 1:
            if not self.all_rfid_mapped():
                self.collection_tile.set_enabled(False)
                self.analysis_tile.set_enabled(False)
            else:
                self.collection_tile.set_enabled(True)
                self.analysis_tile.set_enabled(True)
            self.rfid_button.configure(state="normal")
        else:
            self.collection_tile.set_enabled(True)
            self.analysis_tile.set_enabled(True)
            self.rfid_button.configure(state="disabled")

    def disconnect_database(self):
        """Close experiment DB connection if possible."""
        try:
            self.experiment_db.close()
        except Exception:  # pylint: disable=broad-exception-caught
            pass

    def delete_warning(self):
        """Ask for confirmation before deleting the experiment file."""
        if not self.file_path:
            messagebox.showerror("Delete Error", "No experiment file is currently loaded.")
            return
        confirmed = messagebox.askyesno(
            "Delete Experiment",
            "This will delete the experiment file and all associated data.\n\n"
            "Are you sure you want to continue?",
        )
        if confirmed:
            self.delete_experiment()

    def delete_experiment(self):
        """Delete the currently opened experiment file and navigate back."""
        self.disconnect_database()
        path = self.file_path
        try:
            if os.path.exists(path):
                os.remove(path)
            else:
                messagebox.showwarning("Delete Warning", f"File not found:\n{path}")
        except OSError as error:
            messagebox.showerror("Delete Error", f"Failed to delete experiment:\n{error}")
            return

        if self.menu_page is not None and hasattr(self.menu_page, "raise_frame"):
            self.menu_page.raise_frame()
        else:
            self.back_to_welcome()

    def raise_frame(self):
        """Refresh button states whenever menu is raised."""
        self.disable_buttons_if_needed()
        super().raise_frame()

    def back_to_welcome(self):
        """Return to the main welcome screen."""
        from ui.welcome_screen import ( 
            setup_welcome_screen,
        )

        setup_welcome_screen(self.root, self)
