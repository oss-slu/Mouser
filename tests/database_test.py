'''Database Unit Tests'''
import unittest
import os
import sys
import tempfile
from customtkinter import CTk
from experiment_pages.experiment.experiment_menu_ui import ExperimentMenuUI
from experiment_pages.create_experiment.new_experiment_ui import NewExperimentUI
from databases.experiment_database import ExperimentDatabase

class TestPlatform(unittest.TestCase): 
      def test_database_across_platform(self):
        '''Test to validate SQLite operations across Windows, macOS, and Linux'''
        temp_db_path = create_temp_file()

        db = ExperimentDatabase(temp_db_path)
        db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, 
                        "Weight", 1, ["Investigator"], "Weight")
        db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)
        for i in range(0,4):
            group_id = 1 if i < 2 else 2
            db.add_animal(group_id, 10 + i)

        value = db.get_animal_rfid(animal_id=1)
        os_name = get_platform()
        
        self.assertEqual(value, '10')
        self.assertIn(os_name, ["win32", "darwin", "linux"])

        delete_file(temp_db_path)

        def create_temp_file():
            '''Function to create temporary file and return it'''
            temp = tempfile.NamedTemporaryFile(delete=False)  
            temp.close()        
            return temp.name

        def get_platform():
            '''Function that returns identifier for operating system'''
            return sys.platform

        def delete_file(path):
            '''Function to check if a file exist in path and deletes it'''
            if os.path.exists(path):
                os.remove(path)

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


class TestDatabaseSetup(unittest.TestCase):
    '''Test Basic Setup of Database'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "Weight", 1, ["Investigator"], "Weight")
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)

    def test_num_animals(self):
        '''Checks if num animals equals expected.'''
        self.assertEqual(16, self.db.get_number_animals())

    def test_num_groups(self):
        '''Checks if num groups equals expected.'''
        self.assertEqual(4, self.db.get_number_groups())

    def test_cage_max(self):
        '''Checks if cage max equals expected.'''
        self.assertEqual(4, self.db.get_cage_max())

    def test_get_all_groups(self):
        '''Checks if group names match expected'''
        self.assertEqual([("Control",), ("Group 1",), ("Group 2",), ("Group 3",)]
                          ,self.db.get_all_groups())

class TestAnimalRFIDMethods(unittest.TestCase):
    '''Test if the animal RFID methods work'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "Weight", 1, ["Investigator"], "Weight")
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)
    for i in range(0,4):
        group_id = 1 if i < 2 else 2
        db.add_animal(group_id, 10 + i)

    def test_add_animal_ids(self):
        '''Test if animal id of particular animal matches expected.'''
        self.assertEqual(1, self.db.get_animal_id(10))

    def test_get_animal_ids(self):
        '''Test if animal ids match expected.'''
        self.assertEqual(['1', '2', '3', '4'], self.db.get_all_animal_ids())

    def test_get_animal_rfid(self):
        '''Test if particular animal RFID numbers match expected.'''
        self.assertEqual('10', self.db.get_animal_rfid(1))

    def test_get_animals_rfid(self):
        '''Test if animal rfids match expected.'''
        self.assertEqual([('10',), ('11', ), ('12',), ('13',)],
                        self.db.get_animals_rfid())

class TestCageFunctions(unittest.TestCase):
    '''Tests the cage functions.'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "Weight", 1, ["Investigator"], "Weight")
    db.setup_groups(["Control", "Group 1", "Group 2", "Group 3"], 4)
    for i in range(0,4):
        group_id = 1 if i < 2 else 2
        db.add_animal(group_id, 10 + i)

    def test_get_animals_from_cage(self):
        '''Tests if animals from a particular cage match expected.'''
        self.assertEqual([(1,), (2,)], self.db.get_animals_in_cage())


    def test_get_animals_by_cage(self):
        '''Tests if animals by caged dict matches expected.'''
        self.assertEqual({'1': ['1', '2'], '2': ['3', '4']}, self.db.get_animals_by_cage())

class TestGroupFunctions(unittest.TestCase):
    '''Test Group Functions.'''
    db = ExperimentDatabase()
    db.setup_experiment("Test", "Test Mouse", False, 16, 4, 4, "Weight", 1, ["Investigator"], "Weight")
    db.setup_groups(["Control", "Group 1"], 4)
    for i in range(0,4):
        group_id = 1 if i < 2 else 2
        db.add_animal(group_id, 10 + i)


    def test_get_all_groups(self):
        '''Test if groups match expected.'''
        self.assertEqual([('Control',), ('Group 1',)], self.db.get_all_groups())

    def test_get_animals_in_group(self):
        '''Tests if animals in particular group match expected.'''
        self.assertEqual([(1,), (2,)], self.db.get_animals_in_group("Control"))

    def test_get_animals_by_group(self):
        '''Tests if animals by group dict matches expected.'''
        self.assertEqual({"Control" : ['1', '2'], "Group 1" : ['3', '4']},
                        self.db.get_animals_by_group())

    def test_get_cages_by_group(self):
        '''Tests if cages by group dict matches expected.'''
        self.assertEqual({'Control': ['1'], 'Group 1': ['2']}, 
                        self.db.get_cages_by_group())
