import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, num, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="center")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for i in range(0,num):
            label = ttk.Label(canvas, text=('Group ' + str(i+1)), font=("Arial", 13))
            label.grid(row=i, column=0, padx=10, pady=10)

            text = ttk.Entry(canvas, width=30, font=("Arial", 13))
            text.grid(row=i, column=1, padx=10, pady=20)
            # self.group_names.append(text.get())