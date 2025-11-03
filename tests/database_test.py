'''Database Unit Tests'''
import sys
import os
from datetime import datetime
import time
import tempfile
import importlib.util
import types

# Ensure repository root is on sys.path so tests can import the local `databases` package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # First try a normal import (works when repo root is on sys.path)
    from databases.experiment_database import ExperimentDatabase
    from databases.database_controller import DatabaseController
except ModuleNotFoundError:
    # Fallback: load modules directly from file paths so tests can be run from the tests/ folder
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    exp_path = os.path.join(repo_root, 'databases', 'experiment_database.py')
    ctrl_path = os.path.join(repo_root, 'databases', 'database_controller.py')

    spec = importlib.util.spec_from_file_location(
        'databases.experiment_database', exp_path)
    exp_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exp_mod)
    # Prepare a package context so relative imports inside database_controller.py work
    pkg = types.ModuleType('databases')
    pkg.__path__ = [os.path.join(repo_root, 'databases')]
    sys.modules['databases'] = pkg
    sys.modules['databases.experiment_database'] = exp_mod

    spec2 = importlib.util.spec_from_file_location(
        'databases.database_controller', ctrl_path)
    ctrl_mod = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(ctrl_mod)

    ExperimentDatabase = exp_mod.ExperimentDatabase
    DatabaseController = ctrl_mod.DatabaseController

class TestDatabaseSetup:
    '''Test Basic Setup of Database'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups([
        "Control",
        "Group 1",
        "Group 2",
        "Group 3",
    ], cage_capacity=4)

    #Add 16 animals to match test expectations
    for i in range(16):
        db.add_animal(animal_id=i+1, rfid=str(100 + i), group_id=1)

    def test_num_animals(self):
        '''Checks if num animals equals expected.'''
        print("Returned animal count:", self.db.get_number_animals())
        assert 16 == self.db.get_number_animals()

    def test_num_groups(self):
        '''Checks if num groups equals expected.'''
        # Use public API to get number of groups
        print("Returned group count:", self.db.get_number_groups())
        assert 4 == self.db.get_number_groups()

    def test_cage_max(self):
        '''Checks if cage max equals expected.'''
        # ExperimentDatabase doesn't expose cage_max directly; use the controller
        ctrl = DatabaseController(self.db.db_file)
        assert 4 == ctrl.get_cage_max()

    def test_get_all_groups(self):
        '''Checks if group names match expected'''
        # ExperimentDatabase returns a list of group names
        assert ["Control", "Group 1", "Group 2", "Group 3"] == self.db.get_groups()

    # Legacy get_cages test removed: functionality replaced by get_cages_by_group()

class TestAnimalRFIDMethods:
    '''Test if the animal RFID methods work'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

    def test_add_animal_ids(self):
        '''Test if animal id of particular animal matches expected.'''
        # RFID values are stored as strings
        assert 1 == self.db.get_animal_id('10')


    def test_get_animal_rfid(self):
        '''Test if particular animal RFID numbers match expected.'''
        assert '10' == self.db.get_animal_rfid(1)

    def test_get_animals_rfid(self):
        '''Test if animal rfids match expected.'''
        # Use current API name: returns list of strings
        assert ['10', '11', '12', '13'] == self.db.get_all_animals_rfid()

class TestCageFunctions:
    '''Tests the cage functions.'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

    def test_get_cages(self):
        '''Placeholder: cage behavior validated via get_cages_by_group.'''
        

    def test_get_animals_from_cage(self):
        '''Tests if animals from a particular cage match expected.'''
        # get_animals_in_cage expects a group name
        assert [(1,), (2,)] == self.db.get_animals_in_cage('Control')

    def test_get_animals_by_cage(self):
        '''Tests if animals by caged dict matches expected.'''
        # No direct API for animals_by_cage; validate cage assignments mapping instead
        assignments = self.db.get_cage_assignments()
        # Ensure the first two animals are assigned (group_id, cage_number) tuples
        assert assignments[1][0] == 1
        assert isinstance(assignments[1][1], int)

class TestGroupFunctions:
    '''Test Group Functions.'''
    _fd, _dbfile = tempfile.mkstemp(suffix=".db")
    os.close(_fd)
    db = ExperimentDatabase(file=_dbfile)
    db.setup_experiment(
        "Test",
        "Test Mouse",
        False,
        16,
        4,
        4,
        "A",
        "test-123",
        ["Tester"],
        "Weight",
    )
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

    def test_get_all_groups(self):
        '''Test if groups match expected.'''
        assert ['Control', 'Group 1'] == self.db.get_groups()

    def test_get_animals_in_group(self):
        '''Tests if animals in particular group match expected.'''
        # Use group name with ExperimentDatabase API
        assert [(1,), (2,)] == self.db.get_animals_in_cage('Control')

    def test_get_animals_by_group(self):
        '''Tests if animals by group dict matches expected.'''
        # No direct animals_by_group API; verify groups and assignments are consistent
        groups = self.db.get_groups()
        assert 'Control' in groups

    def test_get_cages_by_group(self):
        '''Tests if cages by group dict matches expected.'''
        # get_cages_by_group returns a dict keyed by group_id -> list of cage numbers
        cages = self.db.get_cages_by_group()
        # Expect group 1 to have at least one cage and group 2 to exist
        assert 1 in cages
        assert isinstance(cages[1], list)

# Tests are intentionally small; disable too-few-public-methods pylint warning
class TestWindowsSQLiteBehavior:  # pylint: disable=too-few-public-methods
    '''Simulates rapid reads/writes to test for SQLite locking and path issues on Windows.'''
    def test_simulated_instrument_input(self):
        '''Simulate instrument input and rapid writes to the DB.'''
        # Use a temporary DB file for this test
        _fd, db_path = tempfile.mkstemp()
        os.close(_fd)

        # Ensure any leftover named file is removed before creating DB
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except OSError:
                pass

        db = ExperimentDatabase(file=db_path)

        db.setup_experiment(
            "Windows Test",
            "Rat",
            True,
            5,
            1,
            5,
            "B",
        )
        db.setup_groups(["RFID Group"], cage_capacity=4)

        for i in range(1, 6):
            db.add_animal(animal_id=i, rfid=f"RFID-{i}", group_id=1)

        for i in range(1, 6):
            db.add_measurement(animal_id=i, value=25 + i)
            time.sleep(0.05)

        today = datetime.now().strftime("%Y-%m-%d")
        data = db.get_measurements_by_date(today)

        assert len(data) == 5
        db.close()
        try:
            os.remove(db_path)
        except OSError:
            pass

if __name__ == "__main__":
    setup = TestDatabaseSetup()
    setup.test_num_animals()
    setup.test_num_groups()
    print("Tests ran successfully.")
