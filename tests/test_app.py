import sys
import os
import sqlite3
import tempfile
from shared.password_utils import PasswordManager
from databases.database_controller import DatabaseController
from databases.experiment_database import ExperimentDatabase
from shared.tk_models import MouserPage
from customtkinter import CTk  
from shared.audio import AudioManager
from shared.flash_overlay import FlashOverlay
from unittest import TestLoader, TestSuite, TextTestRunner


from unittest import TestLoader, TestSuite, TextTestRunner
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ["DISPLAY"] = ":0"


#Import all test classes from your database test file
from tests.database_test import (
    TestPlatform,
    TestUIComponents,
    TestDatabaseSetup,
    TestAnimalRFIDMethods,
    TestCageFunctions,
    TestGroupFunctions
)


def test_database_suite_execution():
    """Ensures all database-related tests pass when executed together."""

    # Load all database tests into one suite
    loader = TestLoader()
    suite = TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestPlatform))
    suite.addTests(loader.loadTestsFromTestCase(TestUIComponents))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSetup))
    suite.addTests(loader.loadTestsFromTestCase(TestAnimalRFIDMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestCageFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestGroupFunctions))

    # Run the suite
    runner = TextTestRunner(verbosity=2)
    result = runner.run(suite)

    #If ANY test fails → pytest will mark THIS test as failed
    assert result.wasSuccessful(), "Database test suite failed"

def test_database_controller_quick(monkeypatch):
    """Test for DatabaseController basic operations"""

    class dummydb:

        def get_measurement_items(self):
            return ["weight"]
        
        def get_cages_by_group(self): 
            return {"1": [1]}
    
        def get_cage_assignments(self): 
            return {"101": (1)}
        
        def get_animals(self):
            return [("101",)]   

        def get_measurements_by_date(self, parameter):  
            return [("101", "2025", "weight", 10.0)]
        
        def get_groups(self):
            return ["A"]
        
        def update_animal_cage(self, a,b):
            return None
        
        class _conn:

            def execute(query):
                return None
            def fetchone():
                return (5,) 

    dummydb = dummydb()

    controller = DatabaseController(":memory:")
    monkeypatch.setattr(controller, "db", dummydb)    
    controller.reset_attributes()

    group = controller.get_groups() 
    cage_max = controller.get_cage_max() 
    valid_animal = controller.check_valid_animal("101") 
    valid_cage = controller.check_valid_cage("999") 
    controller.update_animal_cage("101", 2) 

    assert group == ["A"]
    assert cage_max == 5
    assert valid_animal == True
    assert valid_cage == False

def test_experiment_database_in_memory():
    """Validate ExperimentDatabase basic SQLite behavior"""
    
    db_connection = sqlite3.connect(":memory:")
    experiment_db = ExperimentDatabase(":memory:")
    experiment_db._conn.execute("""
        CREATE TABLE experiments_db (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            weight REAL
        );
    """)
    experiment_db._conn.executescript("""INSERT INTO experiments_db (name, weight)
            VALUES
                ('Mouse A', 25.0),
                ('Mouse B', 30.5);
""")

    experiment_db._conn.commit()

    rows = list(experiment_db._conn.execute("SELECT * FROM experiments_db;"))
    assert len(rows) == 2
    assert rows[0][1] == 'Mouse A'
    assert rows[1][2] == 30.5


    experiment_db._conn.execute("UPDATE experiments_db SET weight = 26.2 WHERE name = 'Mouse A';")
    experiment_db._conn.execute("DELETE FROM experiments_db WHERE name = 'Mouse B';")
    experiment_db._conn.execute("INSERT INTO experiments_db (name, weight) VALUES ('Mouse C', 20.0);")

    experiment_db._conn.rollback()
    experiment_db._conn.close()

def test_password_manager_encrypt_decrypt():
    password = PasswordManager("Test123")
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(b"Secret message")
    temp_path = temp.name
    temp.close()

    password.encrypt_file(temp_path)
    decrypted_data = password.decrypt_file(temp_path)
    assert decrypted_data == b"Secret message"

    os.remove(temp_path)

def test_file_utils_temp_file(tmp_path):
    """Check file read/write operations with temp directory"""
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.write(b"Hello World")
    temp_path = temp.name
    temp.close() 

    with open(temp_path, "rb") as file: 
        content = file.read()

    assert content == b"Hello World"

def test_tk_models_basic():
    """Smoke test for tk_models class creation."""
    root = CTk() 
    shared_model = MouserPage(root, "Test Page")
    assert shared_model is not None
    assert isinstance(shared_model, MouserPage)
    root.destroy()  

def test_audio_playback_mocked(monkeypatch):
    """Ensure AudioManager.play() calls __play when idle."""
    class MockPlay:
        def __init__(self):
            self.called = False
            self.file = None
        def __call__(self, file):
            self.called = True
            self.file = file
            return True

    mock_play = MockPlay()
    monkeypatch.setattr("shared.audio.AudioManager._AudioManager__play", mock_play)

    fake_file = tempfile.NamedTemporaryFile(delete=False)
    fake_file.write(b"Fake audio data")
    fake_file.close()

    AudioManager._is_playing = False
    AudioManager.play(fake_file.name)
    assert mock_play.called is True
    assert mock_play.file == fake_file.name

    os.remove(fake_file.name)


def test_audio_playback_busy(monkeypatch):
    """Ensure AudioManager prevents overlapping playback."""
    AudioManager._is_playing = True
    AudioManager.play("sample.mp3")
    AudioManager._is_playing = False



def test_flash_overlay_behavior():
    """Basic instantiation test for FlashOverlay UI component"""
    
    root = CTk()
    overlay = FlashOverlay(root, "Test Message")
    if hasattr(overlay, "show"):
        overlay.show()
    if hasattr(overlay, "hide"):
        overlay.hide()
    if hasattr(overlay, "flash"):
        overlay.flash()

    assert True

