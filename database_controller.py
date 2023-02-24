from ExperimentDatabase import ExperimentDatabase

class DatabaseController():
    def __init__(self, database):
        
        file = str(database) + '.db'
        self.db = ExperimentDatabase(file)


    def get_all_data(self):
        return(self.db.get_all_experiment_info())


    def get_groups(self):
        raw_groups = self.db.get_all_groups()
        groups = []
        for group in raw_groups:
            name = group[0]
            groups.append(name)

        return(groups)

    
    def get_cages(self):
        return(self.db.get_cages())


    def get_animals_in_cage(self, cage_id):
        return(self.db.get_animals_in_cage(cage_id))


    def close_db(self):
        self.db.close()







