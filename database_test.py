import pytest
from database_apis.experiment_database import ExperimentDatabase

class Test_Database_Setup:
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4)
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"])
    db.setup_cages(16, 4, 4)
    db.setup_measurement_items({"Weight"})
    
    def test_num_animals(self):
        assert 16 == self.db.get_number_animals()
        
    def test_num_groups(self):
        assert 4 == self.db.get_number_groups()
    
    def test_cage_max(self):
        assert 4 == self.db.get_cage_max()

    def test_get_all_groups(self):
        assert [("Control",), ("Group 1",), ("Group 2",), ("Group 3",)] == self.db.get_all_groups()
    
    def test_get_cages(self):
        assert [(1,1), (2,2), (3,3), (4,4)] == self.db.get_cages()
        
class Test_Animal_RFID_Methods:
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", True, 4, 2, 2)
    db.setup_groups(["Control", "Group 1"])
    db.setup_cages(4, 2, 2)
    db.setup_measurement_items({"Weight"})
    for i in range(0,4):
        db.add_animal(i, 10 + i)
    
    def test_add_animal_ids(self):
        assert 1 == self.db.get_animal_id(10)
        
    #is there a reason why the animal ids are returned as strings for this method but not the above method?
    def test_get_animal_ids(self):

        assert ['1', '2', '3', '4'] == self.db.get_all_animal_ids()
    
    def test_get_animal_rfid(self):
        assert '10' == self.db.get_animal_rfid(1)
    
    def test_get_animals_rfid(self):
        
        assert [('10',), ('11', ), ('12',), ('13',)] == self.db.get_animals_rfid()

class Test_Cage_Functions:
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", True, 4, 2, 2)
    db.setup_groups(["Control", "Group 1"])
    db.setup_cages(4, 2, 2)
    db.setup_measurement_items({"Weight"})
    for i in range(0,4):
        db.add_animal(i, 10 + i)
    
    def test_get_cages(self):
        assert [(1, 1), (2, 2)] == self.db.get_cages()

    def test_get_animals_from_cage(self):
        
        assert [(1,), (2,)] == self.db.get_animals_in_cage(1)

    def test_get_animals_by_cage(self):

        assert {'1': ['1', '2'], '2': ['3', '4']} == self.db.get_animals_by_cage()

class Test_Group_Functions:
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", True, 4, 2, 2)
    db.setup_groups(["Control", "Group 1"])
    db.setup_cages(4, 2, 2)
    db.setup_measurement_items({"Weight"})
    for i in range(0,4):
        db.add_animal(i, 10 + i)

    def test_get_all_groups(self):
        assert [('Control',), ('Group 1',)] == self.db.get_all_groups()

    def test_get_animals_in_group(self):
        assert [(1,), (2,)] == self.db.get_animals_in_group(1)
    
    def test_get_animals_by_group(self):
        assert {"Control" : ['1', '2'], "Group 1" : ['3', '4']} == self.db.get_animals_by_group()

    def test_get_cages_by_group(self):
        
        assert {'Control': ['1'], 'Group 1': ['2']} == self.db.get_cages_by_group()