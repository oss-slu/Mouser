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
    
    def test_add_animal_ids(self):
        self.db.add_animal(120)
        assert 1 == self.db.get_animal_id(120)
        
    #is there a reason why the animal ids are returned as strings for this method but not the above method?
    def test_get_animal_ids(self):
        for i in range(0,3):
            self.db.add_animal(10 + i)
         
        assert ['1', '2', '3', '4'] == self.db.get_all_animal_ids()
        
    