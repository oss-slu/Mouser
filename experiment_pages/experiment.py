import csv
from datetime import date
from database_apis.experiment_database import ExperimentDatabase
from datetime import date

class Experiment():
    def __init__(self):

        self.name = ''
        self.investigators = []
        self.species = ''
        self.items = []
        self.rfid = False
        self.num_animals = ''
        self.num_groups = '0'
        self.max_per_cage = ''
        self.animals_per_group = ''
        self.group_names = []
        self.data_collect_type = []
        self.date_created = str(date.today())

    def get_name(self):
        return self.name


    def get_investigators(self):
        return self.investigators


    def get_species(self):
        return self.species


    def get_measurement_items(self):
        return self.items


    def uses_rfid(self):
        return self.rfid


    def get_num_animals(self):
        return self.num_animals


    def get_num_groups(self):
        return self.num_groups


    def get_max_animals(self):
        return self.max_per_cage

    
    def get_group_names(self):
        return self.group_names


    def get_collection_types(self):
        return self.data_collect_type


    def add_to_list(self):
        with open('./created_experiments.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.name, self.date_created])
            f.close()


    def save_to_database(self):
        self.add_to_list()
        file = "databases/experiments/" + self.name + '.db'
        db = ExperimentDatabase(file)
        db.setup_experiment(self.name, self.species, self.rfid, self.num_animals, 
                            self.num_groups, self.max_per_cage)
        db.setup_groups(self.group_names)
        db.setup_cages(self.num_animals, self.num_groups, self.max_per_cage)
        db.setup_measurement_items(self.data_collect_type)
        
        # TO:DO save date created to db

        