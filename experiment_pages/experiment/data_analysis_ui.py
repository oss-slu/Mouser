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
        self.sidebar.grid_rowconfigure(2, weight=1)

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
            text="Export and visualize weight trends",
            font=CTkFont("Segoe UI", 12),
            text_color=self._palette["muted_text"],
        ).pack(anchor="w", pady=(2, 0))

        # Summary tiles (Animals / Dates / Points / Latest date)
        stats_row = CTkFrame(self.left_panel, fg_color="transparent")
        stats_row.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        for col in range(4):
            stats_row.grid_columnconfigure(col, weight=1, uniform="stats")

        def _stat_tile(col_index, title, value_color, tile_bg, tile_border):
            tile = CTkFrame(
                stats_row,
                fg_color=_pick(tile_bg),
                corner_radius=14,
                border_width=1,
                border_color=_pick(tile_border),
            )
            tile.grid(row=0, column=col_index, sticky="ew", padx=6, pady=0)
            CTkLabel(
                tile,
                text=title,
                font=CTkFont("Segoe UI", 12),
                text_color=self._palette["muted_text"],
                anchor="w",
            ).pack(fill="x", padx=14, pady=(12, 0))
            value_label = CTkLabel(
                tile,
                text="--",
                font=CTkFont("Segoe UI Semibold", 26),
                text_color=value_color,
                anchor="w",
            )
            value_label.pack(fill="x", padx=14, pady=(2, 12))
            return value_label

        self.animals_value = _stat_tile(
            0,
            "Animals",
            _pick(self._palette["text"]),
            ("#f1f5f9", "#0f172a"),
            ("#94a3b8", "#475569"),
        )
        self.dates_value = _stat_tile(
            1,
            "Dates",
            ("#2563eb", "#60a5fa"),
            ("#eef2ff", "#111827"),
            ("#818cf8", "#818cf8"),
        )
        self.points_value = _stat_tile(
            2,
            "Points",
            ("#16a34a", "#34d399"),
            ("#ecfdf5", "#042f2e"),
            ("#34d399", "#34d399"),
        )
        self.latest_value = _stat_tile(
            3,
            "Latest",
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
            max_date = max(datetime.strptime(r[0], "%Y-%m-%d").date() for r in rows)
        except Exception:
            return rows
        min_date = max_date - timedelta(days=int(self._range_days) - 1)
        filtered = []
        for d, aid, val in rows:
            try:
                row_date = datetime.strptime(d, "%Y-%m-%d").date()
            except Exception:
                continue
            if row_date >= min_date:
                filtered.append((d, aid, val))
        return filtered

    def refresh_analysis_view(self, redraw_only=False):
        rows = self._load_measurement_rows(getattr(self, "_selected_measurement_id", 1))
        rows = self._filter_rows_by_range(rows)
        if not redraw_only:
            self._populate_table(rows)
            self._populate_legend(rows)
            animal_count = len({r[1] for r in rows})
            date_count = len({r[0] for r in rows})
            points_count = len(rows)
            self.summary_label.configure(text="")
            latest_date = max((r[0] for r in rows), default="-")
            try:
                if hasattr(self, "animals_value") and self.animals_value:
                    self.animals_value.configure(text=str(animal_count))
                if hasattr(self, "dates_value") and self.dates_value:
                    self.dates_value.configure(text=str(date_count))
                if hasattr(self, "points_value") and self.points_value:
                    self.points_value.configure(text=str(points_count))
                if hasattr(self, "latest_value") and self.latest_value:
                    self.latest_value.configure(text=str(latest_date))
            except Exception:
                pass
        self._draw_trend_chart(rows)

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
            for idx, d in enumerate(dates):
                x_map[d] = left + (idx * plot_w / (len(dates) - 1))

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
            label = f"d{date_index.get(d, 0) + 1}"
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
