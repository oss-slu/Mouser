import pytest
from database_apis.experiment_database import ExperimentDatabase

class Test_Setup:
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
        
        assert ["Control", "Group 1", "Group 2", "Group 3"] == self.db.get_all_groups()