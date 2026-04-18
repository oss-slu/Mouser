"""Tumor-level analysis and export UI."""
import os
from collections import defaultdict
from tkinter import filedialog

from customtkinter import (
    CTkButton,
    CTkCanvas,
    CTkFrame,
    CTkLabel,
    CTkScrollbar,
    CTkOptionMenu,
    CTkCheckBox,
    CTkEntry,
    CTkToplevel,
    BooleanVar,
    CENTER,
)
from tkinter.ttk import Treeview, Style

from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage, get_ui_metrics
from shared.analysis_utils import (
    calc_volume,
    mean,
    median,
    trimmed_mean,
    geometric_mean,
    trimmed_geometric_mean,
    stddev_sample,
    survival_percent,
    box_values,
    STATUS_MEASURED,
    STATUS_DEAD,
    STATUS_CENSORED,
    STATUS_SKIPPED,
)


STAT_METHODS = [
    "Mean",
    "Median",
    "Trimmed Mean",
    "Geometric Mean",
    "Trimmed Geometric Mean",
    "StdDev",
    "Survival",
    "Box",
]

DATA_SOURCES = [
    "Volumes",
    "Fold Increase",
]


class TumorDataAnalysisUI(MouserPage):
    """Tumor analysis & export."""

    def __init__(self, parent, prev_page=None, db_file=None):
        super().__init__(parent, "Tumor Analysis", prev_page)
        ui = get_ui_metrics()
        self.db_file = db_file
        self.ui = ui
        self.chart_colors = [
            "#2563eb",
            "#dc2626",
            "#059669",
            "#d97706",
            "#7c3aed",
            "#0891b2",
            "#be123c",
        ]

        self.db = ExperimentDatabase(self.db_file)
        self.calc_method = self.db.get_calc_method()
        self.groups = self.db.get_groups()
        self.group_ids = [row[0] for row in self.db._c.execute("SELECT group_id FROM groups ORDER BY group_id").fetchall()]
        self.group_name_by_id = {}
        for idx, gid in enumerate(self.group_ids):
            if idx < len(self.groups):
                self.group_name_by_id[gid] = self.groups[idx]
        self.stat_method = STAT_METHODS[0]
        self.data_source = DATA_SOURCES[0]
        self.show_error_bars = False
        self.included_group_ids = set(self.group_ids)
        self.excluded_tumor_ids = set()

        self.main_frame = CTkFrame(
            self,
            corner_radius=16,
            fg_color=("white", "#27272a"),
            border_width=1,
            border_color="#d1d5db",
        )
        self.main_frame.place(relx=0.53, rely=0.58, relwidth=0.84, relheight=0.80, anchor=CENTER)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=3)
        self.main_frame.grid_rowconfigure(3, weight=4)

        title_label = CTkLabel(
            self.main_frame,
            text="Tumor Analysis & Export",
            font=("Arial", 24, "bold"),
            text_color=("#111827", "#e5e7eb"),
        )
        title_label.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        controls = CTkFrame(self.main_frame, fg_color="transparent")
        controls.grid(row=1, column=0, padx=16, pady=(2, 8), sticky="ew")
        controls.grid_columnconfigure(10, weight=1)

        self.stat_menu = CTkOptionMenu(
            controls,
            values=STAT_METHODS,
            command=self._on_stat_change,
            width=200,
        )
        self.stat_menu.set(self.stat_method)
        self.stat_menu.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")

        self.source_menu = CTkOptionMenu(
            controls,
            values=DATA_SOURCES,
            command=self._on_source_change,
            width=160,
        )
        self.source_menu.set(self.data_source)
        self.source_menu.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")

        CTkLabel(controls, text="Survival Limit").grid(row=0, column=2, padx=(6, 2), pady=4, sticky="e")
        self.survival_entry = CTkEntry(controls, width=100)
        self.survival_entry.insert(0, "1000")
        self.survival_entry.grid(row=0, column=3, padx=(0, 10), pady=4, sticky="w")

        self.error_bar_toggle = CTkCheckBox(
            controls,
            text="Show Error Bars",
            command=self._on_error_bar_toggle,
        )
        self.error_bar_toggle.grid(row=0, column=4, padx=(0, 10), pady=4, sticky="w")

        self.export_button = CTkButton(
            controls,
            text="Export Raw CSV",
            command=self.export_raw_csv,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.export_button.grid(row=0, column=5, padx=(0, 10), pady=4, sticky="w")

        self.export_stats_button = CTkButton(
            controls,
            text="Export Stats CSV",
            command=self.export_stats_csv,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.export_stats_button.grid(row=0, column=6, padx=(0, 10), pady=4, sticky="w")

        self.refresh_button = CTkButton(
            controls,
            text="Refresh View",
            command=self.refresh_analysis_view,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.refresh_button.grid(row=0, column=7, padx=(0, 10), pady=4, sticky="w")

        self.save_graph_button = CTkButton(
            controls,
            text="Save Graph",
            command=self.save_graph_settings,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.save_graph_button.grid(row=0, column=8, padx=(0, 10), pady=4, sticky="w")

        self.load_graph_button = CTkButton(
            controls,
            text="Load Graph",
            command=self.load_graph_settings,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.load_graph_button.grid(row=0, column=9, padx=(0, 10), pady=4, sticky="w")

        self.summary_label = CTkLabel(
            controls,
            text="",
            font=("Arial", 14),
            text_color=("#374151", "#d1d5db"),
        )
        self.summary_label.grid(row=0, column=10, padx=8, pady=4, sticky="e")

        self.filter_groups_button = CTkButton(
            controls,
            text="Filter Groups",
            command=self.open_group_filter,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.filter_groups_button.grid(row=1, column=0, padx=(0, 10), pady=4, sticky="w")

        self.filter_tumors_button = CTkButton(
            controls,
            text="Filter Tumors",
            command=self.open_tumor_filter,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.filter_tumors_button.grid(row=1, column=1, padx=(0, 10), pady=4, sticky="w")

        self.export_excel_button = CTkButton(
            controls,
            text="Export Excel",
            command=self.export_excel,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.export_excel_button.grid(row=1, column=2, padx=(0, 10), pady=4, sticky="w")

        self._build_table_section()
        self._build_chart_section()
        self.refresh_analysis_view()

    def _build_table_section(self):
        table_card = CTkFrame(
            self.main_frame,
            fg_color=("white", "#18181b"),
            corner_radius=12,
            border_width=1,
            border_color="#d1d5db",
        )
        table_card.grid(row=2, column=0, padx=16, pady=(4, 10), sticky="nsew")
        table_card.grid_columnconfigure(0, weight=1)
        table_card.grid_rowconfigure(0, weight=1)

        style = Style()
        style.configure(
            "TumorExport.Treeview",
            font=("Arial", self.ui["table_font_size"]),
            rowheight=self.ui["table_row_height"] + 2,
        )
        style.configure("TumorExport.Treeview.Heading", font=("Arial", self.ui["table_font_size"], "bold"))
        style.map("TumorExport.Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", "#111827")])

        self.table = Treeview(
            table_card,
            columns=("date", *self.groups),
            show="headings",
            style="TumorExport.Treeview",
            selectmode="browse",
        )
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar = CTkScrollbar(table_card, orientation="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _build_chart_section(self):
        chart_card = CTkFrame(
            self.main_frame,
            fg_color=("white", "#18181b"),
            corner_radius=12,
            border_width=1,
            border_color="#d1d5db",
        )
        chart_card.grid(row=3, column=0, padx=16, pady=(0, 14), sticky="nsew")
        chart_card.grid_columnconfigure(0, weight=1)
        chart_card.grid_rowconfigure(0, weight=1)

        self.chart_canvas = CTkCanvas(chart_card, highlightthickness=0, bg="white")
        self.chart_canvas.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.chart_canvas.bind("<Configure>", lambda _e: self.refresh_analysis_view(redraw_only=True))

    def _on_stat_change(self, value):
        self.stat_method = value
        self.refresh_analysis_view()

    def _on_source_change(self, value):
        self.data_source = value
        self.refresh_analysis_view()

    def _on_error_bar_toggle(self):
        self.show_error_bars = bool(self.error_bar_toggle.get())
        self.refresh_analysis_view()

    def _load_measurements(self):
        self.db._c.execute(
            """
            SELECT t.group_id, t.animal_id, t.tumor_id, t.tumor_index,
                   m.date_measured, m.length, m.width, m.status
            FROM tumor_measurements m
            JOIN tumors t ON t.tumor_id = m.tumor_id
            ORDER BY m.date_measured ASC, t.measurement_order ASC
            """
        )
        rows = self.db._c.fetchall()
        filtered = []
        for row in rows:
            group_id = row[0]
            tumor_id = row[2]
            if self.included_group_ids and group_id not in self.included_group_ids:
                continue
            if tumor_id in self.excluded_tumor_ids:
                continue
            filtered.append(row)
        return filtered

    def _compute_stats(self):
        rows = self._load_measurements()
        if not rows:
            return [], [], []
        dates = sorted({r[4] for r in rows})
        group_ids = self.db._c.execute("SELECT group_id FROM groups ORDER BY group_id").fetchall()
        group_ids = [gid[0] for gid in group_ids]
        group_ids = [gid for gid in group_ids if gid in self.included_group_ids]
        group_names = [self.group_name_by_id.get(gid, str(gid)) for gid in group_ids]
        self.active_groups = group_names

        data = {d: {g: [] for g in group_ids} for d in dates}
        source = self.data_source
        if self.stat_method == "Survival":
            source = "Volumes"
        baseline = {}
        for group_id, _animal_id, tumor_id, _tumor_index, date_measured, length, width, status in rows:
            normalized_status = status or STATUS_MEASURED
            if normalized_status != STATUS_MEASURED:
                continue
            volume = calc_volume(self.calc_method, length, width)
            if volume is None:
                continue
            if tumor_id not in baseline:
                baseline[tumor_id] = volume

        for group_id, _animal_id, tumor_id, _tumor_index, date_measured, length, width, status in rows:
            normalized_status = status or STATUS_MEASURED
            volume = calc_volume(self.calc_method, length, width) if normalized_status == STATUS_MEASURED else None
            if source == "Fold Increase" and normalized_status == STATUS_MEASURED:
                base = baseline.get(tumor_id)
                if base and base > 0:
                    volume = volume / base
                else:
                    volume = None
            record = {"volume": volume, "status": normalized_status}
            data[date_measured][group_id].append(record)

        stats_rows = []
        error_rows = []
        survival_prev = {g: None for g in group_ids}
        for date_measured in dates:
            row = {"date": date_measured}
            error_row = {"date": date_measured}
            for idx, group_id in enumerate(group_ids):
                records = data[date_measured][group_id]
                if self.stat_method == "Survival":
                    try:
                        limit = float(self.survival_entry.get())
                    except ValueError:
                        limit = None
                    value = survival_percent(records, limit, survival_prev[group_id])
                    survival_prev[group_id] = value if value is not None else survival_prev[group_id]
                else:
                    value = self._stat_value(records)
                row[group_names[idx]] = value
                error_row[group_names[idx]] = stddev_sample(records)
            stats_rows.append(row)
            error_rows.append(error_row)
        return stats_rows, dates, error_rows

    def _stat_value(self, records):
        if self.stat_method == "Mean":
            return mean(records)
        if self.stat_method == "Median":
            return median(records)
        if self.stat_method == "Trimmed Mean":
            return trimmed_mean(records)
        if self.stat_method == "Geometric Mean":
            return geometric_mean(records)
        if self.stat_method == "Trimmed Geometric Mean":
            return trimmed_geometric_mean(records)
        if self.stat_method == "StdDev":
            return stddev_sample(records)
        if self.stat_method == "Survival":
            try:
                limit = float(self.survival_entry.get())
            except ValueError:
                limit = None
            return survival_percent(records, limit)
        if self.stat_method == "Box":
            return box_values(records)
        return mean(records)

    def refresh_analysis_view(self, redraw_only=False):
        stats_rows, dates, error_rows = self._compute_stats()
        if not redraw_only:
            self._populate_table(stats_rows)
            self.summary_label.configure(text=f"Dates: {len(dates)} | Groups: {len(getattr(self, 'active_groups', []))}")
        self._draw_chart(stats_rows, dates, error_rows)

    def _populate_table(self, stats_rows):
        self.table.delete(*self.table.get_children())
        columns = ("date", *getattr(self, "active_groups", self.groups))
        self.table.configure(columns=columns)
        for col in columns:
            self.table.heading(col, text=col, anchor="center")
            self.table.column(col, width=140, anchor="center", stretch=True)

        for row in stats_rows:
            values = [row.get("date")]
            for group_name in getattr(self, "active_groups", self.groups):
                val = row.get(group_name)
                if isinstance(val, list):
                    values.append(",".join([f"{v:.2f}" for v in val]))
                elif val is None:
                    values.append("")
                else:
                    values.append(f"{val:.2f}")
            self.table.insert("", "end", values=values)

    def _draw_chart(self, stats_rows, dates, error_rows):
        self.chart_canvas.delete("all")
        if not stats_rows or not dates:
            return

        width = self.chart_canvas.winfo_width()
        height = self.chart_canvas.winfo_height()
        padding = 40

        # Build series
        series = defaultdict(list)
        for row in stats_rows:
            for group in getattr(self, "active_groups", self.groups):
                val = row.get(group)
                if isinstance(val, list) or val is None:
                    series[group].append(None)
                else:
                    series[group].append(val)

        # Determine Y range
        y_values = [v for group_vals in series.values() for v in group_vals if isinstance(v, (int, float))]
        if not y_values:
            return
        y_min, y_max = min(y_values), max(y_values)
        if y_min == y_max:
            y_min -= 1
            y_max += 1

        def x_for_idx(i):
            if len(dates) == 1:
                return padding + (width - 2 * padding) / 2
            return padding + i * (width - 2 * padding) / (len(dates) - 1)

        def y_for_val(val):
            return height - padding - ((val - y_min) / (y_max - y_min)) * (height - 2 * padding)

        # Axes
        self.chart_canvas.create_line(padding, padding, padding, height - padding, fill="#111827")
        self.chart_canvas.create_line(padding, height - padding, width - padding, height - padding, fill="#111827")

        for s_idx, (group, values) in enumerate(series.items()):
            color = self.chart_colors[s_idx % len(self.chart_colors)]
            last_point = None
            for i, val in enumerate(values):
                if val is None:
                    continue
                x = x_for_idx(i)
                y = y_for_val(val)
                self.chart_canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline=color)
                if last_point:
                    if self.stat_method == "Survival":
                        # Step function: horizontal then vertical
                        self.chart_canvas.create_line(last_point[0], last_point[1], x, last_point[1], fill=color, width=2)
                        self.chart_canvas.create_line(x, last_point[1], x, y, fill=color, width=2)
                    else:
                        self.chart_canvas.create_line(last_point[0], last_point[1], x, y, fill=color, width=2)
                if self.show_error_bars and error_rows and self.stat_method in (
                    "Mean",
                    "Geometric Mean",
                    "Trimmed Mean",
                    "Trimmed Geometric Mean",
                ):
                    err = error_rows[i].get(group)
                    if err is not None:
                        y_low = y_for_val(val - err)
                        y_high = y_for_val(val + err)
                        self.chart_canvas.create_line(x, y_low, x, y_high, fill=color, width=1)
                        self.chart_canvas.create_line(x - 4, y_low, x + 4, y_low, fill=color, width=1)
                        self.chart_canvas.create_line(x - 4, y_high, x + 4, y_high, fill=color, width=1)
                last_point = (x, y)
            # Legend
            self.chart_canvas.create_text(
                width - padding,
                padding + 15 * s_idx,
                text=group,
                fill=color,
                anchor="ne",
                font=("Arial", 10),
            )

    def export_raw_csv(self):
        directory = filedialog.askdirectory(title="Select export directory")
        if not directory:
            return
        out_path = os.path.join(directory, "tumor_raw_export.csv")
        self.db._c.execute(
            """
            SELECT t.group_id, g.name as group_name, t.animal_id, t.tumor_index, t.location_label,
                   m.date_measured, m.length, m.width, m.status
            FROM tumor_measurements m
            JOIN tumors t ON t.tumor_id = m.tumor_id
            JOIN groups g ON g.group_id = t.group_id
            ORDER BY m.date_measured ASC, t.measurement_order ASC
            """
        )
        rows = self.db._c.fetchall()
        headers = [
            "group_id",
            "group_name",
            "animal_id",
            "tumor_index",
            "location_label",
            "date_measured",
            "length",
            "width",
            "status",
        ]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(",".join(headers) + "\n")
            for row in rows:
                f.write(",".join([str(item) if item is not None else "" for item in row]) + "\n")

    def export_stats_csv(self):
        directory = filedialog.askdirectory(title="Select export directory")
        if not directory:
            return
        out_path = os.path.join(directory, "tumor_stats_export.csv")
        stats_rows, _dates, _errors = self._compute_stats()
        active_groups = getattr(self, "active_groups", self.groups)
        headers = ["date", *active_groups]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(",".join(headers) + "\n")
            for row in stats_rows:
                values = [row.get("date")]
                for group_name in active_groups:
                    val = row.get(group_name)
                    if isinstance(val, list):
                        values.append("|".join([f"{v:.4f}" for v in val]))
                    elif val is None:
                        values.append("")
                    else:
                        values.append(f"{val:.4f}")
                f.write(",".join(values) + "\n")

    def save_graph_settings(self):
        from tkinter.filedialog import asksaveasfilename
        import json

        path = asksaveasfilename(
            title="Save Graph Settings",
            defaultextension=".mgs",
            filetypes=[("Mouser Graph Settings", "*.mgs")],
        )
        if not path:
            return
        settings = {
            "stat_method": self.stat_method,
            "data_source": self.data_source,
            "show_error_bars": self.show_error_bars,
            "survival_limit": self.survival_entry.get(),
            "included_group_ids": sorted(list(self.included_group_ids)),
            "excluded_tumor_ids": sorted(list(self.excluded_tumor_ids)),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f)

    def load_graph_settings(self):
        from tkinter.filedialog import askopenfilename
        import json

        path = askopenfilename(
            title="Load Graph Settings",
            filetypes=[("Mouser Graph Settings", "*.mgs")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception:
            return

        stat_method = settings.get("stat_method", self.stat_method)
        data_source = settings.get("data_source", self.data_source)
        show_error_bars = settings.get("show_error_bars", self.show_error_bars)
        survival_limit = settings.get("survival_limit", self.survival_entry.get())
        included_group_ids = settings.get("included_group_ids", list(self.included_group_ids))
        excluded_tumor_ids = settings.get("excluded_tumor_ids", list(self.excluded_tumor_ids))

        if stat_method in STAT_METHODS:
            self.stat_method = stat_method
            self.stat_menu.set(stat_method)
        if data_source in DATA_SOURCES:
            self.data_source = data_source
            self.source_menu.set(data_source)
        self.show_error_bars = bool(show_error_bars)
        self.error_bar_toggle.select() if self.show_error_bars else self.error_bar_toggle.deselect()
        self.survival_entry.delete(0, "end")
        self.survival_entry.insert(0, str(survival_limit))
        if included_group_ids:
            self.included_group_ids = set(included_group_ids)
        if excluded_tumor_ids is not None:
            self.excluded_tumor_ids = set(excluded_tumor_ids)
        self.refresh_analysis_view()

    def open_group_filter(self):
        dialog = CTkToplevel(self)
        dialog.title("Filter Groups")
        dialog.geometry("420x420")
        dialog.resizable(False, False)

        vars_by_group = {}
        for idx, gid in enumerate(self.group_ids):
            name = self.group_name_by_id.get(gid, str(gid))
            var = BooleanVar(value=(gid in self.included_group_ids))
            vars_by_group[gid] = var
            chk = CTkCheckBox(dialog, text=name, variable=var)
            chk.grid(row=idx, column=0, sticky="w", padx=20, pady=6)

        def apply_filters():
            self.included_group_ids = {gid for gid, var in vars_by_group.items() if var.get()}
            if not self.included_group_ids:
                self.included_group_ids = set(self.group_ids)
            dialog.destroy()
            self.refresh_analysis_view()

        CTkButton(dialog, text="Apply", command=apply_filters).grid(row=len(self.group_ids) + 1, column=0, pady=12)

    def open_tumor_filter(self):
        dialog = CTkToplevel(self)
        dialog.title("Filter Tumors")
        dialog.geometry("520x520")
        dialog.resizable(False, False)

        self.db._c.execute(
            '''
            SELECT tumor_id, animal_id, tumor_index, location_label, group_id
            FROM tumors
            ORDER BY group_id, animal_id, tumor_index
            '''
        )
        tumors = self.db._c.fetchall()
        vars_by_tumor = {}
        for idx, (tumor_id, animal_id, tumor_index, label, group_id) in enumerate(tumors):
            group_name = self.group_name_by_id.get(group_id, str(group_id))
            display = f"G{group_name} A{animal_id} T{tumor_index} ({label})"
            var = BooleanVar(value=(tumor_id not in self.excluded_tumor_ids))
            vars_by_tumor[tumor_id] = var
            chk = CTkCheckBox(dialog, text=display, variable=var)
            chk.grid(row=idx, column=0, sticky="w", padx=16, pady=4)

        def apply_filters():
            self.excluded_tumor_ids = {tid for tid, var in vars_by_tumor.items() if not var.get()}
            dialog.destroy()
            self.refresh_analysis_view()

        CTkButton(dialog, text="Apply", command=apply_filters).grid(row=len(tumors) + 1, column=0, pady=12)

    def export_excel(self):
        import pandas as pd
        from openpyxl.chart import LineChart, Reference

        directory = filedialog.askdirectory(title="Select export directory")
        if not directory:
            return
        out_path = os.path.join(directory, "tumor_analysis.xlsx")

        # Metadata
        self.db._c.execute("SELECT * FROM experiment")
        experiment = self.db._c.fetchone()
        exp_columns = [col[1] for col in self.db._c.execute("PRAGMA table_info(experiment)")]
        meta_df = pd.DataFrame([experiment], columns=exp_columns)

        # Raw measurements
        self.db._c.execute(
            """
            SELECT g.name as group_name, t.animal_id, t.tumor_index, t.location_label,
                   m.date_measured, m.length, m.width, m.status
            FROM tumor_measurements m
            JOIN tumors t ON t.tumor_id = m.tumor_id
            JOIN groups g ON g.group_id = t.group_id
            ORDER BY m.date_measured ASC, t.measurement_order ASC
            """
        )
        raw_rows = self.db._c.fetchall()
        raw_df = pd.DataFrame(
            raw_rows,
            columns=[
                "group_name",
                "animal_id",
                "tumor_index",
                "location_label",
                "date_measured",
                "length",
                "width",
                "status",
            ],
        )
        raw_df["volume"] = raw_df.apply(
            lambda r: calc_volume(self.calc_method, r["length"], r["width"]) if r["status"] == STATUS_MEASURED else None,
            axis=1,
        )

        stats_rows, _dates, _errors = self._compute_stats()
        stats_df = pd.DataFrame(stats_rows)

        with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
            meta_df.to_excel(writer, sheet_name="Metadata", index=False)
            raw_df.to_excel(writer, sheet_name="RawMeasurements", index=False)
            stats_df.to_excel(writer, sheet_name="Statistics", index=False)

            ws = writer.sheets.get("Statistics")
            if ws and stats_df.shape[1] > 1:
                chart = LineChart()
                chart.title = f"{self.stat_method} ({self.data_source})"
                chart.y_axis.title = self.data_source
                chart.x_axis.title = "Date"

                data_ref = Reference(ws, min_col=2, min_row=1, max_col=stats_df.shape[1], max_row=stats_df.shape[0] + 1)
                cats_ref = Reference(ws, min_col=1, min_row=2, max_row=stats_df.shape[0] + 1)
                chart.add_data(data_ref, titles_from_data=True)
                chart.set_categories(cats_ref)
                ws.add_chart(chart, "H2")
