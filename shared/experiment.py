'''Experiment Module'''
import uuid
from datetime import date
from shared.password_utils import PasswordManager
from databases.experiment_database import ExperimentDatabase

class Experiment():
    '''Experiment Data Object'''
    def __init__(self):

        self.name = ''
        self.investigators = []
        self.species = ''
        self.item = ''
        self.id = ''
        self.rfid = False
        self.num_animals = ''
        self.num_cages = '0'
        self.max_per_cage = ''
        self.animals_per_cage = ''
        self.cage_names = []
        self.data_collect_type = []
        self.date_created = str(date.today())
        self.password = None

        self.cage_num_changed = False
        self.measurement_items_changed = False

    def set_name(self, name):
        '''Sets name.'''
        self.name = name

    def set_investigators(self, invest):
        '''Sets investigators.'''
        self.investigators = invest

    def set_species(self, species):
        '''Sets species.'''
        self.species = species

    def set_measurement_item(self, items):
        '''Sets measurement items.'''
        self.item = items

    def set_uses_rfid(self, rfid):
        '''Sets if experiment uses rfid.'''
        self.rfid = rfid

    def set_num_animals(self, num):
        '''Set number of animals.'''
        self.num_animals = num

    def set_num_cages(self, num):
        '''Set number of cages.'''
        if self.num_cages != num:
            self.num_cages = num
            self.cage_num_changed = True

    def set_max_animals(self, num):
        '''Set max animals per cage.'''
        self.max_per_cage = num

    def set_unique_id(self):
        '''Set unique id.'''
        unique_id = uuid.uuid1()
        self.id = str(unique_id)

    def set_cage_names(self, names):
        '''Sets cage names.'''
        self.cage_names = names

    def set_collection_types(self, data_type):
        '''Sets collection types.'''
        self.data_collect_type = data_type

    def set_animals_per_cage(self, num):
        '''Sets animals per cage.'''
        self.animals_per_cage = num

    def set_password(self, password):
        '''Sets password.'''
        self.password = password

    def set_cage_num_changed_false(self):
        '''Sets cage number changed to false.'''
        self.cage_num_changed = False

    def set_measurement_items_changed_false(self):
        '''Sets measurement items changed to false.'''
        self.measurement_items_changed = False

    def get_name(self):
        '''Returns the name of experiment.'''
        return self.name

    def get_investigators(self):
        '''Returns the list of investigators of the experiment.'''
        return self.investigators

    def get_species(self):
        '''Returns the mouse species of the experiment.'''
        return self.species

    def get_measurement_items(self):
        '''Returns the list of measurement items of the experiment.'''
        return self.item

    def uses_rfid(self):
        '''Returns if experiment uses RFID.'''
        return self.rfid

    def get_num_animals(self):
        '''Returns number of animals of experiment.'''
        return self.num_animals

    def get_num_cages(self):
        '''Returns the number of cages in experiment.'''
        return self.num_cages

    def get_max_animals(self):
        '''Returns the maximum number of animals per cage in experiment.'''
        return self.max_per_cage

    def get_cage_names(self):
        '''Returns the list of cage names in experiment.'''
        return self.cage_names

    def get_collection_types(self):
        '''Return list of collection types in experiment.'''
        return self.data_collect_type

    def get_password(self):
        '''Returns password.'''
        return self.password

    def check_cage_num_changed(self):
        '''Returns if cage number has changed.'''
        return self.cage_num_changed

    def check_measurement_items_changed(self):
        '''Returns if measurement items have changed.'''
        return self.measurement_items_changed

    def save_to_database(self, directory: str):
        '''Saves experiment object to a file.'''
        if self.password:
            file = directory + '/' + self.name + '.pmouser'
        else:
            file = directory + '/' + self.name + '.mouser'
        
        db = ExperimentDatabase(file)
        
        # Convert measurement types to strings if they're tuples
        measurement_types = [item[0] if isinstance(item, tuple) else item 
                            for item in self.data_collect_type]
        
        # Setup experiment with measurement_type from data_collect_type
        db.setup_experiment(
            name=self.name,
            species=self.species,
            uses_rfid=self.rfid,
            num_animals=self.num_animals,
            num_groups=self.num_cages,
            cage_max=self.max_per_cage,
            measurement_type=self.measurement_type,
            experiment_id=self.id,
            investigators=self.investigators,
            measurement=self.item
        )
        
        # Setup cages with cage capacity
        db.setup_cages(
            cage_names=self.cage_names,
            cage_capacity=self.max_per_cage
        )
        
        if self.password:
            manager = PasswordManager(self.password)
            manager.encrypt_file(file)
        # TO:DO save date created to db
        
    def get_measurement_type(self):
        '''Returns whether measurements are automatic.'''
        return hasattr(self, 'measurement_type') and self.measurement_type == 1

    def set_measurement_type(self, is_automatic: int):
        '''Sets whether measurements are automatic (1) or manual (0).'''
        self.measurement_type = is_automatic

    def add_investigator(self, investigator_name):
        if investigator_name and investigator_name not in self.investigators:
            self.investigators.append(investigator_name)
        