#pylint: skip-file
"""Data exporting and analysis page."""

import os
from datetime import datetime, timedelta
from collections import defaultdict
from tkinter import filedialog
from tkinter.ttk import Treeview, Style
from PIL import Image, ImageDraw

from customtkinter import (
    CTkButton,
    CTkCanvas,
    CTkFrame,
    CTkLabel,
    CTkScrollbar,
    CTkToplevel,
    CTkOptionMenu,
    CTkScrollableFrame,
    CENTER,
    CTkFont,
    CTkImage,
    get_appearance_mode,
)

from shared.tk_models import MouserPage, get_ui_metrics
from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND


class DataAnalysisUI(MouserPage):
    """Data exporting UI with table and weight trend graph."""

    @staticmethod
    def _draw_export_icon(color: str, size: int) -> Image.Image:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        stroke = max(2, size // 10)
        mid = size // 2
        top = size // 5
        bottom = size - size // 4

        # Arrow shaft
        draw.line((mid, top, mid, bottom - stroke), fill=color, width=stroke)
        # Arrow head
        head = size // 4
        draw.polygon(
            [(mid - head // 2, bottom - head), (mid + head // 2, bottom - head), (mid, bottom)],
            fill=color,
        )
        # Tray
        tray_y = size - size // 6
        margin = size // 4
        draw.rounded_rectangle(
            (margin, tray_y - stroke * 2, size - margin, tray_y + stroke * 2),
            radius=stroke * 2,
            outline=color,
            width=stroke,
        )
        return image

    @staticmethod
    def _draw_refresh_icon(color: str, size: int) -> Image.Image:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        stroke = max(2, size // 10)
        pad = size // 5
        box = (pad, pad, size - pad, size - pad)
        # Arc
        draw.arc(box, start=40, end=330, fill=color, width=stroke)
        # Arrow head (near top-right)
        tip_x = size - pad
        tip_y = pad + stroke
        head = size // 5
        draw.polygon(
            [
                (tip_x, tip_y),
                (tip_x - head, tip_y + head // 3),
                (tip_x - head // 3, tip_y + head),
            ],
            fill=color,
        )
        return image

    def __init__(self, parent, prev_page=None, db_file=None):
        super().__init__(parent, "Data Exporting", prev_page)
        ui = get_ui_metrics()
        self.db_file = db_file
        self.ui = ui
        is_dark = get_appearance_mode().lower() == "dark"

        def _pick(color_value):
            if isinstance(color_value, (tuple, list)) and len(color_value) >= 2:
                return color_value[1] if is_dark else color_value[0]
            return color_value

        self._pick = _pick
        self._palette = {
            "page_bg": ("#eef2ff", "#0b1220"),
            "card_bg": ("#ffffff", "#101827"),
            "card_border": ("#c7d2fe", "#22304a"),
            "text": ("#0f172a", "#e5e7eb"),
            "muted_text": ("#334155", "#cbd5e1"),
            "table_bg": ("#ffffff", "#0b1220"),
            "table_alt_bg": ("#f8fafc", "#0f172a"),
            "table_header_bg": ("#e0f2fe", "#1e293b"),
            "table_header_fg": ("#0f172a", "#e5e7eb"),
            "table_selected_bg": ("#dbeafe", "#1d4ed8"),
            "table_selected_fg": ("#111827", "#ffffff"),
        }
        self.configure(fg_color=self._palette["page_bg"])
        self.chart_colors = [
            "#2563eb",
            "#dc2626",
            "#059669",
            "#d97706",
            "#7c3aed",
            "#0891b2",
            "#be123c",
        ]
        self._export_notice = None
        self._range_days = None  # None = All

        # Top bar
        top_bar = CTkFrame(self, fg_color=self._palette["card_bg"], corner_radius=0, height=84)
        top_bar.place(relx=0.0, rely=0.0, relwidth=1.0)
        CTkFrame(top_bar, fg_color=_pick(self._palette["card_border"]), height=1).pack(side="bottom", fill="x")

        if hasattr(self, "menu_button") and self.menu_button:
            try:
                self.menu_button.configure(
                    corner_radius=12,
                    height=40,
                    width=54,
                    text="⬅",
                    font=("Segoe UI Semibold", 20),
                    text_color="white",
                    fg_color="#f59e0b",
                    hover_color="#d97706",
                )
                self.menu_button.place_configure(in_=top_bar, relx=0.0, rely=0.0, x=16, y=22, anchor="nw")
            except Exception:
                pass

        # Sidebar owns Refresh/Export buttons (functional).

        # Body layout (content + sidebar)
        body = CTkFrame(self, fg_color="transparent")
        body.place(relx=0.5, rely=0.0, y=88, anchor="n", relwidth=0.94, relheight=0.90)
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=4)
        body.grid_columnconfigure(1, weight=1)

        self.left_panel = CTkFrame(body, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(0, weight=0)  # header
        self.left_panel.grid_rowconfigure(1, weight=0)  # tiles
        self.left_panel.grid_rowconfigure(2, weight=0)  # chart
        self.left_panel.grid_rowconfigure(3, weight=0)  # table
        self.left_panel.grid_rowconfigure(4, weight=1)  # spacer

        self.sidebar = CTkFrame(body, fg_color="transparent")
        self.sidebar.grid(row=0, column=1, sticky="nsew")
        self.sidebar.grid_columnconfigure(0, weight=1)
        # Keep the sidebar content compact; use a spacer row to absorb extra height.
        self.sidebar.grid_rowconfigure(2, weight=0)
        self.sidebar.grid_rowconfigure(3, weight=1)

        # Header
        left_header = CTkFrame(self.left_panel, fg_color="transparent")
        left_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        title_row = CTkFrame(left_header, fg_color="transparent")
        title_row.pack(anchor="w")
        CTkLabel(
            title_row,
            text="📈",
            font=CTkFont("Segoe UI Semibold", 18),
            text_color=self._palette["text"],
            width=0,
        ).pack(side="left", padx=(0, 8))
        CTkLabel(
            title_row,
            text="Data analysis",
            font=CTkFont("Segoe UI Semibold", 24),
            text_color=self._palette["text"],
        ).pack(side="left")
        CTkLabel(
            left_header,
            text="Export and visualize measurement trends",
            font=CTkFont("Segoe UI", 12),
            text_color=self._palette["muted_text"],
        ).pack(anchor="w", pady=(2, 0))

        # Summary tiles (Animals / Dates / Points / Avg change)
        stats_row = CTkFrame(self.left_panel, fg_color="transparent")
        stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        for col in range(4):
            stats_row.grid_columnconfigure(col, weight=1, uniform="stats")

        def _stat_tile(col_index, title, value_color, tile_bg, tile_border):
            tile = CTkFrame(
                stats_row,
                fg_color=_pick(tile_bg),
                corner_radius=14,
                border_width=1,
                border_color=_pick(tile_border),
                height=108,
            )
            tile.grid(row=0, column=col_index, sticky="ew", padx=4, pady=0)
            tile.grid_propagate(False)
            title_label = CTkLabel(
                tile,
                text=title,
                font=CTkFont("Segoe UI", 11),
                text_color=self._palette["muted_text"],
                anchor="w",
            )
            title_label.pack(fill="x", padx=14, pady=(6, 0))
            value_label = CTkLabel(
                tile,
                text="--",
                font=CTkFont("Segoe UI Semibold", 22),
                text_color=value_color,
                anchor="w",
            )
            value_label.pack(fill="x", padx=14, pady=(0, 0))
            subtitle_label = CTkLabel(
                tile,
                text="",
                font=CTkFont("Segoe UI", 10),
                text_color=self._palette["muted_text"],
                anchor="w",
            )
            subtitle_label.pack(fill="x", padx=14, pady=(0, 8))
            return title_label, value_label, subtitle_label

        self.animals_title, self.animals_value, self.animals_subtitle = _stat_tile(
            0,
            "Animals tracked",
            _pick(self._palette["text"]),
            ("#f1f5f9", "#0f172a"),
            ("#94a3b8", "#475569"),
        )
        self.dates_title, self.dates_value, self.dates_subtitle = _stat_tile(
            1,
            "Measurement dates",
            ("#2563eb", "#60a5fa"),
            ("#eef2ff", "#111827"),
            ("#818cf8", "#818cf8"),
        )
        self.points_title, self.points_value, self.points_subtitle = _stat_tile(
            2,
            "Total data points",
            ("#16a34a", "#34d399"),
            ("#ecfdf5", "#042f2e"),
            ("#34d399", "#34d399"),
        )
        self.change_title, self.change_value, self.change_subtitle = _stat_tile(
            3,
            "Avg change",
            ("#a16207", "#fbbf24"),
            ("#fffbeb", "#2e1f0a"),
            ("#f59e0b", "#f59e0b"),
        )

        # Summary label kept for compatibility but hidden (tiles show stats).
        self.summary_label = CTkLabel(
            self.left_panel,
            text="",
            font=CTkFont("Segoe UI", 12),
            text_color=_pick(self._palette["muted_text"]),
        )

        CTkFrame(self.left_panel, fg_color="transparent").grid(row=4, column=0, sticky="nsew")

        # Sidebar controls
        sidebar_card = CTkFrame(
            self.sidebar,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        sidebar_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        sidebar_card.grid_columnconfigure(0, weight=1)

        CTkLabel(
            sidebar_card,
            text="Controls",
            font=CTkFont("Segoe UI Semibold", 14),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        self.export_button = CTkButton(
            sidebar_card,
            text="⭳  Export CSV",
            height=42,
            corner_radius=12,
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
            font=CTkFont("Segoe UI Semibold", 16),
            command=self.export_to_csv,
        )
        self.export_button.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 8))

        self.refresh_button = CTkButton(
            sidebar_card,
            text="⟲  Refresh",
            height=42,
            corner_radius=12,
            fg_color=self._palette["card_bg"],
            hover_color=self._pick(self._palette["table_alt_bg"]),
            border_width=1,
            border_color=self._pick(self._palette["card_border"]),
            text_color=self._pick(self._palette["text"]),
            font=CTkFont("Segoe UI Semibold", 16),
            command=self.refresh_analysis_view,
        )
        self.refresh_button.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        device_card = CTkFrame(
            self.sidebar,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
        )
        device_card.grid(row=1, column=0, sticky="ew")
        device_card.grid_columnconfigure(0, weight=1)

        CTkLabel(
            device_card,
            text="Device / Measurement",
            font=CTkFont("Segoe UI Semibold", 14),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 6))

        self._measurement_choices = self._get_measurement_choices()
        self._selected_measurement_key = self._measurement_choices[0]["key"] if self._measurement_choices else "weight"
        self._selected_measurement_id = self._measurement_choices[0]["id"] if self._measurement_choices else 1
        self._selected_measurement_label = self._measurement_choices[0]["label"] if self._measurement_choices else "Weight"

        self.device_menu = CTkOptionMenu(
            device_card,
            values=[c["label"] for c in self._measurement_choices] or ["Weight"],
            command=self._on_device_selected,
            fg_color=self._palette["card_bg"],
            button_color=self._pick(self._palette["table_alt_bg"]),
            button_hover_color=self._pick(self._palette["table_selected_bg"]),
            text_color=self._pick(self._palette["text"]),
            dropdown_fg_color=self._pick(self._palette["card_bg"]),
            dropdown_text_color=self._pick(self._palette["text"]),
            dropdown_hover_color=self._pick(self._palette["table_alt_bg"]),
            font=CTkFont("Segoe UI", 12),
        )
        self.device_menu.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 14))

        self._build_daily_comparison_card(parent=self.sidebar)

        # Spacer to keep cards pinned to the top of the sidebar.
        CTkFrame(self.sidebar, fg_color="transparent").grid(row=3, column=0, sticky="nsew")

        self._build_chart_section(parent=self.left_panel)
        self._build_table_section(parent=self.left_panel)
        self.refresh_analysis_view()

    def _split_measurements(self, raw_value):
        if raw_value is None:
            return []
        text = str(raw_value).strip()
        if not text:
            return []
        parts = [p.strip() for p in text.replace("\n", ",").split(",")]
        return [p for p in parts if p]

    def _get_measurement_choices(self):
        """Build measurement choices from the experiment's measurement string (UI only)."""
        if not self.db_file or not os.path.exists(self.db_file):
            return [{"key": "weight", "label": "Weight", "id": 1}]

        try:
            db = ExperimentDatabase(self.db_file)
            measurement_name = db.get_measurement_items()
            if isinstance(measurement_name, (list, tuple)):
                measurement_name = measurement_name[0] if measurement_name else None
        except Exception:
            measurement_name = None

        items = self._split_measurements(measurement_name)
        if not items:
            items = ["weight"]

        choices = []
        for idx, item in enumerate(items, start=1):
            key = str(item).strip().lower()
            label = str(item).strip() or f"Measurement {idx}"
            if key == "caliper":
                label = "Caliper (Length)"
            elif key == "weight":
                label = "Balance (Weight)"
            choices.append({"key": key, "label": label, "id": idx})
        return choices

    def _on_device_selected(self, selected_label):
        for choice in self._measurement_choices:
            if choice["label"] == selected_label:
                self._selected_measurement_key = choice["key"]
                self._selected_measurement_id = choice["id"]
                self._selected_measurement_label = choice["label"]
                break
        self.refresh_analysis_view()

    def _build_daily_comparison_card(self, parent):
        card = CTkFrame(
            parent,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._palette["card_border"],
            height=420,
        )
        card.grid(row=2, column=0, sticky="ew", pady=(12, 0))
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        header = CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
        header.grid_columnconfigure(0, weight=1)

        CTkLabel(
            header,
            text="Animals",
            font=CTkFont("Segoe UI Semibold", 14),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w")

        self.daily_comparison_subtitle = CTkLabel(
            header,
            text="Latest vs previous day",
            font=CTkFont("Segoe UI", 11),
            text_color=self._palette["muted_text"],
        )
        self.daily_comparison_subtitle.grid(row=1, column=0, sticky="w", pady=(2, 0))

        CTkFrame(card, fg_color=self._pick(self._palette["card_border"]), height=1).grid(
            row=1, column=0, sticky="ew", padx=0, pady=(0, 6)
        )

        self.daily_comparison_frame = CTkScrollableFrame(
            card,
            fg_color="transparent",
            corner_radius=0,
            border_width=0,
            height=240,
        )
        self.daily_comparison_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.daily_comparison_frame.grid_columnconfigure(0, weight=1)

    def _populate_daily_comparison_card(self, rows):
        try:
            frame = getattr(self, "daily_comparison_frame", None)
            subtitle = getattr(self, "daily_comparison_subtitle", None)
            if frame is None:
                return
            for child in frame.winfo_children():
                child.destroy()
        except Exception:
            return

        if not rows:
            try:
                if subtitle is not None:
                    subtitle.configure(text="No measurements yet")
            except Exception:
                pass
            CTkLabel(
                frame,
                text="No measurements available",
                font=CTkFont("Segoe UI", 12),
                text_color=self._pick(self._palette["muted_text"]),
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=4, pady=(6, 0))
            return

        try:
            latest = max(datetime.strptime(str(d), "%Y-%m-%d").date() for d, _aid, _val in rows)
        except Exception:
            latest = None
        if latest is None:
            return
        prev = latest - timedelta(days=1)
        latest_s = latest.strftime("%Y-%m-%d")
        prev_s = prev.strftime("%Y-%m-%d")

        try:
            label = str(getattr(self, "_selected_measurement_label", "") or "").strip()
            key = str(getattr(self, "_selected_measurement_key", "") or "").strip().lower()
            unit = self._infer_unit_for_measurement(key=key, label=label).strip()
            if subtitle is not None:
                subtitle.configure(text=f"{label or 'Measurement'}: {latest_s} vs {prev_s}")
        except Exception:
            unit = ""

        lookup = {(d, aid): val for d, aid, val in rows}
        animals = sorted({aid for _d, aid, _v in rows})
        color_map = {
            animal_id: self.chart_colors[idx % len(self.chart_colors)] for idx, animal_id in enumerate(animals)
        }

        current_by_animal = {aid: lookup.get((latest_s, aid)) for aid in animals}

        def _sort_key(animal_id):
            cur = current_by_animal.get(animal_id)
            if cur is None:
                return (1, 0.0, animal_id)
            return (0, -float(cur), animal_id)

        sorted_animals = sorted(animals, key=_sort_key)
        text_color = self._pick(self._palette["text"])
        muted = self._pick(self._palette["muted_text"])

        for idx, animal_id in enumerate(sorted_animals):
            cur = current_by_animal.get(animal_id)
            prev_val = lookup.get((prev_s, animal_id))

            delta = None
            if cur is not None and prev_val is not None:
                try:
                    delta = float(cur) - float(prev_val)
                except Exception:
                    delta = None

            value_text = "--" if cur is None else f"{self._format_stat_number(cur)}{unit}"
            if delta is None:
                delta_text = "--"
                delta_color = muted
            else:
                prefix = "+" if delta > 0 else ""
                delta_text = f"{prefix}{self._format_stat_number(delta)}{unit}"
                if delta > 0:
                    delta_color = "#16a34a"
                elif delta < 0:
                    delta_color = "#dc2626"
                else:
                    delta_color = text_color

            row = CTkFrame(frame, fg_color="transparent")
            row.grid(row=idx, column=0, sticky="ew", padx=2, pady=2)
            row.grid_columnconfigure(1, weight=1)

            CTkLabel(
                row,
                text="●",
                font=CTkFont("Segoe UI Semibold", 12),
                text_color=color_map.get(animal_id, text_color),
                width=0,
            ).grid(row=0, column=0, sticky="w", padx=(2, 6))

            CTkLabel(
                row,
                text=f"Animal {animal_id}",
                font=CTkFont("Segoe UI", 12),
                text_color=text_color,
                anchor="w",
            ).grid(row=0, column=1, sticky="w")

            right = CTkFrame(row, fg_color="transparent")
            right.grid(row=0, column=2, sticky="e")
            right.grid_columnconfigure(0, weight=1)

            CTkLabel(
                right,
                text=value_text,
                font=CTkFont("Segoe UI Semibold", 13),
                text_color=text_color,
                anchor="e",
            ).grid(row=0, column=0, sticky="e")

            CTkLabel(
                right,
                text=delta_text,
                font=CTkFont("Segoe UI", 11),
                text_color=delta_color,
                anchor="e",
            ).grid(row=1, column=0, sticky="e", pady=(0, 2))

    def _build_table_section(self, parent):
        table_card = CTkFrame(
            parent,
            fg_color=self._palette["card_bg"],
            corner_radius=14,
            border_width=1,
            border_color=self._pick(self._palette["card_border"]),
        )
        table_card.grid(row=3, column=0, sticky="ew")
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)

        # Inset helps the rounded border look clean around a ttk Treeview (square corners).
        table_inset = CTkFrame(
            table_card,
            fg_color=self._pick(self._palette["table_bg"]),
            corner_radius=12,
            border_width=0,
        )
        table_inset.grid(row=0, column=0, sticky="ew", padx=7, pady=7)
        table_inset.grid_columnconfigure(0, weight=1)
        table_inset.grid_rowconfigure(0, weight=1)

        style = Style()
        try:
            if style.theme_use() in {"vista", "xpnative"}:
                style.theme_use("clam")
        except Exception:
            pass
        style.configure(
            "Export.Treeview",
            background=self._pick(self._palette["table_bg"]),
            fieldbackground=self._pick(self._palette["table_bg"]),
            foreground=self._pick(self._palette["text"]),
            font=("Segoe UI", max(12, self.ui["table_font_size"])),
            rowheight=self.ui["table_row_height"] + 2,
            borderwidth=0,
        )
        style.configure(
            "Export.Treeview.Heading",
            background=self._pick(self._palette["table_header_bg"]),
            foreground=self._pick(self._palette["table_header_fg"]),
            font=("Segoe UI Semibold", max(12, self.ui["table_font_size"])),
            relief="flat",
            padding=(10, 6),
        )
        style.map(
            "Export.Treeview",
            background=[("selected", self._pick(self._palette["table_selected_bg"]))],
            foreground=[("selected", self._pick(self._palette["table_selected_fg"]))],
        )

        self.table = Treeview(
            table_inset,
            columns=("date", "animal_id", "weight"),
            show="headings",
            style="Export.Treeview",
            selectmode="browse",
            height=8,
        )
        self.table.heading("date", text="Date", anchor="center")
        self.table.heading("animal_id", text="Animal ID", anchor="center")
        self.table.heading("weight", text="Weight", anchor="center")
        self.table.column("date", width=220, anchor="center", stretch=True)
        self.table.column("animal_id", width=170, anchor="center", stretch=True)
        self.table.column("weight", width=170, anchor="center", stretch=True)
        self.table.grid(row=0, column=0, sticky="nsew")

        try:
            self.table.tag_configure("odd", background=self._pick(self._palette["table_alt_bg"]))
            self.table.tag_configure("even", background=self._pick(self._palette["table_bg"]))
        except Exception:
            pass

        scrollbar = CTkScrollbar(table_inset, orientation="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(2, 0))

    def _build_chart_section(self, parent):
        chart_card = CTkFrame(
            parent,
            fg_color=self._palette["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=self._pick(self._palette["card_border"]),
            height=250,
        )
        chart_card.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(0, weight=0)
        chart_card.grid_rowconfigure(1, weight=0)
        chart_card.grid_rowconfigure(2, weight=1)
        chart_card.grid_propagate(False)

        header = CTkFrame(chart_card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        header.grid_columnconfigure(0, weight=1)

        CTkLabel(
            header,
            text="Weight trends",
            font=CTkFont("Segoe UI Semibold", 13),
            text_color=self._palette["text"],
        ).grid(row=0, column=0, sticky="w")

        chips = CTkFrame(header, fg_color="transparent")
        chips.grid(row=0, column=1, sticky="e")

        self._range_buttons = {}

        def _chip(col, text, key, days):
            btn = CTkButton(
                chips,
                text=text,
                width=44,
                height=26,
                corner_radius=999,
                fg_color=self._pick(self._palette["card_bg"]),
                hover_color=self._pick(self._palette["table_alt_bg"]),
                border_width=1,
                border_color=self._pick(self._palette["card_border"]),
                text_color=self._pick(self._palette["text"]),
                font=CTkFont("Segoe UI Semibold", 11),
                command=lambda d=days: self._on_range_chip(d),
            )
            btn.grid(row=0, column=col, padx=4)
            self._range_buttons[key] = btn

        _chip(0, "All", "all", None)
        _chip(1, "7d", "7", 7)
        _chip(2, "14d", "14", 14)
        _chip(3, "28d", "28", 28)
        self._set_range(self._range_days)

        CTkFrame(chart_card, fg_color=self._pick(self._palette["card_border"]), height=1).grid(
            row=1, column=0, sticky="ew"
        )

        content = CTkFrame(chart_card, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=12, pady=(8, 12))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_rowconfigure(0, weight=1)

        self.chart_canvas = CTkCanvas(
            content, highlightthickness=0, bg=self._pick(self._palette["table_bg"])
        )
        self.chart_canvas.grid(row=0, column=0, sticky="nsew")
        self.chart_canvas.bind("<Configure>", lambda _e: self.refresh_analysis_view(redraw_only=True))

        legend_card = CTkFrame(
            content,
            fg_color=self._pick(self._palette["card_bg"]),
            corner_radius=12,
            border_width=1,
            border_color=self._pick(self._palette["card_border"]),
            width=140,
        )
        legend_card.grid(row=0, column=1, sticky="ns", padx=(12, 0))
        legend_card.grid_propagate(False)
        legend_card.grid_columnconfigure(0, weight=1)
        legend_card.grid_rowconfigure(1, weight=1)

        CTkLabel(
            legend_card,
            text="Animals",
            font=CTkFont("Segoe UI Semibold", 12),
            text_color=self._pick(self._palette["text"]),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 6))

        self.legend_frame = CTkScrollableFrame(
            legend_card,
            fg_color="transparent",
            corner_radius=0,
            border_width=0,
            width=140,
            height=1,
        )
        self.legend_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 8))
        self.legend_frame.grid_columnconfigure(0, weight=1)

    def _load_measurement_rows(self, measurement_id: int):
        if not self.db_file or not os.path.exists(self.db_file):
            return []
        db = ExperimentDatabase(self.db_file)
        if int(measurement_id or 1) == 1:
            db._c.execute(
                """
                SELECT DATE(timestamp) as measurement_date, animal_id, value
                FROM animal_measurements
                WHERE value IS NOT NULL
                  AND (measurement_id IS NULL OR measurement_id = 1)
                ORDER BY measurement_date ASC, animal_id ASC
                """
            )
        else:
            db._c.execute(
                """
                SELECT DATE(timestamp) as measurement_date, animal_id, value
                FROM animal_measurements
                WHERE value IS NOT NULL
                  AND measurement_id = ?
                ORDER BY measurement_date ASC, animal_id ASC
                """,
                (int(measurement_id),),
            )
        rows = db._c.fetchall()
        return [(str(d), int(aid), float(val)) for d, aid, val in rows]

    def _set_range(self, days):
        self._range_days = days
        try:
            if hasattr(self, "_range_buttons") and self._range_buttons:
                for key, btn in self._range_buttons.items():
                    selected = (key == "all" and days is None) or (key == str(days))
                    btn.configure(
                        fg_color="#2563eb" if selected else self._pick(self._palette["card_bg"]),
                        text_color="white" if selected else self._pick(self._palette["text"]),
                        border_width=0 if selected else 1,
                        border_color=self._pick(self._palette["card_border"]),
                        hover_color="#1e40af" if selected else self._pick(self._palette["table_alt_bg"]),
                    )
        except Exception:
            pass

    def _on_range_chip(self, days):
        self._set_range(days)
        self.refresh_analysis_view()

    def _filter_rows_by_range(self, rows):
        if not rows or self._range_days is None:
            return rows
        try:
            days = int(self._range_days)
        except Exception:
            return rows
        if days <= 0:
            return rows

        # Range filters are relative to today (not the most recent measurement date):
        # 7d means from (today - 6 days) through today, inclusive.
        today = datetime.now().date()
        min_date = today - timedelta(days=days - 1)
        filtered = []
        for d, aid, val in rows:
            try:
                row_date = datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                continue
            if min_date <= row_date <= today:
                filtered.append((d, aid, val))
        return filtered

    def refresh_analysis_view(self, redraw_only=False):
        selected_measurement_id = getattr(self, "_selected_measurement_id", 1)

        # Tiles should summarize progress from the first measurement date until today (not range-filtered).
        all_rows = self._load_measurement_rows(selected_measurement_id)

        # Chart/table respect the selected range filter chips.
        rows = self._filter_rows_by_range(list(all_rows))
        if not redraw_only:
            self._populate_table(rows)
            self._populate_legend(rows)
            self._populate_daily_comparison_card(rows)

            animal_total, sacrificed = self._load_animal_counts()
            measured_days, span_days = self._compute_measured_days_and_span(all_rows)
            filled_points = len(all_rows)
            total_expected = int(animal_total) * int(measured_days) if animal_total and measured_days else 0

            # Avg change since start (per-animal delta, averaged).
            avg_change = self._compute_average_change(all_rows)
            change_text, change_color, change_title = self._format_change_stat(avg_change)

            self.summary_label.configure(text="")
            try:
                if getattr(self, "animals_value", None) is not None:
                    self.animals_value.configure(text=str(animal_total))
                if getattr(self, "animals_subtitle", None) is not None:
                    self.animals_subtitle.configure(
                        text="• All active" if int(sacrificed or 0) == 0 else f"• {int(sacrificed)} sacrificed"
                    )

                if getattr(self, "dates_value", None) is not None:
                    self.dates_value.configure(text=str(measured_days))
                if getattr(self, "dates_subtitle", None) is not None:
                    self.dates_subtitle.configure(
                        text="No data yet" if measured_days == 0 else f"Over {span_days} days"
                    )

                if getattr(self, "points_value", None) is not None:
                    self.points_value.configure(text=str(filled_points))
                if getattr(self, "points_subtitle", None) is not None:
                    if total_expected > 0:
                        self.points_subtitle.configure(text=f"{filled_points}/{total_expected} filled")
                    else:
                        self.points_subtitle.configure(text="0/0 filled")

                if getattr(self, "change_title", None) is not None:
                    self.change_title.configure(text=change_title)
                if getattr(self, "change_value", None) is not None:
                    self.change_value.configure(text=change_text, text_color=change_color)
                if getattr(self, "change_subtitle", None) is not None:
                    self.change_subtitle.configure(text="since start")
            except Exception:
                pass
        self._draw_trend_chart(rows)

    def _load_animal_counts(self):
        """Return (total_animals, sacrificed_animals) for this experiment DB."""
        if not self.db_file or not os.path.exists(self.db_file):
            return 0, 0
        db = None
        try:
            db = ExperimentDatabase(self.db_file)
            db._c.execute("SELECT COUNT(*) FROM animals")
            total = db._c.fetchone()
            total_animals = int(total[0]) if total and total[0] is not None else 0

            db._c.execute("SELECT COUNT(*) FROM animals WHERE active = 0")
            inactive = db._c.fetchone()
            sacrificed = int(inactive[0]) if inactive and inactive[0] is not None else 0
            return total_animals, sacrificed
        except Exception:
            return 0, 0
        finally:
            try:
                if db is not None:
                    db._conn.commit()
            except Exception:
                pass

    @staticmethod
    def _compute_measured_days_and_span(rows):
        """Return (measured_days, span_days_from_first_to_today)."""
        if not rows:
            return 0, 0
        try:
            dates = sorted({datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows if r and r[0]})
        except Exception:
            return 0, 0
        if not dates:
            return 0, 0
        first = dates[0]
        today = datetime.now().date()
        span_days = max(1, (today - first).days + 1)
        return len(dates), span_days

    @staticmethod
    def _compute_average_change(rows):
        """Average per-animal change from first date to last date (returns float or None)."""
        if not rows:
            return None
        by_animal = defaultdict(list)
        for d, aid, val in rows:
            try:
                day = datetime.strptime(str(d), "%Y-%m-%d").date()
                by_animal[int(aid)].append((day, float(val)))
            except Exception:
                continue

        deltas = []
        for _aid, points in by_animal.items():
            if len(points) < 2:
                continue
            points.sort(key=lambda p: p[0])
            first_val = points[0][1]
            last_val = points[-1][1]
            if first_val is None or last_val is None:
                continue
            deltas.append(last_val - first_val)

        if not deltas:
            return None
        return sum(deltas) / float(len(deltas))

    def _format_change_stat(self, avg_change):
        """Return (value_text, value_color, title_text) for the avg change tile."""
        label = str(getattr(self, "_selected_measurement_label", "") or "").strip() or "Measurement"
        key = str(getattr(self, "_selected_measurement_key", "") or "").strip().lower()
        metric = self._metric_from_label(label=label, key=key)
        title_text = f"Avg {metric} change" if metric else "Avg change"

        unit = self._infer_unit_for_measurement(key=key, label=label)
        if avg_change is None:
            return "--", self._pick(self._palette["muted_text"]), title_text

        try:
            num = float(avg_change)
        except Exception:
            return "--", self._pick(self._palette["muted_text"]), title_text

        prefix = "+" if num > 0 else ""
        text = f"{prefix}{self._format_stat_number(num)}{unit}"
        if num > 0:
            color = "#16a34a"
        elif num < 0:
            color = "#dc2626"
        else:
            color = self._pick(self._palette["text"])
        return text, color, title_text

    @staticmethod
    def _metric_from_label(label="", key=""):
        label = str(label or "").strip()
        key = str(key or "").strip().lower()
        if "(" in label and ")" in label:
            try:
                inner = label.split("(", 1)[1].split(")", 1)[0].strip()
                if inner:
                    return inner
            except Exception:
                pass
        if any(token in (key + " " + label).lower() for token in ("weight", "balance", "balancer", "scale")):
            return "weight"
        if any(token in (key + " " + label).lower() for token in ("caliper", "length")):
            return "length"
        if any(token in (key + " " + label).lower() for token in ("therm", "temp", "temperature")):
            return "temperature"
        return label or "measurement"

    @staticmethod
    def _format_stat_number(value):
        try:
            value = float(value)
        except Exception:
            return "--"
        if abs(value) >= 100:
            return f"{value:.0f}"
        text = f"{value:.2f}"
        return text.rstrip("0").rstrip(".")

    @staticmethod
    def _infer_unit_for_measurement(key="", label=""):
        combined = f"{key} {label}".lower()
        if any(token in combined for token in ("weight", "balance", "balancer", "scale")):
            return " g"
        if any(token in combined for token in ("caliper", "length", "mm")):
            return " mm"
        if any(token in combined for token in ("therm", "temp", "temperature", "°c", "celsius")):
            return " °C"
        return ""

    def _populate_legend(self, rows):
        try:
            if not hasattr(self, "legend_frame") or self.legend_frame is None:
                return
            for child in self.legend_frame.winfo_children():
                child.destroy()
        except Exception:
            return

        animals = sorted({aid for _d, aid, _v in rows})
        text_color = self._pick(self._palette["text"])

        # Legend only (no per-animal stats shown here).

        for idx, animal_id in enumerate(animals):
            color = self.chart_colors[idx % len(self.chart_colors)]
            row = CTkFrame(self.legend_frame, fg_color="transparent")
            row.grid(row=idx, column=0, sticky="ew", padx=2, pady=0)
            row.grid_columnconfigure(1, weight=1)

            CTkLabel(
                row,
                text="●",
                font=CTkFont("Segoe UI Semibold", 12),
                text_color=color,
                width=0,
            ).grid(row=0, column=0, sticky="w", padx=(2, 6))

            CTkLabel(
                row,
                text=f"Animal {animal_id}",
                font=CTkFont("Segoe UI", 11),
                text_color=text_color,
                anchor="w",
            ).grid(row=0, column=1, sticky="w")

    def _populate_table(self, rows):
        date_list = sorted({measurement_date for measurement_date, _animal_id, _weight in rows})
        animal_ids = sorted({animal_id for _measurement_date, animal_id, _weight in rows})
        lookup = {(measurement_date, animal_id): weight for measurement_date, animal_id, weight in rows}

        columns = ("animal_id", *date_list)
        self.table.configure(columns=columns)
        self.table.heading("animal_id", text="Animal ID", anchor="center")
        self.table.column("animal_id", width=130, anchor="center", stretch=False)
        for measurement_date in date_list:
            self.table.heading(measurement_date, text=measurement_date, anchor="center")
            self.table.column(measurement_date, width=130, anchor="center", stretch=True)

        for item in self.table.get_children():
            self.table.delete(item)
        for idx, animal_id in enumerate(animal_ids):
            row_values = [animal_id]
            for measurement_date in date_list:
                value = lookup.get((measurement_date, animal_id))
                row_values.append(f"{value:.2f}" if value is not None else "-")
            tag = "even" if idx % 2 == 0 else "odd"
            self.table.insert("", "end", values=tuple(row_values), tags=(tag,))

    def _draw_trend_chart(self, rows):
        canvas = self.chart_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 200)
        height = max(canvas.winfo_height(), 180)
        left, right, top, bottom = 96, 40, 18, 64
        plot_w = max(width - left - right, 50)
        plot_h = max(height - top - bottom, 50)

        text_color = self._pick(self._palette["text"])
        muted_text = self._pick(self._palette["muted_text"])
        border_color = self._pick(self._palette["card_border"])
        grid_color = self._pick(("#e5e7eb", "#22304a"))

        y_label = getattr(self, "_selected_measurement_label", "Measurement")
        canvas.create_rectangle(
            left,
            top,
            left + plot_w,
            top + plot_h,
            outline=border_color,
            width=1,
            fill=self._pick(self._palette["table_bg"]),
        )
        canvas.create_text(24, top + plot_h / 2, text=y_label, anchor="center", angle=90, fill=text_color)
        canvas.create_text(left + plot_w / 2, height - 16, text="Date", fill=text_color)

        if not rows:
            canvas.create_text(width / 2, height / 2, text="No data available yet.", fill=muted_text)
            return

        dates = sorted({row[0] for row in rows})
        date_index = {d: idx for idx, d in enumerate(dates)}
        by_animal = defaultdict(list)
        min_w = min(row[2] for row in rows)
        max_w = max(row[2] for row in rows)
        if min_w == max_w:
            min_w -= 1
            max_w += 1

        x_map = {}
        if len(dates) == 1:
            x_map[dates[0]] = left + (plot_w / 2)
        else:
            # Add a little horizontal padding so first/last points don't sit on the plot border.
            x_pad = min(24, max(12, int(plot_w * 0.04)))
            x_span = max(1, plot_w - (2 * x_pad))
            for idx, d in enumerate(dates):
                x_map[d] = left + x_pad + (idx * x_span / (len(dates) - 1))

        for d, aid, w in rows:
            by_animal[aid].append((d, w))

        def to_y(weight):
            ratio = (weight - min_w) / (max_w - min_w)
            return top + plot_h - (ratio * plot_h)

        for i in range(6):
            value = min_w + (max_w - min_w) * (i / 5)
            y = to_y(value)
            canvas.create_line(left, y, left + plot_w, y, fill=grid_color, dash=(2, 4))
            canvas.create_text(left - 8, y, text=f"{value:.1f}", anchor="e", fill=muted_text)

        max_labels = 8
        if len(dates) <= max_labels:
            label_dates = dates
        else:
            step = max(1, len(dates) // max_labels)
            label_dates = dates[::step]
            if dates[-1] not in label_dates:
                label_dates.append(dates[-1])
        for d in label_dates:
            x = x_map[d]
            canvas.create_line(x, top, x, top + plot_h, fill=grid_color, dash=(2, 4))
            canvas.create_line(x, top + plot_h, x, top + plot_h + 4, fill=muted_text)
            try:
                label = datetime.strptime(str(d), "%Y-%m-%d").strftime("%b %d")
            except Exception:
                label = str(d)
            canvas.create_text(x, top + plot_h + 10, text=label, anchor="n", fill=muted_text)

        ordered_animals = [aid for aid, _pts in sorted(by_animal.items())]
        animal_index = {aid: idx for idx, aid in enumerate(ordered_animals)}

        for idx, (animal_id, points) in enumerate(sorted(by_animal.items())):
            color = self.chart_colors[idx % len(self.chart_colors)]
            points = sorted(points, key=lambda p: p[0])
            coords = []
            for point_idx, (d, w) in enumerate(points):
                x = x_map[d]
                if len(dates) == 1:
                    offset = (animal_index[animal_id] - (len(ordered_animals) - 1) / 2) * 14
                    x = x + offset
                y = to_y(w)
                coords.extend([x, y])
                canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)
                if point_idx == len(points) - 1:
                    label_dy = -8
                    if len(dates) == 1:
                        label_dy = -12 + (animal_index[animal_id] * 10)
                    canvas.create_text(x + 6, y + label_dy, text=f"{w:.1f}", anchor="w", fill=color, font=("Arial", 9))
            if len(coords) >= 4 and len(dates) > 1:
                canvas.create_line(*coords, fill=color, width=2, smooth=False)

    def dismiss_export_notice(self):
        if self._export_notice is not None:
            self._export_notice.destroy()
            self._export_notice = None

    def show_export_success_notice(self):
        """Shows a persistent in-page success notification until dismissed or navigated away."""
        if self._export_notice is None:
            container = CTkFrame(
                self,
                corner_radius=12,
                fg_color=("#ecfdf5", "#064e3b"),
                border_width=1,
                border_color=("#10b981", "#10b981"),
            )
            container.place(relx=0.5, rely=0.1, anchor=CENTER)

            label = CTkLabel(
                container,
                text="Export to CSV successful!",
                text_color=("#065f46", "white"),
                font=("Segoe UI Semibold", 14),
            )
            label.grid(row=0, column=0, padx=(12, 10), pady=8, sticky="w")

            dismiss_button = CTkButton(
                container,
                text="Dismiss",
                command=self.dismiss_export_notice,
                width=90,
                height=32,
                font=("Segoe UI Semibold", 13),
                fg_color="#2563eb",
                hover_color="#1e40af",
                text_color="white",
            )
            dismiss_button.grid(row=0, column=1, padx=(0, 10), pady=6, sticky="e")

            container.grid_columnconfigure(0, weight=1)
            self._export_notice = container
        else:
            for child in self._export_notice.winfo_children():
                if isinstance(child, CTkLabel):
                    child.configure(text="Export to CSV successful!")
                    break

    def export_to_csv(self):
        """Handles exporting the database to CSV files."""
        if not self.db_file or not os.path.exists(self.db_file):
            self.show_notification("Error", "Database file not found.")
            return

        save_dir = filedialog.askdirectory(title="Select Directory to Save CSV Files")
        if not save_dir:
            return

        try:
            db = ExperimentDatabase(self.db_file)
            db.export_to_single_formatted_csv(save_dir)
            AudioManager.play(SUCCESS_SOUND)
            self.show_export_success_notice()
        except Exception:
            self.show_notification("Error", "Export to CSV failed")

    def raise_frame(self):
        """Raise frame and refresh displayed data."""
        super().raise_frame()
        self.dismiss_export_notice()
        self.refresh_analysis_view()

    def show_notification(self, title, message):
        """Displays a notification window."""
        notification = CTkToplevel(self)
        notification.title(title)
        notification.geometry("400x200")
        notification.resizable(False, False)

        label = CTkLabel(notification, text=message, font=("Arial", 20), pady=20)
        label.pack(pady=10)

        ok_button = CTkButton(
            notification,
            text="OK",
            command=notification.destroy,
            width=100,
            height=50,
            font=("Arial", 16),
        )
        ok_button.pack(pady=20)

        notification.transient(self)
        notification.grab_set()
