"""
Tests for configuration management.

Run with: pytest tests/test_config.py -v
"""

import os
import sys
import json
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import Config


class TestConfigDefaults:
    """Test default configuration settings."""

    def test_default_auto_update_enabled(self):
        """Auto-update should be disabled by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            assert config.get_auto_update_enabled() == False

    def test_default_auto_download_enabled(self):
        """Auto-download should be disabled by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            assert config.get_auto_download_enabled() == False

    def test_default_auto_install_enabled(self):
        """Auto-install should be disabled by default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            assert config.get_auto_install_enabled() == False


class TestConfigReadWrite:
    """Test reading and writing configuration."""

    def test_set_auto_update_enabled(self):
        """Should be able to enable auto-update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            config.set_auto_update_enabled(True)
            
            assert config.get_auto_update_enabled() == True

    def test_config_persists(self):
        """Configuration should persist across instances."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            
            # Create first config and modify
            config1 = Config(config_file)
            config1.set_auto_update_enabled(True)
            
            # Create second config from same file
            config2 = Config(config_file)
            
            assert config2.get_auto_update_enabled() == True

    def test_get_with_dot_notation(self):
        """Should be able to get nested values with dot notation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            value = config.get('auto_update.enabled')
            
            assert value == False

    def test_set_with_dot_notation(self):
        """Should be able to set nested values with dot notation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            config.set('auto_update.enabled', True)
            
            assert config.get('auto_update.enabled') == True

    def test_get_with_default(self):
        """Should return default value for missing keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            value = config.get('nonexistent.key', 'default')
            
            assert value == 'default'


class TestConfigFileHandling:
    """Test configuration file creation and error handling."""

    def test_creates_config_file(self):
        """Should create config file if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "subdir" / "test_config.json"
            
            assert not config_file.exists()
            
            config = Config(config_file)
            
            assert config_file.exists()

    def test_creates_parent_directory(self):
        """Should create parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "a" / "b" / "c" / "test_config.json"
            
            config = Config(config_file)
            
            assert config_file.parent.exists()

    def test_handles_corrupted_file(self):
        """Should use defaults if config file is corrupted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            
            # Create corrupted JSON file
            with open(config_file, 'w') as f:
                f.write("{ invalid json }")
            
            # Should not crash, should use defaults
            config = Config(config_file)
            
            assert config.get_auto_update_enabled() == False

    def test_config_file_format(self):
        """Config file should be valid JSON with correct structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_file = Path(tmpdir) / "test_config.json"
            config = Config(config_file)
            
            # Read file directly
            with open(config_file, 'r') as f:
                data = json.load(f)
            
            assert 'auto_update' in data
            assert 'enabled' in data['auto_update']
            assert 'check_on_startup' in data['auto_update']
            assert 'auto_download' in data['auto_update']
            assert 'auto_install' in data['auto_update']
