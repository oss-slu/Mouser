"""
Settings dialog for Mouser application preferences.

Allows users to configure auto-update and other application settings.
"""

import customtkinter as ctk
from shared.config import get_config


class SettingsDialog(ctk.CTkToplevel):
    """
    Settings dialog window for configuring application preferences.
    """

    def __init__(self, parent):
        """
        Initialize settings dialog.

        Args:
            parent: Parent window
        """
        super().__init__(parent)

        self.config = get_config()
        self.title("Mouser Settings")
        self.geometry("500x400")

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        # Center dialog on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        self._create_widgets()

    def _create_widgets(self):
        """Create and layout all widgets in the dialog."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20, padx=20)

        # Auto-Update Section
        auto_update_frame = ctk.CTkFrame(self)
        auto_update_frame.pack(pady=10, padx=20, fill="x")

        section_label = ctk.CTkLabel(
            auto_update_frame,
            text="Auto-Update Settings",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        section_label.pack(pady=10, padx=10, anchor="w")

        # Enable auto-update checkbox
        self.auto_update_var = ctk.BooleanVar(
            value=self.config.get_auto_update_enabled()
        )
        self.auto_update_checkbox = ctk.CTkCheckBox(
            auto_update_frame,
            text="Enable automatic updates",
            variable=self.auto_update_var,
            command=self._on_auto_update_toggled
        )
        self.auto_update_checkbox.pack(pady=5, padx=20, anchor="w")

        # Description
        desc_label = ctk.CTkLabel(
            auto_update_frame,
            text="When enabled, Mouser will automatically check for updates\n"
                 "on startup and install them without prompting.",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        desc_label.pack(pady=5, padx=20, anchor="w")

        # Auto-download checkbox (sub-option)
        self.auto_download_var = ctk.BooleanVar(
            value=self.config.get_auto_download_enabled()
        )
        self.auto_download_checkbox = ctk.CTkCheckBox(
            auto_update_frame,
            text="Automatically download updates",
            variable=self.auto_download_var
        )
        self.auto_download_checkbox.pack(pady=5, padx=40, anchor="w")

        # Auto-install checkbox (sub-option)
        self.auto_install_var = ctk.BooleanVar(
            value=self.config.get_auto_install_enabled()
        )
        self.auto_install_checkbox = ctk.CTkCheckBox(
            auto_update_frame,
            text="Automatically install updates and restart",
            variable=self.auto_install_var
        )
        self.auto_install_checkbox.pack(pady=5, padx=40, anchor="w")

        # Update enabled/disabled state
        self._update_checkbox_states()

        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20, padx=20, fill="x", side="bottom")

        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(side="right", padx=5)

        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._save_and_close
        )
        save_button.pack(side="right", padx=5)

    def _on_auto_update_toggled(self):
        """Handle auto-update checkbox toggle."""
        self._update_checkbox_states()

    def _update_checkbox_states(self):
        """Enable/disable sub-options based on auto-update state."""
        enabled = self.auto_update_var.get()

        if enabled:
            self.auto_download_checkbox.configure(state="normal")
            self.auto_install_checkbox.configure(state="normal")
        else:
            self.auto_download_checkbox.configure(state="disabled")
            self.auto_install_checkbox.configure(state="disabled")

    def _save_and_close(self):
        """Save settings and close dialog."""
        # Save all settings
        self.config.set_auto_update_enabled(self.auto_update_var.get())
        self.config.set('auto_update.auto_download', self.auto_download_var.get())
        self.config.set('auto_update.auto_install', self.auto_install_var.get())
        self.destroy()


def show_settings_dialog(parent):
    """
    Show the settings dialog.

    Args:
        parent: Parent window
    """
    dialog = SettingsDialog(parent)
    dialog.wait_window()
