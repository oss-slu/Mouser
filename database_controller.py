from database_apis.experiment_database import ExperimentDatabase
import copy

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
                             '5': ['9', '10'], '6': ['11', '12'], '7': ['13', '14'], '8': ['15', '16'], 
                             '9': ['17', '18'], '10': ['19', '20']}
        
        self.animal_weights = {1: '80', 2: '73', 3: '65', 4: '66', 5: '66', 6: '69', 7: '89', 
                                8: '74', 9: '70', 10: '75', 11: '70', 12: '66', 13: '80', 
                                14: '72', 15: '80', 16: '90', 17: '76', 18: '87', 19: '90', 20: '65'}

        self.valid_ids = []
        for i in range(1, 21):
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


    def update_animal_cage(self, animal, old_cage, new_cage):
        # print('before: ', self.animals_in_cage[old_cage])
        self.animals_in_cage[old_cage].remove(animal)
        # print('after removal: ', self.animals_in_cage[old_cage])
        self.animals_in_cage[new_cage].append(animal)
        # print('after add to new: ', self.animals_in_cage[new_cage])

    def get_updated_animals(self):
        updated_animals = []
        new_id = 1
        group = 1
        for cages in self.cages_in_group.values():
            for cage in cages:
                animals = self.animals_in_cage[cage]
                for animal in animals:
                    updated_animals.append((int(animal), new_id, group, int(cage)))
                    new_id += 1
            group += 1
        return updated_animals
        #get animals into format to update database [(old_animal_id, new_aniaml_id, new_group, new_cage), ...]

    def autosort(self):
        num_animals = int(self.db.get_number_animals())
        num_groups = int(self.db.get_number_groups())
        cage_max = int(self.db.get_cage_max())

        animal_weights_sorted = sorted(self.animal_weights.items(), key=lambda item: item[1])

        animals_grouped = []
        g = 1 #g determines the group the animal will be assigned to
        for i in range(1, num_animals+1):
            idx = i 
            animals_grouped.append((animal_weights_sorted[idx-1][0], g))
            if i % (num_groups*2) == 0:
                g = 1
            elif i % (num_groups*2) > num_groups:
                g -= 1
            elif i % (num_groups*2) < num_groups:
                g += 1

        animals_sorted = []
        cage = 1
        for i in range(1, num_groups+1): #i is the group for which we are currently putting the animals into cages
            group = [item for item in animals_grouped if item[1] == i]
            m = 0 #m tracks the number of animals in a cage to see if we have hit the maxium number of animals in a cage
            for k in group: #k refers to the animal in each group
                if m == cage_max:
                    cage += 1
                    m = 1
                else:
                    m += 1
                animals_sorted.append( (k[0], k[1], cage) ) #k[0] is animal id, k[1] is animal group
            cage += 1

        temp_animals_in_cage = copy.deepcopy(self.animals_in_cage)

        for key, value_list in temp_animals_in_cage.items():
            for value in value_list:
                index = animals_sorted.index(next(item for item in animals_sorted if str(item[0]) == value))
                self.update_animal_cage(value, key, str(animals_sorted[index][2])) #update_animal_cage(self, animal, old_cage, new_cage)

    def update_experiment(self, updated_animals):
        self.db.update_animals(updated_animals)
        self.close_db


    def close_db(self):
        self.db.close()




if __name__ == '__main__':
    controller = DatabaseController('Cancer Drug')

    # print(controller.get_cages_in_group('Group B'))
    print(controller.get_animals_in_cage('5'))
    print(controller.update_animal_cage('2', '1', '2'))



 
