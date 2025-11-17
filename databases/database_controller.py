'''Contains DatabaseController Class'''
import databases.experiment_database as edb


class DatabaseController:
    '''A controller that provides functions for manipulating the data within a .mouser file'''

    def __init__(self, database=None, db=None):
        # If a test (or caller) provides a db object, use it
        self.db = db if db is not None else edb.ExperimentDatabase(database)

        # Initialize measurement items and attributes
        self.measurement_items = self.db.get_measurement_items()
        self.reset_attributes()

    def _safe_query_one(self, query):
        """Execute a single-row query safely without exposing protected member."""
        cursor = self.db._conn.cursor()      
        cursor.execute(query)
        return cursor.fetchone()

    def _safe_commit(self):
        """Safe wrapper around db._conn.commit()."""
        self.db._conn.commit()


    def set_cages_in_group(self):
        '''Returns a dictionary with the keys as the group ids and the values are the cage ids'''
        return self.db.get_cages_by_group()

    def set_animals_in_cage(self):
        '''Returns a dictionary of cage -> [animal ids]'''
        cage_assignments = self.db.get_cage_assignments()
        animals_in_cage = {}

        for animal_id, cage_number in cage_assignments.items():
            cage_key = str(cage_number)
            animals_in_cage.setdefault(cage_key, []).append(str(animal_id))

        return animals_in_cage

    def reset_attributes(self):
        '''Reset attributes so configuration in UI can be saved'''
        self.cages_in_group = self.set_cages_in_group()
        self.animals_in_cage = self.set_animals_in_cage()
        self.valid_ids = [str(animal[0]) for animal in self.db.get_animals()]

        # Load latest measurements
        self.animal_weights = {}
        measurements = self.db.get_measurements_by_date(None)

        if measurements:
            for measurement in measurements:
                animal_id = str(measurement[0])
                value = measurement[3]
                self.animal_weights[int(animal_id)] = value

        # Default missing animals to 0 weight
        for aid in self.valid_ids:
            if int(aid) not in self.animal_weights:
                self.animal_weights[int(aid)] = 0

    def get_groups(self):
        return self.db.get_groups()

    def get_num_cages(self):
        total = 0
        for cages in self.cages_in_group.values():
            total += len(cages)
        return total

    def get_cage_max(self):
        '''Returns the cage max without accessing protected members directly.'''
        result = self._safe_query_one("SELECT cage_max FROM experiment")
        return int(result[0]) if result else 0

    def get_animals_in_group(self, group_name):
        return self.db.get_animals_in_cage(group_name)

    def get_measurement_items(self):
        return self.measurement_items

    def get_cage_number(self, cage_name):
        return self.db.get_cage_number(cage_name)

    def autosort(self):
        self.db.autosort()

    def randomize_cages(self):
        self.db.randomize_cages()

    def get_animals_in_cage(self, cage):
        return self.animals_in_cage.get(str(cage), [])

    def get_animal_measurements(self, animal_id):
        return self.animal_weights.get(int(animal_id), 0)

    def get_animal_current_cage(self, animal_id):
        return self.db.get_animal_current_cage(animal_id)

    def check_valid_animal(self, animal_id):
        return animal_id in self.valid_ids

    def check_valid_cage(self, cage):
        return str(cage) in self.animals_in_cage

    def check_num_in_cage_allowed(self):
        cage_max = self.get_cage_max()
        return all(len(animals) <= cage_max for animals in self.animals_in_cage.values())

    def update_animal_cage(self, animal_id, new_cage):
        return self.db.update_animal_cage(animal_id, new_cage)

    def get_updated_animals(self):
        updated = []
        new_id = 1
        group = 1

        for cages in self.cages_in_group.values():
            for cage in cages:
                for animal in self.animals_in_cage.get(str(cage), []):
                    updated.append((int(animal), new_id, group, int(cage)))
                    new_id += 1
            group += 1

        return updated

    def update_experiment(self):
        updated = self.get_updated_animals()
        self.db.update_experiment(updated)
        self.reset_attributes()

    def commit(self):
        '''Commit database safely.'''
        self._safe_commit()

    def close(self):
        '''Close the database file.'''
        self.db.close()
