from ExperimentDatabase import ExperimentDatabase

class DatabaseController():
    def __init__(self, database):
        
        file = str(database) + '.db'
        self.db = ExperimentDatabase(file)

        # self.measurement_items = self.db.get_measurement_items()

        # # WORKING DATABASE CALLS (go live when animal data is able to be entered)
        # self.cages_in_group = self.set_cages_in_group()    # {group : [cage ids]}
        # self.animals_in_cage = self.set_animals_in_cage()   # {cage : [animal ids]}
        # self.valid_ids = self.db.get_all_animal_ids()

        ### temporary dummy vars ###
        self.measurement_items = ['Weight']
        self.cages_in_group = {'Group A': ['1', '2', '3', '4', '5'], 'Group B': ['6', '7', '8', '9', '10']}
        self.animals_in_cage = {'1': ['1', '2'], '2': ['3', '4'], '3': ['5', '6'], '4': ['7', '8'], 
                             '5': ['9', '10'], '6': ['11', '12'], '7': ['13', '14'], '8': {'15', '16'}, 
                             '9': ['17', '18'], '10': ['19', '20']}
        
        self.animal_weights = {}
        self.valid_ids = []
        for i in range(1, 21):
            self.animal_weights[i] = '0'
            self.valid_ids.append(str(i))
        ############################        


    def set_cages_in_group(self):
        return(self.db.get_cages_by_group())


    def set_animals_in_cage(self):
        return(self.db.get_animals_by_cage())


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
        return(self.measurement_items)


    def get_cages_in_group(self, group):
        return (self.cages_in_group[group])


    def get_animals_in_cage(self, cage):
        return(self.animals_in_cage[cage])


    def get_animal_measurements(self, animal_id):
        return(self.animal_weights[int(animal_id)])
    

    def get_animal_current_cage(self, id):
        keys = self.animals_in_cage.keys()
        cages = [self.animals_in_cage[key] for key in keys]
        
        for num in range(0,len(cages)):
            if id in cages[num]:
                return(str(num+1))


    def check_valid_animal(self, id):
        if id in self.valid_ids:
            return(True)
        else:
            return(False)


    def check_valid_cage(self, cage):
        if int(cage) <= self.get_num_cages():
            return(True)
        else:
            return(False)


    def update_animal_cage(self, animal, old_cage, new_cage):
        # print('before: ', self.animals_in_cage[old_cage])
        self.animals_in_cage[old_cage].remove(animal)
        # print('after removal: ', self.animals_in_cage[old_cage])
        self.animals_in_cage[new_cage].append(animal)
        # print('after add to new: ', self.animals_in_cage[new_cage])


    def update_experiment(self):
        # stored & updated values in self.animals_in_cage
        # save to database
        self.close_db


    def close_db(self):
        self.db.close()




if __name__ == '__main__':
    controller = DatabaseController('Cancer Drug')

    # print(controller.get_cages_in_group('Group B'))
    print(controller.get_animals_in_cage('5'))
    print(controller.update_animal_cage('2', '1', '2'))



 
