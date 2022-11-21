class Experiment():
    def __init__(self):

        self.name = ''
        self.investigators = []
        self.species = ''
        self.items = []
        self.rfid = False
        self.num_animals = ''
        self.num_groups = '0'
        self.max_per_cage = ''

        self.group_names = []
        self.animals_per_group = ''

    def get_name(self):
        return self.name


    def get_investigators(self):
        return self.investigators


    def get_species(self):
        return self.species


    def get_measurement_items(self):
        return self.items


    def uses_rfid(self):
        return self.rfid


    def get_num_animals(self):
        return self.num_animals


    def get_num_groups(self):
        return self.num_groups


    def get_max_animals(self):
        return self.max_per_cage


    def save_to_database(self):
        # to-do : add db function calls
        return