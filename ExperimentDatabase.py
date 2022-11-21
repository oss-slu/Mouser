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
                                cage_max INTEGER
                                );''')
            self._c.execute('''CREATE TABLE animals (
                                experiment_id INTEGER,
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                cage_id INTEGER,
                                remarks TEXT,
                                active INTEGER
                                );''')
            self._c.execute('''CREATE TABLE groups (
                                experiment_id INTEGER,
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER
                                );''')
            self._c.execute('''CREATE TABLE cages (
                                experiment_id INTEGER,
                                cage_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                num_animals INTEGER
                                );''')
            self._c.execute('''CREATE TABLE measurement_items (
                                experiment_id INTEGER,
                                measurement_id INTEGER PRIMARY KEY,
                                item TEXT,
                                auto INTEGER
                                );''')
            self._c.execute('''CREATE TABLE animal_rfid (
                                experiment_id INTEGER,
                                animal_id INTEGER PRIMARY KEY,
                                rfid TEXT UNIQUE
                                );''')
            self._conn.commit()
        except sqlite3.OperationalError:
            print('Tables already exist')

 
    def setup_experiment(self, name, species, uses_rfid, num_animals, num_groups, cage_max):
        self._c.execute(''' INSERT INTO experiment (name, species, uses_rfid, num_animals, num_groups, cage_max) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (name, species, uses_rfid, num_animals, num_groups, cage_max))
        self._conn.commit()

    def setup_groups(self, group_names, animals_per_group):
        for group in group_names:
            self._c.execute(''' INSERT INTO groups (name, num_animals) 
                                VALUES (?, ?)''',
                                (group, animals_per_group))
            self._conn.commit()

    def setup_measurement_items(self, items): #items is a list of tuples where each tuple contains the measurement item and true (1) for automatic input or false (0) for manual
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
        self._c.execute("INSERT INTO animals (animal_id, group_id, cage_id, remarks, active) VALUES (?, ?, ?, ?, True)", (animal_id, group_id, cage_id, remarks))
        self._conn.commit()


    def get_animals(self):
        self._c.execute("SELECT animal_id, group_id, cage_id, active FROM animals")
        return self._c.fetchall()

    def get_animal_id(self, rfid):
        self._c.execute("SELECT animal_id FROM animal_rfid WHERE rfid=?", (rfid,))
        return self._c.fetchone()[0]


    def update_group_and_cage(self, animal_id, new_group, new_cage):
        self._c.execute("UPDATE animals SET group_id=?, cage_id=? WHERE animal_id=?", (new_group, new_cage, animal_id))
        self._conn.commit()

    def deactivate_animal(self, animal_id):
        self._c.execute("UPDATE animals SET active=0 WHERE animal_id=?", (animal_id,))
        self._conn.commit()

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
    print(db.get_animal_id(1234))
    print(db.get_animals())
    db.update_group_and_cage(1, 3, 3)
    db.deactivate_animal(2)
    print(db.get_animals())
