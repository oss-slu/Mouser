'''Contains DatabaseController Class'''
import copy
from database_apis.experiment_database import ExperimentDatabase

class DatabaseController():
    '''A controller that provides functions for manipulating the data within a .mouser file'''
    def __init__(self, database):

        file = database
        self.db = ExperimentDatabase(file)

        # self.measurement_items = self.db.get_measurement_items()
        self.measurement_items = ['Weight']

        self.reset_attributes()


    def set_cages_in_group(self):
        '''Returns the a dictionary with the keys are the group ids and 
        the values are the cage ids in each group in the database.

        Ex: set_cages_in_group()[group_id] = [cage_1, cage_2, ...]
        '''
        return self.db.get_cages_by_group()


    def set_animals_in_cage(self):
        '''Returns the a dictionary with the keys are the cage ids and 
        the values are the animal ids in each cage in the database.

        Ex: set_animals_in_cage()[cage_id] = [animal_1, animal_2, ...]
        '''
        return self.db.get_animals_by_cage()


    def reset_attributes(self):
        ''' reset's the attribute lists so configuration in ui can be saved, 
            the page can be exited, and then visited again displaying the new config   
            without destroying all objects 
        '''
        self.cages_in_group = self.set_cages_in_group()    # {group : [cage ids]}
        self.animals_in_cage = self.set_animals_in_cage()   # {cage : [animal ids]}
        self.valid_ids = self.db.get_all_animal_ids()      # [id, id, id, ...]

        # adding weights while not connected to the data collection database
        # when weights connected, add db call to get animal weight for animal id
        self.animal_weights = {}          # {animalId : 'weight'}
        counter = 1
        for animal in self.valid_ids:
            self.animal_weights[int(animal)] = counter
            counter += 1


    def get_groups(self):
        '''Returns a list of all group names in the database.'''
        raw_groups = self.db.get_all_groups()
        groups = []
        for group in raw_groups:
            name = group[0]
            groups.append(name)

        return groups

    def get_num_cages(self):
        '''Returns the number of cages in the database.'''
        num = len(self.db.get_cages())
        return num

    def get_cage_max(self):
        '''Returns the maximum size of the cages in the database.'''
        cage_max = int(self.db.get_cage_max())
        return cage_max

    def get_measurement_items(self):
        '''Returns a list of all measurement items in the database.'''
        return self.measurement_items

    def get_cages_in_group(self, group):
        '''Returns a list of all cage ids in the specified group.'''
        if group in self.cages_in_group.keys():
            return self.cages_in_group[group]
        return []

    def get_animals_in_cage(self, cage):
        '''Returns a list of animal ids in the specified cage.'''
        if cage in self.animals_in_cage.keys():
            return self.animals_in_cage[cage]
        return []


    def get_animal_measurements(self, animal_id):
        '''Returns a list of the measurements of the specified animal_id.'''
        return self.animal_weights[int(animal_id)]

    def get_animal_current_cage(self, animal_id):
        '''Returns the cage id of the specied animal id.'''
        keys = self.animals_in_cage.keys()
        cages = [self.animals_in_cage[key] for key in keys]

        for num in range(0,len(cages)):
            if animal_id in cages[num]:
                return str(num+1)


    def check_valid_animal(self, animal_id):
        '''Returns true if the specified animal id is valid and false otherwise.'''
        return animal_id in self.valid_ids

    def check_valid_cage(self, cage):
        '''Returns true if the specified cage is valid and false otherwise.'''
        return int(cage) <= self.get_num_cages()

    def check_num_in_cage_allowed(self):
        '''Returns false if there are more animals in cages than the maximum cage size.'''
        max_allowed = 0
        for animals in self.animals_in_cage.values():
            if len(animals) > max_allowed:
                max_allowed = len(animals)

        return max_allowed <= self.get_cage_max()

    def update_animal_cage(self, animal, old_cage, new_cage):
        '''Removes specified animal from the first cage to the second cage.'''
        self.animals_in_cage[old_cage].remove(animal)
        self.animals_in_cage[new_cage].append(animal)

    def get_updated_animals(self):
        '''Returns a list of tuples in the format
        (old_animal_id, new_animal_id, new_group, new_cage)
        
        This formoat is used to update the database.
        '''
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

    def autosort(self):
        '''Autosorts the animals in the database into cages and groups.'''
        num_animals = int(self.db.get_number_animals())
        num_groups = int(self.db.get_number_groups())
        cage_max = self.get_cage_max()

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
        for i in range(1, num_groups+1):
            #i is the group for which we are currently putting the animals into cages
            group = [item for item in animals_grouped if item[1] == i]
            m = 0
            '''m tracks the number of animals in a cage to see if we
            have hit the maxium number of animals in a cage'''
            for k in group:
                #k refers to the animal in each group
                if m == cage_max:
                    cage += 1
                    m = 1
                else:
                    m += 1
                animals_sorted.append( (k[0], k[1], cage) )
                #k[0] is animal id, k[1] is animal group
            cage += 1

        temp_animals_in_cage = copy.deepcopy(self.animals_in_cage)

        for key, value_list in temp_animals_in_cage.items():
            for value in value_list:
                index = animals_sorted.index(
                    next(item for item in animals_sorted if str(item[0]) == value)
                    )
                self.update_animal_cage(value, key, str(animals_sorted[index][2]))
                #update_animal_cage(self, animal, old_cage, new_cage)

    def update_experiment(self):
        '''Updates the database to reflect current animal states.'''
        updated_animals = self.get_updated_animals()
        self.db.update_animals(updated_animals)
        self.reset_attributes()

    def close(self):
        '''Closes the database file.'''
        self.db.close()
