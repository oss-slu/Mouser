'''Contains DatabaseController Class'''
# pylint: disable=too-many-instance-attributes, too-many-public-methods

import databases.experiment_database as edb


class DatabaseController:
    '''A controller that provides functions for manipulating data within a .mouser file'''

    def __init__(self, database=None, db=None):
        '''Initialize the controller with an ExperimentDatabase or a test double.'''
        if db is not None:
            self.db = db
        else:
            self.db = edb.ExperimentDatabase(database)

        self.measurement_items = self.db.get_measurement_items()
        self.reset_attributes()

    def set_cages_in_group(self):
        '''Return dict mapping group IDs to cage IDs'''
        return self.db.get_cages_by_group()

    def set_animals_in_cage(self):
        '''Return dict mapping cage IDs to list of animals'''
        cage_assignments = self.db.get_cage_assignments()
        animals_in_cage = {}

        for animal_id, cage_number in cage_assignments.items():
            cage_key = str(cage_number)
            animals_in_cage.setdefault(cage_key, []).append(str(animal_id))

        return animals_in_cage

    def reset_attributes(self):
        '''Reset internal attributes for cage/group/measurement tracking'''
        self.cages_in_group = self.set_cages_in_group()
        self.animals_in_cage = self.set_animals_in_cage()
        self.valid_ids = [str(a[0]) for a in self.db.get_animals()]

        # Build animal weight lookup
        self.animal_weights = {}
        measurements = self.db.get_measurements_by_date(None)

        for animal_id in self.valid_ids:
            found = False
            if measurements:
                for measurement in measurements:
                    if str(measurement[0]) == animal_id:
                        self.animal_weights[int(animal_id)] = measurement[3]
                        found = True
                        break
            if not found:
                self.animal_weights[int(animal_id)] = 0

    def get_groups(self):
        '''Return list of groups'''
        return self.db.get_groups()

    def get_num_cages(self):
        '''Return total number of cages'''
        return sum(len(cages) for cages in self.cages_in_group.values())

    def get_cage_max(self):
        '''Return maximum allowed animals per cage'''
        # pylint: disable=protected-access
        self.db._conn.execute("SELECT cage_max FROM experiment")
        result = self.db._conn.fetchone()
        return int(result[0]) if result else 0

    def get_animals_in_group(self, group_name):
        '''Return animals in the given group'''
        return self.db.get_animals_in_cage(group_name)

    def get_measurement_items(self):
        '''Return measurement item list'''
        return self.measurement_items

    def get_cage_number(self, cage_name):
        '''Return internal numeric cage ID'''
        return self.db.get_cage_number(cage_name)

    def autosort(self):
        '''Run autosort routine'''
        self.db.autosort()

    def randomize_cages(self):
        '''Randomize animal-to-cage assignments'''
        self.db.randomize_cages()

    def get_animals_in_cage(self, cage):
        '''Return animal list in given cage'''
        return self.animals_in_cage.get(cage, [])

    def get_animal_measurements(self, animal_id):
        '''Return latest recorded measurement'''
        return self.animal_weights[int(animal_id)]

    def get_animal_current_cage(self, animal_id):
        '''Return cage currently assigned to animal'''
        return self.db.get_animal_current_cage(animal_id)

    def check_valid_animal(self, animal_id):
        '''Return True if animal ID exists'''
        return animal_id in self.valid_ids

    def check_valid_cage(self, cage):
        '''Return True if cage exists'''
        return str(cage) in self.animals_in_cage

    def check_num_in_cage_allowed(self):
        '''Return False if any cage exceeds capacity'''
        cage_max = self.get_cage_max()
        return all(len(animals) <= cage_max for animals in self.animals_in_cage.values())

    def update_animal_cage(self, animal_id, new_cage):
        '''Move animal to a new cage'''
        return self.db.update_animal_cage(animal_id, new_cage)

    def get_updated_animals(self):
        '''Return list of updated animal positions for DB update'''
        updated = []
        new_id = 1
        group = 1

        for cages in self.cages_in_group.values():
            for cage in cages:
                for animal in self.animals_in_cage[str(cage)]:
                    updated.append((int(animal), new_id, group, int(cage)))
                    new_id += 1
            group += 1

        return updated

    def update_experiment(self):
        '''Apply updates to experiment file'''
        updated_animals = self.get_updated_animals()
        self.db.update_experiment(updated_animals)
        self.reset_attributes()

    def commit(self):
        '''Commit database changes'''
        # pylint: disable=protected-access
        self.db._conn.commit()

    def close(self):
        '''Close underlying database'''
        self.db.close()
