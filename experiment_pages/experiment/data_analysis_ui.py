#pylint: skip-file
"""Data exporting and analysis page."""

import os
from collections import defaultdict
from tkinter import filedialog
from tkinter.ttk import Treeview, Style

from customtkinter import (
    CTkButton,
    CTkCanvas,
    CTkFrame,
    CTkLabel,
    CTkScrollbar,
    CTkToplevel,
    CENTER,
)

from shared.tk_models import MouserPage, get_ui_metrics
from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND


class DataAnalysisUI(MouserPage):
    """Data exporting UI with table and weight trend graph."""

    def __init__(self, parent, prev_page=None, db_file=None):
        super().__init__(parent, "Data Exporting", prev_page)
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

        self.main_frame = CTkFrame(
            self,
            corner_radius=16,
            fg_color=("white", "#27272a"),
            border_width=1,
            border_color="#d1d5db",
        )
        self.main_frame.place(relx=0.53, rely=0.58, relwidth=0.82, relheight=0.78, anchor=CENTER)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=3)
        self.main_frame.grid_rowconfigure(3, weight=4)

        title_label = CTkLabel(
            self.main_frame,
            text="Data Analysis & Export",
            font=("Arial", 24, "bold"),
            text_color=("#111827", "#e5e7eb"),
        )
        title_label.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="w")

        controls = CTkFrame(self.main_frame, fg_color="transparent")
        controls.grid(row=1, column=0, padx=16, pady=(2, 8), sticky="ew")
        controls.grid_columnconfigure(2, weight=1)

        self.export_button = CTkButton(
            controls,
            text="Export Data to CSV",
            command=self.export_to_csv,
            width=ui["action_width"],
            height=ui["action_height"],
            font=("Segoe UI Semibold", ui["action_font_size"]),
            fg_color="#2563eb",
            hover_color="#1e40af",
            text_color="white",
        )
        self.export_button.grid(row=0, column=0, padx=(0, 10), pady=4, sticky="w")

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
        self.refresh_button.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")

        self.summary_label = CTkLabel(
            controls,
            text="",
            font=("Arial", 14),
            text_color=("#374151", "#d1d5db"),
        )
        self.summary_label.grid(row=0, column=2, padx=8, pady=4, sticky="e")

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
            "Export.Treeview",
            font=("Arial", self.ui["table_font_size"]),
            rowheight=self.ui["table_row_height"] + 2,
        )
        style.configure("Export.Treeview.Heading", font=("Arial", self.ui["table_font_size"], "bold"))
        style.map("Export.Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", "#111827")])

        self.table = Treeview(
            table_card,
            columns=("date", "animal_id", "weight"),
            show="headings",
            style="Export.Treeview",
            selectmode="browse",
        )
        self.table.heading("date", text="Date", anchor="center")
        self.table.heading("animal_id", text="Animal ID", anchor="center")
        self.table.heading("weight", text="Weight", anchor="center")
        self.table.column("date", width=220, anchor="center", stretch=True)
        self.table.column("animal_id", width=170, anchor="center", stretch=True)
        self.table.column("weight", width=170, anchor="center", stretch=True)
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

    def _load_weight_rows(self):
        if not self.db_file or not os.path.exists(self.db_file):
            return []
        db = ExperimentDatabase(self.db_file)
        db._c.execute(
            """
            SELECT DATE(timestamp) as measurement_date, animal_id, value
            FROM animal_measurements
            WHERE value IS NOT NULL
              AND (measurement_id IS NULL OR measurement_id = 1)
            ORDER BY measurement_date ASC, animal_id ASC
            """
        )
        card.grid(row=1, column=0, padx=80, pady=20, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0, 1, 2), weight=1)

        # --- Description ---
        desc_font = CTkFont("Segoe UI", 18)
        CTkLabel(
            card,
            text="Analyze and visualize your collected experiment data below.",
            font=desc_font,
            text_color=("#4b5563", "#d4d4d8"),
            wraplength=700,
            justify="center"
        ).grid(row=0, column=0, pady=(20, 10))

        # --- Placeholder for Charts/Plots ---
        CTkLabel(
            card,
            text="[Charts and Data Visualizations Placeholder]",
            font=CTkFont("Segoe UI Italic", 16),
            text_color=("#6b7280", "#a1a1aa")
        ).grid(row=1, column=0, pady=(20, 10))

        # --- Buttons Section ---
        button_font = CTkFont("Segoe UI Semibold", 20)
        button_style = {
            "corner_radius": 12,
            "height": 50,
            "width": 350,
            "font": button_font,
            "text_color": "white",
            "fg_color": "#2563eb",
            "hover_color": "#1e40af"
        }

        CTkButton(
            card,
            text="Export Results",
            command=self.export_data,
            **button_style
        ).grid(row=2, column=0, pady=(10, 15))

        CTkButton(
            card,
            text="Back to menu",
            command=self.back_to_menu,
            **button_style
        ).grid(row=3, column=0, pady=(10, 25))

    # --- Functional Logic (unchanged) ---
    def export_data(self):
        """Handles exporting analyzed data to file."""
        print("Exporting analyzed results...")

    def back_to_menu(self):
        """Return to experiment menu."""
        # pylint: disable=import-outside-toplevel
        from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
        page = ExperimentMenuUI(self.root, self.file_path, self)
        page.raise_frame()
        rows = db._c.fetchall()
        return [(str(d), int(aid), float(val)) for d, aid, val in rows]

    def refresh_analysis_view(self, redraw_only=False):
        rows = self._load_weight_rows()
        if not redraw_only:
            self._populate_table(rows)
            animal_count = len({r[1] for r in rows})
            date_count = len({r[0] for r in rows})
            self.summary_label.configure(text=f"Animals: {animal_count} | Dates: {date_count} | Points: {len(rows)}")
        self._draw_trend_chart(rows)

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
        for animal_id in animal_ids:
            row_values = [animal_id]
            for measurement_date in date_list:
                value = lookup.get((measurement_date, animal_id))
                row_values.append(f"{value:.2f}" if value is not None else "-")
            self.table.insert("", "end", values=tuple(row_values))

    def _draw_trend_chart(self, rows):
        canvas = self.chart_canvas
        canvas.delete("all")
        width = max(canvas.winfo_width(), 200)
        height = max(canvas.winfo_height(), 180)
        left, right, top, bottom = 96, 190, 18, 64
        plot_w = max(width - left - right, 50)
        plot_h = max(height - top - bottom, 50)

        canvas.create_rectangle(left, top, left + plot_w, top + plot_h, outline="#9ca3af", width=1)
        canvas.create_text(24, top + plot_h / 2, text="Weight of Animal", anchor="center", angle=90, fill="#111827")
        canvas.create_text(left + plot_w / 2, height - 16, text="Date", fill="#111827")

        if not rows:
            canvas.create_text(width / 2, height / 2, text="No data available yet.", fill="#6b7280")
            return

        dates = sorted({row[0] for row in rows})
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
            canvas.create_line(left, y, left + plot_w, y, fill="#e5e7eb")
            canvas.create_text(left - 8, y, text=f"{value:.1f}", anchor="e", fill="#4b5563")

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
            canvas.create_line(x, top + plot_h, x, top + plot_h + 4, fill="#6b7280")
            if len(dates) <= 6:
                canvas.create_text(x, top + plot_h + 10, text=d, anchor="n", fill="#4b5563")
            else:
                canvas.create_text(x, top + plot_h + 14, text=d, angle=35, anchor="w", fill="#4b5563")

        ordered_animals = [aid for aid, _pts in sorted(by_animal.items())]
        animal_index = {aid: idx for idx, aid in enumerate(ordered_animals)}

        legend_x = left + plot_w + 20
        legend_y = top + 8
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
            canvas.create_rectangle(legend_x, legend_y + idx * 18, legend_x + 10, legend_y + 10 + idx * 18, fill=color, outline=color)
            canvas.create_text(legend_x + 16, legend_y + 5 + idx * 18, text=f"Animal {animal_id}", anchor="w", fill="#111827")

    def show_success_message(self):
        """Shows a temporary success message on the screen."""
        success_label = CTkLabel(
            self.main_frame,
            text="Export to CSV successful!",
            text_color="green",
            font=("Arial", 18, "bold"),
        )
        success_label.place(relx=0.50, rely=0.10, anchor=CENTER)
        self.after(1800, success_label.destroy)

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
            self.show_success_message()
        except Exception:
            self.show_notification("Error", "Export to CSV failed")

    def raise_frame(self):
        """Raise frame and refresh displayed data."""
        super().raise_frame()
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
