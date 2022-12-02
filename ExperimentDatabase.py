import sqlite3

class ExperimentDatabase:
    def __init__(self, file=":memory:"):  #call with file name as argument or no args to use memory
        self._conn = sqlite3.connect(file)
        self._c = self._conn.cursor()
        try:
            self._c.execute('''CREATE TABLE experiment (
                                experiment_id INTEGER PRIMARY KEY,
                                name TEXT,
                                species TEXT,
                                uses_rfid INTEGER,
                                num_animals INTEGER,
                                num_groups INTEGER,
                                cage_max INTEGER);''')
            self._c.execute('''CREATE TABLE animals (
                                experiment_id INTEGER,
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                cage_id INTEGER,
                                remarks TEXT,
                                active INTEGER,
                                weight INTEGER);''')
            self._c.execute('''CREATE TABLE groups (
                                experiment_id INTEGER,
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER);''')
            self._c.execute('''CREATE TABLE cages (
                                experiment_id INTEGER,
                                cage_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                num_animals INTEGER);''')
            self._c.execute('''CREATE TABLE measurement_items (
                                experiment_id INTEGER,
                                measurement_id INTEGER PRIMARY KEY,
                                item TEXT,
                                auto INTEGER);''')
            self._c.execute('''CREATE TABLE animal_rfid (
                                experiment_id INTEGER,
                                animal_id INTEGER PRIMARY KEY,
                                rfid TEXT UNIQUE);''')
            self._conn.commit()
        except sqlite3.OperationalError:
            print('Tables already exist')


    def setup_experiment(self, name, species, uses_rfid, num_animals, num_groups, cage_max):
        self._c.execute(''' INSERT INTO experiment (name, species, uses_rfid, num_animals, num_groups, cage_max) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (name, species, uses_rfid, num_animals, num_groups, cage_max))
        self._conn.commit()

    def setup_groups(self, group_names, animals_per_group):
        '''Adds the groups to the database.
            arg1 (list): a list of all the group names
            arg2 (int): a number representing the number of animals per group
        '''
        for group in group_names:
            self._c.execute(''' INSERT INTO groups (name, num_animals) 
                                VALUES (?, ?)''',
                                (group, animals_per_group))
            self._conn.commit()

    def setup_measurement_items(self, items):
        '''Adds the measurement items to the database.
        
        arg1 (list of tuples):  First item in the tuple is the name of the measurement item
                                Second item in the tuple is a true or false indicating whether or not the item will be input automatically or manually
                                    (True or 1 for automatic and False or 0 for manual)
        '''
        for item in items:
            self._c.execute(''' INSERT INTO measurement_items (item, auto) 
                                VALUES (?, ?)''',
                                (item[0], item[1]))
            self._conn.commit()   

    def setup_cages(self):
        pass



    def add_animal(self, rfid, group_id, cage_id, remarks=''):
        self._c.execute("INSERT INTO animal_rfid (rfid) VALUES (?)", (rfid, ))
        self._conn.commit()
        animal_id = self.get_animal_id(rfid)
        self._c.execute("INSERT INTO animals (animal_id, group_id, cage_id, remarks, active) VALUES (?, ?, ?, ?, True)",
                        (animal_id, group_id, cage_id, remarks))
        self._conn.commit()



    def update_group_and_cage(self, animal_id, new_group, new_cage):
        self._c.execute("UPDATE animals SET group_id=?, cage_id=? WHERE animal_id=?", (new_group, new_cage, animal_id))
        self._conn.commit()

    def deactivate_animal(self, animal_id):
        self._c.execute("UPDATE animals SET active=0 WHERE animal_id=?", (animal_id,))
        self._conn.commit()
    

    def update_animals(self, animals):
        ''' Updates animal ids, groups, and cages
        arg1 list of tuples: each tuple contains 4 items (old animal id, new animal id, new group, new cage)
            the tuple should contain all the animals even if one animal does not change
        '''
        offset=10000
        i=1
        while i <= len(animals):
            self._c.execute("UPDATE animals SET animal_id=? WHERE animal_id=?", (i+offset, i))
            self._c.execute("UPDATE animal_rfid SET animal_id=? WHERE animal_id=?", (i+offset, i))
            self._conn.commit()
            i+=1

        for animal in animals:
            self._c.execute("UPDATE animals SET animal_id=?, group_id=?, cage_id=? WHERE animal_id=?", (animal[1], animal[2], animal[3], animal[0]+offset))
            self._c.execute("UPDATE animal_rfid SET animal_id=? WHERE animal_id=?", (i+offset, i))
            self._conn.commit()

    def get_all_groups(self):
        self._c.execute("SELECT name FROM groups")
        return self._c.fetchall()

    def get_cages(self):
        self._c.execute("SELECT cage_id, group_id FROM cages")
        return self._c.fetchall()

    def get_animals_in_cage(self, cage_id):
        self._c.execute("SELECT animal_id FROM animals WHERE cage_id=?", (cage_id, ))
        return self._c.fetchall()
    
    def get_animals_in_group(self, group_id):
        self._c.execute("SELECT animal_id FROM animals WHERE group_id=?", (group_id, ))
        return self._c.fetchall()

    def get_animals_in_cage(self, cage_id):
        self._c.execute("SELECT animal_id FROM animals WHERE cage_id=?", (cage_id, ))
        return self._c.fetchall()
    
    def get_animals_in_group(self, group_id):
        self._c.execute("SELECT animal_id FROM animals WHERE group_id=?", (group_id, ))
        return self._c.fetchall()

    def get_animals(self):
        self._c.execute("SELECT animal_id, group_id, cage_id, weight, active FROM animals")
        return self._c.fetchall()

    def get_animal_id(self, rfid):
        self._c.execute("SELECT animal_id FROM animal_rfid WHERE rfid=?", (rfid,))
        return self._c.fetchone()[0]

    def get_all_experiment_info(self):
        self._c.execute("SELECT name, species, uses_rfid, num_animals, num_groups, cage_max FROM experiment")
        print('Experiment: name, species, uses_rfid, num_animals, num_groups, cage_max')
        print(self._c.fetchall())
        self._c.execute("SELECT name, num_animals  FROM groups")
        print('Groups: name, num_animals')
        print(self._c.fetchall())
        self._c.execute("SELECT item, auto FROM measurement_items")
        print('Measurement Items: item, auto')
        print(self._c.fetchall())

    def close(self):
        self._conn.close()



if __name__ == "__main__":
    db = ExperimentDatabase()
    db.setup_experiment('CancerDrug', 'hampster', True, 60, 3, 5)
    db.setup_groups(('Control', 'Drug A', 'Drug B'), 20)
    db.setup_measurement_items([('Weight', True), ('Length', True)])
    
    db.add_animal(1234, 1, 1)
    db.add_animal(4562, 1, 1)
    db.add_animal(4682, 1, 2)
    db.add_animal(5782, 1, 2, 'missing left front leg')
    
    #print(db.get_animal_id(1234))
    print(db.get_animals())
    #db.update_group_and_cage(1, 3, 3)
    #db.deactivate_animal(2)
    db.update_animals( [ (3, 1, 1, 1), (2, 2, 1, 1), (4, 3, 2, 2), (1, 4, 2, 2) ] )
    print(db.get_animals())
    #db.get_all_experiment_info()