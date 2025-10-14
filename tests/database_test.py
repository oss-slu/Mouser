from datetime import datetime
import os
import time
import tempfile

'''Database Unit Tests'''
import unittest
from customtkinter import CTk
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from databases.experiment_database import ExperimentDatabase

'''Test class for UI components'''
class TestUIComponents(unittest.TestCase):
   def setUp(self):
       self.root = CTk()
       self.experiment_menu = ExperimentMenuUI(self.root, "test_file.mouser")
       self.new_experiment = NewExperimentUI(self.root)


   def tearDown(self):
       self.root.destroy()


   '''Test if the buttons in experiment menu ui exists'''
   def test_buttons_exist(self):
       self.assertIsNotNone(self.experiment_menu.collection_button)
       self.assertIsNotNone(self.experiment_menu.analysis_button)
       self.assertIsNotNone(self.experiment_menu.group_button)
       self.assertIsNotNone(self.experiment_menu.rfid_button)
       self.assertIsNotNone(self.experiment_menu.summary_button)


   '''Test button states'''
   def test_button_states(self):
       if not self.experiment_menu.all_rfid_mapped():
           self.assertEqual(self.experiment_menu.collection_button.cget("state"), "disabled")
           self.assertEqual(self.experiment_menu.analysis_button.cget("state"), "disabled")
       else:
           self.assertEqual(self.experiment_menu.rfid_button.cget("state"), "disabled")

   def test_frame_navigation(self):
       self.experiment_menu.data_page.raise_frame()
       self.experiment_menu.analysis_page.raise_frame()


   '''Test scaling factor of the font on mac'''
   def test_platform_scaling(self):
       if self.root.tk.call('tk', 'windowingsystem') == 'aqua':
           default_font = self.root.option_get("font", None)
           self.assertTrue(default_font)

   '''Test to check if new_experiment ui exist'''
   def test_new_experiment_ui(self):
       self.assertIsNotNone(self.new_experiment)

class TestDatabaseSetup:
    '''Test Basic Setup of Database'''
    db = ExperimentDatabase(file=tempfile.NamedTemporaryFile(suffix=".db", delete=False).name)
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "A", "test-123", ["Tester"], "Weight")
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], cage_capacity=4)

    #Add 16 animals to match test expectations
    for i in range(16):
        db.add_animal(animal_id=i+1, rfid=str(100 + i), group_id=1)

    def test_num_animals(self):
        '''Checks if num animals equals expected.'''
        print("Returned animal count:", self.db.get_number_animals())
        assert 16 == self.db.get_number_animals()

    def test_num_groups(self):
        '''Checks if num groups equals expected.'''
        self.db._c.execute("SELECT COUNT(*) FROM groups")
        result = self.db._c.fetchone()[0]
        print("Returned group count:", result)
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
    db = ExperimentDatabase(file=tempfile.NamedTemporaryFile(suffix=".db", delete=False).name)
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "A", "test-123", ["Tester"], "Weight")
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

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
    db = ExperimentDatabase(file=tempfile.NamedTemporaryFile(suffix=".db", delete=False).name)
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "A", "test-123", ["Tester"], "Weight")
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

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
    db = ExperimentDatabase(file=tempfile.NamedTemporaryFile(suffix=".db", delete=False).name)
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "A", "test-123", ["Tester"], "Weight")
    db.setup_groups(["Control", "Group 1"], cage_capacity=4)
    for i in range(0,4):
        db.add_animal(animal_id=i, rfid=str(10 + i), group_id=1)

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

class TestWindowsSQLiteBehavior:
    '''Simulates rapid reads/writes to test for SQLite locking and path issues on Windows.'''
    def test_simulated_instrument_input(self):
        test_db_file = "windows_test_sim.db"

        if os.path.exists(test_db_file):
            os.remove(test_db_file)

        db = ExperimentDatabase(file=tempfile.NamedTemporaryFile(delete=False).name)

        db.setup_experiment("Windows Test", "Rat", True, 5, 1, 5, "B")
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
        os.remove(test_db_file)

if __name__ == "__main__":
    setup = TestDatabaseSetup()
    setup.test_num_animals()
    setup.test_num_groups()
    print("Tests ran successfully.")
