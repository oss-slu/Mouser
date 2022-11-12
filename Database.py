import sqlite3

class Database:
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
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                cage_id INTEGER,
                                remarks TEXT
                                );''')
            self._c.execute('''CREATE TABLE groups (
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER
                                );''')
            self._c.execute('''CREATE TABLE cages (
                                cage_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                num_animals INTEGER
                                );''')
            self._c.execute('''CREATE TABLE measurement_items (
                                measurement_id INTEGER PRIMARY KEY,
                                item TEXT,
                                auto INTEGER
                                );''')
            self._c.execute('''CREATE TABLE conversion (
                                animal_id INTEGER PRIMARY KEY,
                                rfid TEXT UNIQUE
                                );''')
            self._conn.commit()
        except sqlite3.OperationalError:
            print('Tables already exist')

 
    def create_experiment(self, name, species, uses_rfid, num_animals, group_names, cage_max):
        #insert into experiment table
        num_groups = len(group_names)
        self._c.execute(''' INSERT INTO experiment (name, species, uses_rfid, num_animals, num_groups, cage_max) 
                            VALUES (?, ?, ?, ?, ?, ?)''',
                            (name, species, uses_rfid, num_animals, num_groups, cage_max))
        self._conn.commit()

        #insert into groups table
        animals_per_group = num_animals / num_groups
        for group_name in group_names:
            self._c.execute(''' INSERT INTO groups (name, num_animals) 
                                VALUES (?, ?)''',
                                (group_name, animals_per_group))
            self._conn.commit()
            
        #insert into cage table

        #insert into measurement items table
        
        

    def add_animal(self, rf):
        self._c.execute("INSERT INTO conversion (rfid) VALUES (?)", (rf, ))
        self._conn.commit()

    def get_all_animals(self):
        self._c.execute("SELECT * FROM conversion")
        return self._c.fetchall()

    def get_animal_id(self, rf):
        self._c.execute("SELECT animal_id FROM conversion WHERE rfid=?", (rf,))
        return self._c.fetchone()[0]

    def close(self):
        self._conn.close()


if __name__ == "__main__":
    db = Database()
    db.create_experiment('CancerDrug', 'Hamster', 1, 90, ('Control', 'Drug A', 'Drug B'), 5)

    db.add_animal(1234)
    db.add_animal(4562)
    db.add_animal(4682)
    db.add_animal(5782)
    print(db.get_animal_id(1234))
    print(db.get_all_animals())
