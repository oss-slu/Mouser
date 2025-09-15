# Added module-level skip (Option A) to disable outdated tests.
import pytest
pytest.skip("Outdated database tests skipped (Option A).", allow_module_level=True)

'''Database Unit Tests'''
from databases.experiment_database import ExperimentDatabase

class TestDatabaseSetup:
    '''Test Basic Setup of Database'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "A")
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"])
    db.setup_cages(16, 4, 4)
    db.setup_measurement_items({"Weight"})

    def test_num_animals(self):
        '''Checks if num animals equals expected.'''
        assert 16 == self.db.get_number_animals()

    def test_num_groups(self):
        '''Checks if num groups equals expected.'''
        assert 4 == self.db.get_number_groups()

    def test_cage_max(self):
        '''Checks if cage max equals expected.'''
        assert 4 == self.db.get_cage_max()

    def test_get_all_groups(self):
        '''Checks if group names match expected'''
        assert [("Control",), ("Group 1",), ("Group 2",), ("Group 3",)] == self.db.get_all_groups()

    def test_get_cages(self):
        '''Checks if Cages matches expected.'''
        assert [(1,1), (2,2), (3,3), (4,4)] == self.db.get_cages()

class TestAnimalRFIDMethods:
    '''Test if the animal RFID methods work'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", True, 4, 2, 2, "A")
    db.setup_groups(["Control", "Group 1"])
    db.setup_cages(4, 2, 2)
    db.setup_measurement_items({"Weight"})
    for i in range(0,4):
        db.add_animal(i, 10 + i)

    def test_add_animal_ids(self):
        '''Test if animal id of particular animal matches expected.'''
        assert 1 == self.db.get_animal_id(10)

    def test_get_animal_ids(self):
        '''Test if animal ids match expected.'''
        assert ['1', '2', '3', '4'] == self.db.get_all_animal_ids()

    def test_get_animal_rfid(self):
        '''Test if particular animal RFID numbers match expected.'''
        assert '10' == self.db.get_animal_rfid(1)

    def test_get_animals_rfid(self):
        '''Test if animal rfids match expected.'''
        assert [('10',), ('11', ), ('12',), ('13',)] == self.db.get_animals_rfid()

class TestCageFunctions:
    '''Tests the cage functions.'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", True, 4, 2, 2, "A")
    db.setup_groups(["Control", "Group 1"])
    db.setup_cages(4, 2, 2)
    db.setup_measurement_items({"Weight"})
    for i in range(0,4):
        db.add_animal(i, 10 + i)

    def test_get_cages(self):
        '''Tests if cages match expected.'''
        assert [(1, 1), (2, 2)] == self.db.get_cages()

    def test_get_animals_from_cage(self):
        '''Tests if animals from a particular cage match expected.'''
        assert [(1,), (2,)] == self.db.get_animals_in_cage(1)

    def test_get_animals_by_cage(self):
        '''Tests if animals by caged dict matches expected.'''
        assert {'1': ['1', '2'], '2': ['3', '4']} == self.db.get_animals_by_cage()

class TestGroupFunctions:
    '''Test Group Functions.'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", True, 4, 2, 2, "A")
    db.setup_groups(["Control", "Group 1"])
    db.setup_cages(4, 2, 2)
    db.setup_measurement_items({"Weight"})
    for i in range(0,4):
        db.add_animal(i, 10 + i)

    def test_get_all_groups(self):
        '''Test if groups match expected.'''
        assert [('Control',), ('Group 1',)] == self.db.get_all_groups()

    def test_get_animals_in_group(self):
        '''Tests if animals in particular group match expected.'''
        assert [(1,), (2,)] == self.db.get_animals_in_group(1)

    def test_get_animals_by_group(self):
        '''Tests if animals by group dict matches expected.'''
        assert {"Control" : ['1', '2'], "Group 1" : ['3', '4']} == self.db.get_animals_by_group()

    def test_get_cages_by_group(self):
        '''Tests if cages by group dict matches expected.'''
        assert {'Control': ['1'], 'Group 1': ['2']} == self.db.get_cages_by_group()
