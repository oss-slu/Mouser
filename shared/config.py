"""
Configuration management for Mouser application.

Handles reading and writing user preferences, including auto-update settings.
"""

import json
from pathlib import Path


class Config:
    """
    Manages application configuration settings.
    
    Settings are stored in a JSON file in the user's settings directory.
    """
    
    def __init__(self, config_file="settings/app_config.json"):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file relative to project root
        """
        self.config_path = Path(config_file)
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Load settings from config file or create default settings."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, use defaults
                return self._default_settings()
        else:
            # Create default settings file
            settings = self._default_settings()
            self._save_settings(settings)
            return settings
    
    def _default_settings(self):
        """Return default configuration settings."""
        return {
            "auto_update": {
                "enabled": False,  # Auto-update disabled by default
                "check_on_startup": True,
                "auto_download": False,  # Disabled by default
                "auto_install": False  # Disabled by default
            }
        }
    
    def _save_settings(self, settings):
        """Save settings to config file."""
        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w') as f:
            json.dump(settings, f, indent=2)
    
    def get(self, key, default=None):
        """
        Get a configuration value.
        
        Args:
            key: Dot-notation key (e.g., 'auto_update.enabled')
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """
        Set a configuration value and save to file.
        
        Args:
            key: Dot-notation key (e.g., 'auto_update.enabled')
            value: Value to set
        """
        keys = key.split('.')
        settings = self.settings
        
        # Navigate to the parent of the final key
        for k in keys[:-1]:
            if k not in settings:
                settings[k] = {}
            settings = settings[k]
        
        # Set the final key
        settings[keys[-1]] = value
        
        # Save to file
        self._save_settings(self.settings)
    
    def get_auto_update_enabled(self):
        """Check if auto-update is enabled."""
        return self.get('auto_update.enabled', True)
    
    def set_auto_update_enabled(self, enabled):
        """Enable or disable auto-update."""
        self.set('auto_update.enabled', enabled)
    
    def get_auto_download_enabled(self):
        """Check if automatic download is enabled."""
        return self.get('auto_update.auto_download', True)
    
    def get_auto_install_enabled(self):
        """Check if automatic installation is enabled."""
        return self.get('auto_update.auto_install', True)


# Global config instance
_config = None

def get_config():
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
