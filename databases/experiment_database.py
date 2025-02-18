'''SQLite Database module for Mouser.'''
import sqlite3
import os
from datetime import datetime

class ExperimentDatabase:
    '''SQLite Database Object for Experiments.'''
    def __init__(self, file=":memory:"):  #call with file name as argument or no args to use memory
        self.db_file = file
        self._conn = sqlite3.connect(file, check_same_thread=False)
        self._c = self._conn.cursor()
        try:
            self._c.execute('''CREATE TABLE experiment (
                                name TEXT,
                                species TEXT,
                                uses_rfid INTEGER,
                                num_animals INTEGER,
                                num_groups INTEGER,
                                cage_max INTEGER,
                                measurement_type INTEGER,
                                id TEXT);''')
            
            self._c.execute('''CREATE TABLE animals (
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                rfid INTEGER UNIQUE,
                                remarks TEXT,
                                active INTEGER);''')
                                
            self._c.execute('''CREATE TABLE animal_measurements (
                                measurement_id INTEGER PRIMARY KEY,
                                animal_id INTEGER,
                                timestamp DATETIME,
                                value REAL,
                                FOREIGN KEY(animal_id) REFERENCES animals(animal_id));''')
                                
            self._c.execute('''CREATE TABLE groups (
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER,
                                cage_capacity INTEGER);''')
            
            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    def setup_experiment(self, name, species, uses_rfid, num_animals, num_groups, cage_max, measurement_type, experiment_id):
        '''Initializes Experiment.'''
        self._c.execute('''INSERT INTO experiment (name, species, uses_rfid, num_animals,
                        num_groups, cage_max, measurement_type, id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (name, species, uses_rfid, num_animals, num_groups, 
                         cage_max, measurement_type, experiment_id))
        self._conn.commit()

    def setup_groups(self, group_names, cage_capacity):
        '''Adds the groups to the database.'''
        for group in group_names:
            self._c.execute('''INSERT INTO groups (name, num_animals, cage_capacity)
                            VALUES (?, ?, ?)''',
                            (group, 0, cage_capacity))
            self._conn.commit()

    def add_measurement(self, animal_id, value):
        '''Adds a new measurement for an animal.'''
        timestamp = datetime.now()
        self._c.execute('''INSERT INTO animal_measurements (animal_id, timestamp, value)
                        VALUES (?, ?, ?)''',
                        (animal_id, timestamp, value))
        self._conn.commit()

    def get_measurements_by_date(self, date):
        '''Gets all measurements for a specific date.'''
        self._c.execute('''SELECT a.animal_id, a.rfid, m.timestamp, m.value 
                        FROM animal_measurements m
                        JOIN animals a ON m.animal_id = a.animal_id
                        WHERE DATE(m.timestamp) = ?''', (date,))
        return self._c.fetchall()

    def add_animal(self, animal_id, rfid, group_id, remarks=''):
        '''Adds animal to experiment.'''
        try:
            self._c.execute('''INSERT INTO animals (animal_id, group_id, rfid, remarks, active)
                            VALUES (?, ?, ?, ?, 1)''',
                            (animal_id, group_id, rfid, remarks))
            
            # Update group animal count
            self._c.execute('''UPDATE groups 
                            SET num_animals = num_animals + 1 
                            WHERE group_id = ?''', (group_id,))
            
            self._conn.commit()
            return animal_id
        except sqlite3.Error as e:
            print(f"Error adding animal: {e}")
            return None

    def remove_animal(self, animal_id):
        '''Removes an animal from the experiment.'''
        self._c.execute("SELECT group_id FROM animals WHERE animal_id = ?", (animal_id,))
        group_info = self._c.fetchone()
        
        if group_info:
            group_id = group_info[0]
            
            # Update group count
            self._c.execute('''UPDATE groups 
                            SET num_animals = num_animals - 1 
                            WHERE group_id = ?''', (group_id,))
            
            # Deactivate animal instead of deleting
            self._c.execute("UPDATE animals SET active = 0 WHERE animal_id = ?", (animal_id,))
            self._conn.commit()
        else:
            raise LookupError(f"No animal found with ID {animal_id}")

    def export_data(self, output_file):
        '''Exports experiment data to CSV files.'''
        import pandas as pd
        
        # Create base directory
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Export measurements with animal info
        measurements_query = '''
            SELECT 
                m.timestamp,
                a.animal_id,
                a.rfid,
                g.name as group_name,
                m.value
            FROM animal_measurements m
            JOIN animals a ON m.animal_id = a.animal_id
            JOIN groups g ON a.group_id = g.group_id
        '''
        df = pd.read_sql_query(measurements_query, self._conn)
        df.to_csv(output_file, index=False)

    def get_experiment_id(self):
        '''Returns the experiment id from the experiment table.'''
        self._c.execute("SELECT id FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else None

    def get_measurement_items(self):
        '''Returns the list of measurement items for the experiment.'''
        self._c.execute("SELECT measurement_type FROM experiment")
        result = self._c.fetchone()
        
        if result and result[0]:
            # Convert comma-separated string back to list of tuples
            measurement_types = result[0].split(',')
            # Return as list of tuples to maintain compatibility with existing code
            return [(item.strip(), item.strip()) for item in measurement_types]
        return []

    def close(self):
        '''Closes database connection.'''
        self._conn.close()

    def experiment_uses_rfid(self):
        '''Returns whether the experiment uses RFID (0 or 1).'''
        self._c.execute("SELECT uses_rfid FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else 0

    def get_animals(self):
        '''Returns a list of all active animals in the experiment.'''
        self._c.execute('''SELECT animal_id, rfid 
                        FROM animals 
                        WHERE active = 1 
                        ORDER BY animal_id''')
        return self._c.fetchall()
    
    def get_total_number_animals(self):
        '''Returns the total number of animals from the experiment table.'''
        self._c.execute("SELECT num_animals FROM experiment")
        result = self._c.fetchone()
        print(result[0])
        return result[0] if result else 0

    def get_number_animals(self):
        '''Returns the number of active animals in the database.'''
        self._c.execute("SELECT COUNT(*) FROM animals WHERE active = 1")
        result = self._c.fetchone()
        return result[0] if result else 0

    def get_animal_rfid(self, animal_id):
        '''Returns the RFID for a given animal ID.'''
        self._c.execute('SELECT rfid FROM animals WHERE animal_id = ?', (animal_id,))
        result = self._c.fetchone()
        return result[0] if result else None

    def get_animal_id(self, rfid):
        '''Returns the animal ID for a given RFID.'''
        self._c.execute('SELECT animal_id FROM animals WHERE rfid = ?', (rfid,))
        result = self._c.fetchone()
        return result[0] if result else None

    def get_data_for_date(self, date):
        '''Gets all measurements for a specific date.'''
        self._c.execute('''
            SELECT 
                a.animal_id,
                m.value,
                m.timestamp
            FROM animals a
            LEFT JOIN animal_measurements m ON a.animal_id = m.animal_id
            WHERE DATE(m.timestamp) = ? AND a.active = 1
            ORDER BY a.animal_id
        ''', (date,))
        return self._c.fetchall()

    def add_data_entry(self, entry_date, animal_id, measurements):
        '''Adds new measurement entries for an animal.'''
        for value in measurements:
            if value is not None:
                self._c.execute('''
                    INSERT INTO animal_measurements (animal_id, timestamp, value)
                    VALUES (?, ?, ?)
                ''', (animal_id, entry_date, value))
        self._conn.commit()

    def change_data_entry(self, entry_date, animal_id, measurements):
        '''Updates measurement entries for an animal.'''
        # First remove existing measurements for this date/animal
        self._c.execute('''
            DELETE FROM animal_measurements 
            WHERE animal_id = ? AND DATE(timestamp) = ?
        ''', (animal_id, entry_date))
        
        # Then add new measurements
        self.add_data_entry(entry_date, animal_id, measurements)

    def get_cages_by_group(self):
        '''Returns a dictionary of group IDs mapped to their cage information.'''
        self._c.execute('''
            SELECT group_id, name, cage_capacity 
            FROM groups
        ''')
        groups = self._c.fetchall()
        
        # Create a simulated cage structure based on group capacity
        cages_by_group = {}
        for group in groups:
            group_id, _, capacity = group
            # Create virtual cage IDs for the group based on capacity
            num_cages = (self.get_group_animal_count(group_id) + capacity - 1) // capacity
            cages_by_group[group_id] = list(range(1, num_cages + 1))
        
        return cages_by_group

    def get_group_animal_count(self, group_id):
        '''Returns the number of active animals in a group.'''
        self._c.execute('''
            SELECT COUNT(*) 
            FROM animals 
            WHERE group_id = ? AND active = 1
        ''', (group_id,))
        return self._c.fetchone()[0]

    def get_cage_capacity(self, group_id):
        '''Returns the cage capacity for a group.'''
        self._c.execute('SELECT cage_capacity FROM groups WHERE group_id = ?', (group_id,))
        result = self._c.fetchone()
        return result[0] if result else None

    def get_animals_in_cage(self, group_id, cage_number, cage_capacity):
        '''Returns animals in a virtual cage based on group and cage number.'''
        self._c.execute('''
            SELECT animal_id, rfid, remarks 
            FROM animals 
            WHERE group_id = ? AND active = 1 
            ORDER BY animal_id
            LIMIT ? OFFSET ?
        ''', (group_id, cage_capacity, (cage_number - 1) * cage_capacity))
        return self._c.fetchall()

    def get_cage_assignments(self):
        '''Returns a dictionary of animal IDs mapped to their cage assignments.'''
        cage_assignments = {}
        groups = self._c.execute('SELECT group_id, cage_capacity FROM groups').fetchall()
        
        for group_id, capacity in groups:
            animals = self._c.execute('''
                SELECT animal_id 
                FROM animals 
                WHERE group_id = ? AND active = 1 
                ORDER BY animal_id
            ''', (group_id,)).fetchall()
            
            for i, animal in enumerate(animals):
                cage_number = (i // capacity) + 1
                cage_assignments[animal[0]] = (group_id, cage_number)
        
        return cage_assignments

    def get_groups(self):
        '''Returns a list of all group names in the database.'''
        self._c.execute("SELECT name FROM groups")
        return [group[0] for group in self._c.fetchall()]

    def get_all_animals_rfid(self):
        '''Returns a list of all RFIDs for active animals in the experiment.'''
        self._c.execute('''SELECT rfid 
                        FROM animals 
                        WHERE active = 1 AND rfid IS NOT NULL 
                        ORDER BY animal_id''')
        return [rfid[0] for rfid in self._c.fetchall()]

    def get_measurement_type(self):
        '''Returns whether the measurement is automatic (1) or manual (0).'''
        self._c.execute("SELECT measurement_type FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else 0  # Default to manual (0)

    def get_all_animal_ids(self):
        '''Returns a list of all animal IDs that have RFIDs mapped to them.'''
        self._c.execute('''
            SELECT animal_id 
            FROM animals 
            WHERE rfid IS NOT NULL 
            AND active = 1
        ''')
        return [animal[0] for animal in self._c.fetchall()]



