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
        

    def get_num_cages(self):
        num = len(self.db.get_cages())
        return(num)


    def get_measurement_items(self):
        # temporary for demo
        return(['Weight'])
        # return(self.db.get_measurement_items())


    # demo purposes only until db insert working
    def make_temporary_cages(self):
        group_cages = {'Group A': ('1', '2', '3', '4', '5'), 'Group B': ('6', '7', '8', '9', '10')}
        return (group_cages)


    def get_cages_in_group(self, group):
        # temporary call
        groups_and_cages = self.make_temporary_cages()
        return (groups_and_cages[group])


    def get_animals_in_cage(self, cage):
        # temporary until db insert working
        cages_and_animals = {'1': ('1', '2'), '2': ('3', '4'), '3': ('5', '6'), '4': ('7', '8'), 
                             '5': ('9', '10'), '6': ('11', '12'), '7': ('13', '14'), '8': ('15', '16'), 
                             '9': ('17', '18'), '10': ('19', '20')}
        return(cages_and_animals[cage])


    # def get_animals_in_cage(self, cage_id):
    #     return(self.db.get_animals_in_cage(cage_id))


    def make_temp_measurements(self):
        # temporary data for demo
        animal_weights = {}
        for i in range(1, 21):
            animal_weights[i] = '0'
        return(animal_weights)


    def get_animal_measurements(self, animal_id):
        weights = self.make_temp_measurements()
        return(weights[int(animal_id)])


    # def get_animal_measurements(self, animal_id):
    #     return(self.db.get_animal_measurements(animal_id))


    def update_experiment(self):
        # do stuff
        self.close_db


    def close_db(self):
        self.db.close()




if __name__ == '__main__':
    controller = DatabaseController('Cancer Drug')

    # print(controller.get_cages_in_group('Group B'))
    # print(controller.get_animals_in_cage(5))
    print(controller.get_animal_measurements(4))

