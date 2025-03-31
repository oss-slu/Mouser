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
                                id TEXT,
                                investigators TEXT,
                                measurement TEXT,
                                num_measurements INTEGER);''')

            self._c.execute('''CREATE TABLE animals (
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                rfid TEXT UNIQUE,
                                remarks TEXT,
                                active INTEGER);''')

            self._c.execute('''CREATE TABLE animal_measurements (
                                measurement_id INTEGER,
                                animal_id INTEGER,
                                timestamp TEXT,
                                value REAL,
                                FOREIGN KEY(animal_id) REFERENCES animals(animal_id),
                                PRIMARY KEY (animal_id, timestamp));''')

            self._c.execute('''CREATE TABLE groups (
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER,
                                cage_capacity INTEGER);''')

            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    def setup_experiment(self, name, species, uses_rfid, num_animals, num_groups, cage_max, measurement_type, experiment_id, investigators, measurement, num_runs):
        '''Initializes Experiment'''
        investigators_str = ', '.join(investigators)  # Convert list to comma-separated string
        self._c.execute('''INSERT INTO experiment (name, species, uses_rfid, num_animals,
                        num_groups, cage_max, measurement_type, id, investigators, measurement, num_measurements)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (name, species, uses_rfid, num_animals, num_groups,
                         cage_max, measurement_type, experiment_id, investigators_str, measurement, num_runs))
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
                            WHERE group_id = ?''', (group_id))

            # Deactivate animal instead of deleting
            self._c.execute("UPDATE animals SET active = 0 WHERE animal_id = ?", (animal_id,))
            self._conn.commit()
        else:
            raise LookupError(f"No animal found with ID {animal_id}")
        
    def find_next_available_group(self):
        '''Finds the next available group with space in its cage.'''
        self._c.execute('''SELECT group_id, num_animals, cage_capacity
                        FROM groups
                        WHERE num_animals < cage_capacity
                        ORDER BY group_id''')
        result = self._c.fetchone()
        return result[0] if result else None

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
        self._c.execute("SELECT measurement FROM experiment")
        result = self._c.fetchone()

        return result

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
        if result:
            print(result[0])
            return result[0]
        return 0

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
        try:
            self._c.execute('''
                SELECT animal_id, value
                FROM animal_measurements
                WHERE timestamp = ?
            ''', (date,))
            return self._c.fetchall()
        except Exception as e:
            print(f"Error getting data for date: {e}")
            return []

    def add_data_entry(self, date, animal_id, values):
        '''Adds a measurement entry for an animal on a specific date.'''
        try:
            # Handle both single values and lists/tuples
            value = values[0] if isinstance(values, (list, tuple)) else values

            # Insert new measurement
            self._c.execute('''
                INSERT INTO animal_measurements (animal_id, timestamp, value)
                VALUES (?, ?, ?)
            ''', (animal_id, date, value))

            self._conn.commit()
        except Exception as e:
            print(f"Error adding data entry: {e}")
            self._conn.rollback()
            
    def change_data_entry(self, date, animal_id, value):
        '''Updates a measurement entry for an animal on a specific date.'''
        try:

            # Update existing measurement
            self._c.execute('''
                UPDATE animal_measurements
                SET value = ?
                WHERE animal_id = ? AND timestamp = ?
            ''', (value, animal_id, date))

            if self._c.rowcount == 0:  # No existing record found
                self.add_data_entry(date, animal_id, value)

            self._conn.commit()
        except Exception as e:
            print(f"Error changing data entry: {e}")
            self._conn.rollback()

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

    def get_animals_in_cage(self, group_name):
        '''Returns animals in a virtual cage based on group and cage number.'''
        try:
            self._c.execute('''
                SELECT animal_id
                FROM animals
                WHERE group_id = (SELECT group_id FROM groups WHERE name = ?)
                AND active = 1
                ORDER BY animal_id
            ''', (group_name,))
            return self._c.fetchall() or [] #Empty list if nothing
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

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
    
    def get_animal_current_cage(self, animal_id):
        '''Returns the current cage (group_id) for an animal'''
        self._c.execute('''
            SELECT group_id 
            FROM animals 
            WHERE animal_id = ? AND active = 1
        ''', (animal_id,))
        result = self._c.fetchone()
        return result[0] if result else None

    def update_animal_cage(self, animal_id, new_group_id):
        '''Updates an animal's cage assignment by updating its group_id'''
        try:
            # Get current group_id
            self._c.execute('''
                SELECT group_id 
                FROM animals 
                WHERE animal_id = ? AND active = 1
            ''', (animal_id,))
            old_group = self._c.fetchone()
            
            if old_group:
                old_group_id = old_group[0]
                
                # Update animal's group
                self._c.execute('''
                    UPDATE animals 
                    SET group_id = ? 
                    WHERE animal_id = ? AND active = 1
                ''', (new_group_id, animal_id))
                
                # Update old group's count
                self._c.execute('''
                    UPDATE groups 
                    SET num_animals = num_animals - 1 
                    WHERE group_id = ?
                ''', (old_group_id,))
                
                # Update new group's count
                self._c.execute('''
                    UPDATE groups 
                    SET num_animals = num_animals + 1 
                    WHERE group_id = ?
                ''', (new_group_id,))
                
                self._conn.commit()
                return True
        except Exception as e:
            print(f"Error updating animal cage: {e}")
            self._conn.rollback()
            return False

    def update_experiment(self, animals_to_update):
        '''Updates the database to reflect current animal states.'''
        updated_animals = animals_to_update
        for old_id, new_id, group_id in updated_animals:
            self._c.execute('''
                UPDATE animals
                SET animal_id = ?, group_id = ?
                WHERE animal_id = ?
            ''', (new_id, group_id, old_id))
        self._conn.commit()

        

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

    def export_to_csv(self, directory):
        '''Exports all relevant tables in the database to a folder named after the experiment in the specified directory.'''
        import pandas as pd

        # Get the experiment name
        self._c.execute("SELECT name FROM experiment")
        experiment_name = self._c.fetchone()
        experiment_name = experiment_name[0] if experiment_name else "default_experiment"

        # Create a folder for the experiment
        experiment_folder = os.path.join(directory, experiment_name)
        os.makedirs(experiment_folder, exist_ok=True)

        # Define the tables to export
        tables = {
            'experiment': 'experiment.csv',
            'animals': 'animals.csv',
            'animal_measurements': 'animal_measurements.csv',
            'groups': 'groups.csv'
        }

        for table, filename in tables.items():
            query = f"SELECT * FROM {table}"
            df = pd.read_sql_query(query, self._conn)
            csv_file_path = os.path.join(experiment_folder, filename)
            df.to_csv(csv_file_path, index=False)

        print(f"All tables exported successfully to {experiment_folder}.")

    def set_animal_active_status(self, animal_id, status):
        '''Sets the active status of an animal.'''
        self._c.execute("UPDATE animals SET active = ? WHERE animal_id = ?", (status, animal_id))
        self._conn.commit()

    def set_number_animals(self, number):
        '''Sets the number of animals in the experiment.'''
        self._c.execute("UPDATE experiment SET num_animals = ?", (number,))
        self._conn.commit()

    def insert_blank_data_for_day(self, animal_ids, date):
        '''Inserts blank measurements for a list of animal IDs for a specific date.'''
        try:
            for animal_id in animal_ids:
                self._c.execute('''INSERT INTO animal_measurements (animal_id, timestamp, value)
                                VALUES (?, ?, ?)''',
                                (animal_id, date, None))  # Insert None for blank value
            self._conn.commit()
        except Exception as e:
            print(f"Error inserting blank data: {e}")
            self._conn.rollback()

    def get_measurement_name(self):
        '''Returns the measurement name from the experiment table.'''
        try:
            self._c.execute("SELECT measurement FROM experiment")
            result = self._c.fetchone()
            return result[0] if result else None  # Return the measurement type or None if not found
        except Exception as e:
            print(f"Error retrieving measurement value: {e}")
            return None
        
    def randomize_cages(self):
        '''Automatically and randomly sorts animals into cages within their groups, respecting cage capacity limits.'''
        import random
        
        try:
            # Get all groups and their cage capacities
            self._c.execute('SELECT group_id, cage_capacity FROM groups ORDER BY group_id')
            groups = self._c.fetchall()
            
            # Get all active animals
            self._c.execute('SELECT animal_id FROM animals WHERE active = 1')
            animals = [animal[0] for animal in self._c.fetchall()]
            random.shuffle(animals)
            
            # Reset all group counts
            self._c.execute('UPDATE groups SET num_animals = 0')
            
            current_group_idx = 0
            for animal_id in animals:
                # Find next group with space
                while True:
                    if current_group_idx >= len(groups):
                        current_group_idx = 0  # Start over from first group if needed
                    
                    group_id, capacity = groups[current_group_idx]
                    
                    # Check if group has space
                    self._c.execute('SELECT num_animals FROM groups WHERE group_id = ?', (group_id,))
                    current_count = self._c.fetchone()[0]
                    
                    if current_count < capacity:
                        break
                        
                    current_group_idx += 1
                
                # Assign animal to group
                self._c.execute('''
                    UPDATE animals
                    SET group_id = ?
                    WHERE animal_id = ?
                ''', (group_id, animal_id))
                
                # Update group count
                self._c.execute('''
                    UPDATE groups
                    SET num_animals = num_animals + 1
                    WHERE group_id = ?
                ''', (group_id,))
            
            self._conn.commit()
            return True
            
        except Exception as e:
            print(f"Error during randomization: {e}")
            self._conn.rollback()
            return False
        
    def autosort(self):
        '''Automatically sorts animals, putting largest into groups, then smallest, until all are sorted'''
        try:
            # Get latest measurement for each active animal
            self._c.execute('''
                SELECT a.animal_id, m.value 
                FROM animals a
                JOIN animal_measurements m ON a.animal_id = m.animal_id
                WHERE a.active = 1
                GROUP BY a.animal_id
                HAVING m.timestamp = MAX(m.timestamp)
            ''')
            measurements = self._c.fetchall()
            
            # Sort measurements by value in descending order
            measurements.sort(key=lambda x: x[1], reverse=True)
            
            # Get all groups and their capacities
            self._c.execute('SELECT group_id, cage_capacity FROM groups')
            groups = self._c.fetchall()
            
            # First, reset all group counts to 0
            for group_id, _ in groups:
                self._c.execute('''
                    UPDATE groups
                    SET num_animals = 0
                    WHERE group_id = ?
                ''', (group_id,))
            
            # Initialize pointers for largest and smallest animals
            large_ptr = 0
            small_ptr = len(measurements) - 1
            use_largest = True  # Flag to alternate between largest and smallest
            
            while large_ptr <= small_ptr:
                for group_id, capacity in groups:
                    # Check if we've distributed all animals
                    if large_ptr > small_ptr:
                        break
                        
                    # Check if this group has space
                    self._c.execute('SELECT num_animals FROM groups WHERE group_id = ?', (group_id,))
                    current_count = self._c.fetchone()[0]
                    
                    if current_count >= capacity:
                        continue
                    
                    # Get the next animal to assign (either largest or smallest)
                    if use_largest:
                        animal_id = measurements[large_ptr][0]
                        large_ptr += 1
                    else:
                        animal_id = measurements[small_ptr][0]
                        small_ptr -= 1
                    
                    # Update the animal's group assignment
                    self._c.execute('''
                        UPDATE animals 
                        SET group_id = ? 
                        WHERE animal_id = ?
                    ''', (group_id, animal_id))
                    
                    # Update group animal count
                    self._c.execute('''
                        UPDATE groups
                        SET num_animals = num_animals + 1
                        WHERE group_id = ?
                    ''', (group_id,))
                
                # Switch between distributing largest and smallest
                use_largest = not use_largest
            
            self._conn.commit()
            return True
            
        except Exception as e:
            print(f"Error during autosort: {e}")
            self._conn.rollback()
            return False