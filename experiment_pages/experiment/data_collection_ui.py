"""Data Collection UI Module."""
import re
import sqlite3 as sql
import threading
import time
import traceback
from datetime import date

from customtkinter import *
from CTkMessagebox import CTkMessagebox

from databases.experiment_database import ExperimentDatabase
from shared.audio import AudioManager
from shared.file_utils import SUCCESS_SOUND, save_temp_to_file
from shared.flash_overlay import FlashOverlay
from shared.serial_handler import SerialDataHandler
from shared.tk_models import MouserPage

class DataCollectionUI(MouserPage):
    """Handles live or manual data collection for active experiments."""

    def __init__(self, parent, prev_page, database_name, file_path: str = ""):
        super().__init__(parent, "Data Collection", prev_page)

        self.root = parent
        self.menu_page = prev_page
        self.file_path = file_path or database_name
        self.current_file_path = self.file_path

        self.database = ExperimentDatabase(database_name)

        ...
    
    # 🔧 FIX for pylint
    def raise_frame(self):
        super().raise_frame()
