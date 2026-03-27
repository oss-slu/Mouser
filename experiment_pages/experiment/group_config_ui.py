'''Group configuration module (modernized UI, full logic retained).'''
# pylint: disable=too-many-instance-attributes, import-error
from customtkinter import (
    CTk, CTkFrame, CTkLabel, CTkEntry,
    CTkButton, CTkRadioButton, CTkFont, BooleanVar, W, LEFT
)
from shared.tk_models import MouserPage, ChangePageButton
from shared.scrollable_frame import ScrolledFrame
from shared.experiment import Experiment
from experiment_pages.create_experiment.summary_ui import SummaryUI


class GroupConfigUI(MouserPage):
    '''Group Configuration user interface (preserves all logic).'''
    
    def __init__(
        self,
        experiment: Experiment,
        parent: CTk,
        prev_page: CTkFrame,
        menu_page: CTkFrame,
        edit_mode: bool = False,
        save_callback=None,
    ):
        title = "Experiment - Group Configuration" if edit_mode else "New Experiment - Group Configuration"
        super().__init__(parent, title, None)  # Pass None to prevent parent from creating menu button
        
        self.experiment = experiment
        self.menu_page = menu_page
        self.prev_page = prev_page
        self.next_button = None
        self.edit_mode = edit_mode
        self.save_callback = save_callback
        
        # Configure page background
        self.configure(fg_color="#eef4ff")
        self.canvas.configure(bg="#eef4ff", highlightthickness=0)
        self.canvas.configure(yscrollincrement=24)
        self._scroll_enabled = False
        
        # Configure banner
        self.canvas.itemconfig(
            self.rectangle,
            fill="#0f172a",
            outline="#0f172a",
        )
        self.canvas.itemconfig(
            self.title_label,
            text="Group Configuration",
            fill="#f8fafc",
            font=("Segoe UI Semibold", 20),
        )
        
        # Add scrollbar
        from customtkinter import CTkScrollbar
        self.scrollbar = CTkScrollbar(
            self,
            orientation="vertical",
            command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Fonts
        self.font_section = CTkFont("Segoe UI Semibold", 18)
        self.font_label = CTkFont("Segoe UI Semibold", 15)
        self.font_body = CTkFont("Segoe UI", 14)
        
        # Field styling
        self.field_style = {
            "height": 42,
            "corner_radius": 14,
            "border_width": 1,
            "border_color": "#bfdbfe",
            "fg_color": "#f8fbff",
            "text_color": "#0f172a",
            "font": self.font_body,
        }
        
        # ----------------------------
        # Top Navigation Buttons
        # ----------------------------
        # Create back button
        if prev_page:
            self.menu_button = CTkButton(
                self.canvas,
                text="←",
                corner_radius=15,
                height=42,
                width=42,
                font=("Segoe UI Semibold", 17),
                command=lambda: prev_page.raise_frame(),
                text_color="#f8fafc",
                fg_color="#1d4ed8",
                hover_color="#1e3a8a",
                bg_color="transparent",
                border_width=1,
                border_color="#93c5fd",
            )
            self.menu_button_window = self.canvas.create_window(
                24,
                25,
                anchor="w",
                window=self.menu_button,
            )
        
        if self.edit_mode:
            self.create_save_button()
        else:
            # Set next page (Summary) for new experiment flow
            self.next_page = SummaryUI(self.experiment, parent, self, menu_page)
            self.create_next_button()
        
        # ----------------------------
        # Main Content Frame
        # ----------------------------
        self.main_frame = CTkFrame(
            self.canvas,
            fg_color="#eef4ff",
            corner_radius=0,
        )
        self.main_window = self.canvas.create_window(
            24,
            68,
            anchor="nw",
            window=self.main_frame,
        )
        
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.bind("<Configure>", self._update_scroll_region)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<Enter>", self._bind_mousewheel)
        self.canvas.bind("<Leave>", self._unbind_mousewheel)
        
        # --- Group Names Section (direct to main_frame, no outer container) ---
        group_section = self._create_section(
            self.main_frame, 
            0, 
            0, 
            "📝 Group Names", 
            "#ffffff",  # White background
            "#bfdbfe"   # Blue border
        )
        
        self.group_frame = CTkFrame(group_section, fg_color="transparent")
        self.group_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.group_frame.grid_columnconfigure(0, weight=1)
        
        self.create_group_entries(int(self.experiment.get_num_groups()))
        
        # --- Input Method Section (with extra top spacing) ---
        method_section = self._create_section(
            self.main_frame,
            1,
            0,
            "⚙️ Input Method",
            "#ffffff",  # White background
            "#bbf7d0"   # Green border
        )
        
        self.item_frame = CTkFrame(method_section, fg_color="transparent")
        self.item_frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 18))
        self.item_frame.grid_columnconfigure(0, weight=1)
        self.item_frame.grid_columnconfigure(1, weight=1)
        self.item_frame.grid_columnconfigure(2, weight=1)
        
        self.create_item_frame(self.experiment.get_measurement_items())
    
    def _create_section(
        self,
        parent,
        row,
        column,
        title,
        fg_color,
        border_color,
    ):
        """Create a stylized section card."""
        frame = CTkFrame(
            parent,
            fg_color=fg_color,
            corner_radius=22,
            border_width=2,  # Increased border width for better visibility
            border_color=border_color,
        )
        # First section: 20px top padding, second section: 30px top spacing, 30px bottom padding
        if row == 0:
            pady_value = (20, 12)
        else:
            pady_value = (30, 30)  # Extra bottom padding for last section
            
        frame.grid(
            row=row,
            column=column,
            sticky="ew",
            padx=10,
            pady=pady_value,
        )
        frame.grid_columnconfigure(0, weight=1)
        
        CTkLabel(
            frame,
            text=title,
            font=self.font_section,
            text_color="#0f172a",
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(18, 14))
        
        return frame
    
    def _update_scroll_region(self, _event=None):
        """Enable page scrolling only when content exceeds the visible area."""
        self.update_idletasks()
        content_height = self.main_frame.winfo_reqheight() + 150  # Increased padding for bottom content
        canvas_height = max(self.canvas.winfo_height(), 1)
        self._scroll_enabled = content_height > canvas_height
        if self._scroll_enabled:
            self.canvas.configure(
                scrollregion=(0, 0, self.canvas.winfo_width(), content_height)
            )
            self.scrollbar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        else:
            self.canvas.configure(
                scrollregion=(0, 0, self.canvas.winfo_width(), canvas_height)
            )
            self.canvas.yview_moveto(0)
            self.scrollbar.place_forget()
    
    def _bind_mousewheel(self, _event=None):
        """Enable mousewheel scrolling while the pointer is on this page."""
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<4>", self._on_mousewheel)
        self.canvas.bind_all("<5>", self._on_mousewheel)
    
    def _unbind_mousewheel(self, _event=None):
        """Disable page-level mousewheel binding when leaving the page."""
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<4>")
        self.canvas.unbind_all("<5>")
    
    def _on_mousewheel(self, event):
        """Scroll the page canvas across supported platforms."""
        if not self._scroll_enabled:
            return
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    def _on_canvas_configure(self, event):
        """Resize the embedded content area with the window width."""
        content_width = max(event.width - 56, 320)
        self.canvas.coords(self.main_window, 24, 68)
        self.canvas.itemconfigure(self.main_window, width=content_width)
        
        # Reposition the back button on the left side of the banner
        if hasattr(self, "menu_button_window") and self.menu_button_window is not None:
            self.canvas.coords(self.menu_button_window, 24, 25)
        
        # Reposition the next button on the right side of the banner
        if hasattr(self, "next_button_window") and self.next_button_window is not None:
            self.canvas.coords(self.next_button_window, event.width, 30)
        
        self._update_scroll_region()
    
    # ------------------------------------------------------------
    # Navigation / Buttons
    # ------------------------------------------------------------
    def create_next_button(self):
        '''Creates a Next button aligned on banner.'''
        if self.next_button:
            self.next_button.destroy()
        if hasattr(self, "next_button_window") and self.next_button_window is not None:
            self.canvas.delete(self.next_button_window)
            self.next_button_window = None
        
        self.next_button = CTkButton(
            self.canvas,
            text="➜",
            corner_radius=25,
            height=50,
            width=50,
            font=("Segoe UI Semibold", 24),
            text_color="#ffffff",
            fg_color="#ea580c",
            hover_color="#dc2626",
            bg_color="transparent",
            border_width=0,
            command=lambda: [self.save_experiment(), self.next_page.raise_frame()],
        )
        self.next_button_window = self.canvas.create_window(
            max(self.canvas.winfo_width(), 25),
            30,
            anchor="e",
            window=self.next_button,
        )
    
    def create_save_button(self):
        """Creates a Save & Return button for existing experiment edit flow."""
        if self.next_button:
            self.next_button.destroy()
        if hasattr(self, "next_button_window") and self.next_button_window is not None:
            self.canvas.delete(self.next_button_window)
            self.next_button_window = None
        
        self.next_button = CTkButton(
            self.canvas,
            text="💾",
            corner_radius=25,
            height=50,
            width=50,
            font=("Segoe UI Semibold", 24),
            text_color="#ffffff",
            fg_color="#16a34a",
            hover_color="#15803d",
            bg_color="transparent",
            border_width=0,
            command=lambda: [self.save_experiment(), self.menu_page.raise_frame()],
        )
        self.next_button_window = self.canvas.create_window(
            max(self.canvas.winfo_width(), 25),
            30,
            anchor="e",
            window=self.next_button,
        )
    
    # ------------------------------------------------------------
    # Core Functionality
    # ------------------------------------------------------------
    def create_group_entries(self, num):
        '''Creates widgets for group entries.'''
        self.group_input = []
        existing_names = self.experiment.get_group_names() if hasattr(self.experiment, "get_group_names") else []
        
        for i in range(num):
            # Label for each group
            CTkLabel(
                self.group_frame,
                text=f"Group {i + 1} Name",
                font=self.font_label,
                text_color="#1e293b",
                anchor="w",
            ).grid(row=i * 2, column=0, sticky=W, padx=0, pady=(8 if i > 0 else 0, 6))
            
            # Entry field
            entry = CTkEntry(
                self.group_frame,
                width=400,
                placeholder_text=f"Enter name for Group {i + 1}",
                **self.field_style,
            )
            entry.grid(row=i * 2 + 1, column=0, sticky="ew", padx=0, pady=(0, 12 if i < num - 1 else 0))
            
            if i < len(existing_names):
                entry.insert(0, str(existing_names[i]))
            
            self.group_input.append(entry)
    
    def create_item_frame(self, item):
        '''Creates a radio-button group for input method selection.'''
        self.button_vars = []
        self.item_auto_buttons = []
        self.item_man_buttons = []
        
        initial_value = self.experiment.get_measurement_type()
        self.type = BooleanVar(value=(initial_value != 0))
        self.button_vars.append(self.type)
        
        # Label
        CTkLabel(
            self.item_frame,
            text=f"{item} Collection Method",
            font=self.font_label,
            text_color="#1e293b",
            anchor="w",
        ).grid(row=0, column=0, columnspan=3, sticky=W, padx=0, pady=(0, 12))
        
        # Radio button frame
        radio_frame = CTkFrame(self.item_frame, fg_color="transparent")
        radio_frame.grid(row=1, column=0, columnspan=3, sticky="w", padx=0)
        
        auto = CTkRadioButton(
            radio_frame,
            text='🤖 Automatic',
            variable=self.type,
            value=True,
            font=self.font_body,
            text_color="#0f172a",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            border_color="#60a5fa",
        )
        man = CTkRadioButton(
            radio_frame,
            text='✍️ Manual',
            variable=self.type,
            value=False,
            font=self.font_body,
            text_color="#0f172a",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            border_color="#60a5fa",
        )
        
        auto.grid(row=0, column=0, padx=(0, 24), pady=4)
        man.grid(row=0, column=1, padx=(0, 8), pady=4)
        
        self.item_auto_buttons.append(auto)
        self.item_man_buttons.append(man)
    
    def update_page(self):
        '''Updates the UI when experiment data changes.'''
        if self.experiment.check_num_groups_change():
            for widget in self.group_frame.winfo_children():
                widget.destroy()
            self.create_group_entries(int(self.experiment.get_num_groups()))
            self.experiment.set_group_num_changed_false()
        
        if self.experiment.check_measurement_items_changed():
            for widget in self.item_frame.winfo_children():
                widget.destroy()
            self.create_item_frame(self.experiment.get_measurement_items())
            self.experiment.set_measurement_items_changed_false()
    
    def save_experiment(self):
        '''Saves all entered group names and input method.'''
        group_names = [entry.get().strip() for entry in self.group_input]
        self.experiment.group_names = group_names
        self.experiment.data_collect_type = 1 if self.button_vars[0].get() else 0
        
        if callable(self.save_callback):
            self.save_callback(self.experiment)
        
        if hasattr(self, "next_page") and self.next_page is not None:
            self.next_page.update_page()