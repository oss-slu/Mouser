from database_apis.experiment_database import ExperimentDatabase

class DatabaseController():
    def __init__(self, database):
        
        file = 'databases/experiments/' + str(database) + '.db'
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
            self.animal_weights[i] = str(i)
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


    def get_cage_max(self):
        raw_max = self.db.get_cage_max()
        max = int(raw_max[0][0])
        return(max)


    def get_measurement_items(self):
        return(self.measurement_items)


    def get_cages_in_group(self, group):
        if group in self.cages_in_group.keys():
            return (self.cages_in_group[group])
        return []


    def get_animals_in_cage(self, cage):
        if cage in self.animals_in_cage.keys():
            return(self.animals_in_cage[cage])
        return []


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
        
    
    def check_num_in_cage_allowed(self):
        max = 0
        for animals in self.animals_in_cage.values():
            if len(animals) > max:
                max = len(animals)

        if max <= self.get_cage_max():
            return True
        else:
            return False

        
    def update_animal_cage(self, animal, old_cage, new_cage):
        self.animals_in_cage[old_cage].remove(animal)
        self.animals_in_cage[new_cage].append(animal)


    def update_experiment(self):
        updated_animals_list = []
        group_id = 0
        new_animal_id = 1 # renumber animal ids so they are always in numerical order  

        for group in self.cages_in_group:
            for cage in self.cages_in_group.get(group):
                for animal in self.animals_in_cage.get(cage):
                    animal_tuple = (int(animal), new_animal_id, group_id, int(cage))
                    updated_animals_list.append(animal_tuple)
                    new_animal_id += 1
            group_id += 1

        self.db.update_animals(updated_animals_list)

