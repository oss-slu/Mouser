'''Contains DatabaseController Class'''
from databases.experiment_database import ExperimentDatabase

class DatabaseController():
    '''A controller that provides functions for manipulating the data within a .mouser file'''
    def __init__(self, database):
        self.db = ExperimentDatabase(database)
        self.measurement_items = self.db.get_measurement_items()
        self.reset_attributes()

    def set_cages_in_group(self):
        '''Returns a dictionary with the keys as the group ids and
        the values are the cage ids in each group in the database.'''
        return self.db.get_cages_by_group()

    def set_animals_in_cage(self):
        '''Returns a dictionary with the keys as the cage ids and
        the values are the animal ids in each cage in the database.'''
        cage_assignments = self.db.get_cage_assignments()
        animals_in_cage = {}

        # Group animals by their assigned cage
        for animal_id, (group_id, cage_number) in cage_assignments.items():
            cage_key = str(cage_number)
            if cage_key not in animals_in_cage:
                animals_in_cage[cage_key] = []
            animals_in_cage[cage_key].append(str(animal_id))

        return animals_in_cage

    def reset_attributes(self):
        '''Reset's the attribute lists so configuration in ui can be saved'''
        self.cages_in_group = self.set_cages_in_group()    # {group : [cage ids]}
        self.animals_in_cage = self.set_animals_in_cage()   # {cage : [animal ids]}
        self.valid_ids = [str(animal[0]) for animal in self.db.get_animals()]

        # Get actual measurements from the database
        self.animal_weights = {}
        for animal_id in self.valid_ids:
            measurements = self.db.get_measurements_by_date(None)  # Get latest measurement
            if measurements:
                for measurement in measurements:
                    if str(measurement[0]) == animal_id:
                        self.animal_weights[int(animal_id)] = measurement[3]  # value
                        break
            if int(animal_id) not in self.animal_weights:
                self.animal_weights[int(animal_id)] = 0

    def get_groups(self):
        '''Returns a list of all group names in the database.'''
        return self.db.get_groups()

    def get_num_cages(self):
        '''Returns the number of cages across all groups.'''
        total_cages = 0
        for cages in self.cages_in_group.values():
            total_cages += len(cages)
        return total_cages

    def get_cage_max(self):
        '''Returns the maximum size of the cages in the database.'''
        self._c.execute("SELECT cage_max FROM experiment")
        result = self._c.fetchone()
        return int(result[0]) if result else 0

    def get_measurement_items(self):
        '''Returns a list of all measurement items in the database.'''
        return self.measurement_items

    def get_cages_in_group(self, group):
        '''Returns a list of all cage ids in the specified group.'''
        if group in self.cages_in_group:
            return self.cages_in_group[group]
        return []

    def get_animals_in_cage(self, cage):
        '''Returns a list of animal ids in the specified cage.'''
        if cage in self.animals_in_cage:
            return self.animals_in_cage[cage]
        return []

    def get_animal_measurements(self, animal_id):
        '''Returns the latest measurement of the specified animal_id.'''
        return self.animal_weights[int(animal_id)]

    def get_animal_current_cage(self, animal_id):
        '''Returns the cage id of the specified animal id.'''
        cage_assignments = self.db.get_cage_assignments()
        if int(animal_id) in cage_assignments:
            return str(cage_assignments[int(animal_id)][1])
        return None

    def check_valid_animal(self, animal_id):
        '''Returns true if the specified animal id is valid and false otherwise.'''
        return animal_id in self.valid_ids

    def check_valid_cage(self, cage):
        '''Returns true if the specified cage is valid and false otherwise.'''
        return str(cage) in self.animals_in_cage

    def check_num_in_cage_allowed(self):
        '''Returns false if there are more animals in cages than the maximum cage size.'''
        cage_max = self.get_cage_max()
        for animals in self.animals_in_cage.values():
            if len(animals) > cage_max:
                return False
        return True

    def update_animal_cage(self, animal, old_cage, new_cage):
        '''Removes specified animal from the first cage to the second cage.'''
        if animal in self.animals_in_cage[old_cage]:
            self.animals_in_cage[old_cage].remove(animal)
            self.animals_in_cage[new_cage].append(animal)

    def get_updated_animals(self):
        '''Returns a list of tuples for updating the database.'''
        updated_animals = []
        new_id = 1
        group = 1
        for cages in self.cages_in_group.values():
            for cage in cages:
                animals = self.animals_in_cage[str(cage)]
                for animal in animals:
                    updated_animals.append((int(animal), new_id, group, int(cage)))
                    new_id += 1
            group += 1
        return updated_animals

    def update_experiment(self):
        '''Updates the database to reflect current animal states.'''
        updated_animals = self.get_updated_animals()
        for old_id, new_id, group_id, cage in updated_animals:
            self.db._c.execute('''
                UPDATE animals
                SET animal_id = ?, group_id = ?
                WHERE animal_id = ?
            ''', (new_id, group_id, old_id))
        self.db._conn.commit()
        self.reset_attributes()

    def close(self):
        '''Closes the database file.'''
        self.db.close()
