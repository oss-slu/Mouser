'''SQLite Database module for Mouser.'''
import sqlite3
import os
import csv

class ExperimentDatabase:
    '''SQLite Database Object for Experiments.'''
    def __init__(self, file=":memory:"):  #call with file name as argument or no args to use memory
        self.db_file = file
        self._conn = sqlite3.connect(file)
        self._c = self._conn.cursor()
        try:
            self._c.execute('''CREATE TABLE experiment (
                                name TEXT,
                                species TEXT,
                                uses_rfid INTEGER,
                                num_animals INTEGER,
                                num_groups INTEGER,
                                cage_max INTEGER,
                                id TEXT);''')
            self._c.execute('''CREATE TABLE animals (
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                cage_id INTEGER,
                                remarks TEXT,
                                active INTEGER,
                                weight INTEGER);''')
            self._c.execute('''CREATE TABLE groups (
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER,
                                full INTEGER);''')
            self._c.execute('''CREATE TABLE cages (
                                cage_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                num_animals INTEGER,
                                full INTEGER);''')
            self._c.execute('''CREATE TABLE measurement_items (
                                measurement_id INTEGER PRIMARY KEY,
                                item TEXT,
                                auto INTEGER);''')
            self._c.execute('''CREATE TABLE animal_rfid (
                                animal_id INTEGER PRIMARY KEY,
                                rfid TEXT UNIQUE);''')
            self._c.execute('''CREATE TABLE collected_data (
                                date TEXT,
                                animal_id INTEGER);''')
            self._conn.commit()
        except sqlite3.OperationalError:
            pass

    def setup_experiment(self, name, species, uses_rfid, num_animals, num_groups, cage_max, experiment_id):
        '''Initializes Experiment.
        
        Called before inserting any other data.'''
        self._c.execute(''' INSERT INTO experiment (name, species, uses_rfid, num_animals,
                            num_groups, cage_max, id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)''',
                            (name, species, uses_rfid, num_animals, num_groups, cage_max, experiment_id))
        self._conn.commit()

    def setup_groups(self, group_names: list):
        '''Adds the groups to the database.
            arg1 (list): a list of all the group names
        '''
        for group in group_names:
            self._c.execute(''' INSERT INTO groups (name, num_animals, full)
                                VALUES (?, ?, ?)''',
                                (group, 0, 0))
            self._conn.commit()

    def setup_cages(self, num_animals, num_groups, cage_max):
        '''Adds the cages into the experiment.'''
        cages_per_group = (int(num_animals)//int(num_groups)) // int(cage_max)

        cage = 1
        for i in range(1, int(num_groups)+1):
            for cage in range(int(cages_per_group)):
                self._c.execute(''' INSERT INTO cages (group_id, num_animals, full)
                                    VALUES (?, ?, ?)''',
                                    (i, 0, 0))
                self._conn.commit()
                cage += 1
            i += 1

    def setup_measurement_items(self, items):
        '''Adds the measurement items to the database.

        arg1 (list of tuples):
            First item in the tuple is the name of the measurement item.

            Second item in the tuple is a true or false indicating whether
            or not the item will be input automatically or manually
            
            (True or 1 for automatic and False or 0 for manual)
        '''
        for item in items:
            self._c.execute(''' INSERT INTO measurement_items (item, auto)
                                VALUES (?, ?)''',
                                (item[0], item[1]))
            self._conn.commit()

    def setup_collected_data(self, measurement_items):
        '''Configures the collected data table to include a column for
        each measurement item.
        
        arg1 (list of measurement items) as strings
        '''

        for measurement_item in measurement_items:
            query = f''' ALTER TABLE collected_data
                                ADD COLUMN {measurement_item} REAL'''
            self._c.execute(query)
            self._conn.commit()

    def add_data_entry(self, date, animal_id, measurements):
        '''Adds a data entry to the collected_data table with the given
        date, animal_id and a list of measurments.'''
        self._c.execute("SELECT item FROM measurement_items")
        measurement_items = [item[0] for item in self._c.fetchall()]


        insert_param = "(date,animal_id," + ",".join(measurement_items) + ")"

        values_param = f"({str(date)}, {str(animal_id)}, {','.join(map(str, measurements))})"

        query = f"INSERT INTO collected_data {insert_param} VALUES {values_param}" % (insert_param, values_param)

        self._c.execute(query)
        self._conn.commit()

    def change_data_entry(self, date, animal_id, measurements):
        '''Overwrites the data entry of a particular date and animal id
        to the new measurements.'''

        self._c.execute("SELECT item FROM measurement_items")
        measurement_items = [item[0] for item in self._c.fetchall()]

        set_query = "SET "

        for i in range(0,len(measurements)): #pylint: disable= consider-using-enumerate
            if i != 0:
                set_query = set_query +  ", "

            set_query = set_query + measurement_items[i] + " = " + str(measurements[i])

        update_query = f"UPDATE collected_data {set_query} WHERE date=(?) and animal_id=(?)"

        self._c.execute(update_query, (date, animal_id))
        self._conn.commit()

    def get_data_for_date(self, date):
        '''Gets all the measurement data for the given date.'''


        self._c.execute("SELECT * FROM collected_data WHERE date = " + date)
        return self._c.fetchall()

    def get_measurement_items(self):
        '''Returns the measurement items from the experiment.'''
        self._c.execute("SELECT measurement_id, item, auto FROM measurement_items")
        return self._c.fetchall()

    def add_animal_rfid(self, animal_id, rfid):
        '''Associates animal_id with an rfid number in experiment.'''

        self._c.execute("INSERT INTO animal_rfid (animal_id, rfid) VALUES (?, ?)", (animal_id, rfid))

        self._conn.commit()

    def change_animal_rfid(self, animal_id, rfid):
        '''Changes the rfid number of the animal to the passed rfid number'''

        self._c.execute(f"UPDATE animal_rfid SET rfid = {rfid} WHERE animal_id = {animal_id}")

    def remove_animal_rfid(self, animal_id):
        '''Removes the passed animal_id from the rfid table'''

        self._c.execute(f"DELETE from animal_rfid WHERE animal_id = {animal_id}")

    def add_animal(self, animal_id, rfid, remarks=''):
        '''Adds animal to experiment.'''

        print(f"📡 DEBUG: Adding animal {animal_id} with RFID {rfid}")  # ✅ ADD THIS

        self.add_animal_rfid(animal_id, rfid)

        animal_id = self.get_animal_id(rfid)
        cage_id = self._get_next_cage()
        group_id = self._get_next_group()

        self._c.execute('''INSERT INTO animals (animal_id, group_id, cage_id, remarks, active)
                        VALUES (?, ?, ?, ?, True)''',
                        (animal_id, group_id, cage_id, remarks))
        self._conn.commit()

        inserted_id = self.get_animal_id(rfid)
        print(f"📡 DEBUG: Inserted Animal ID: {inserted_id}")  # ✅ ADD THIS

        return inserted_id


    def remove_animal(self, animal_id):
        '''Removes an animal from the experiment.'''
        self._c.execute(f"SELECT group_id, cage_id FROM animals WHERE animal_id = {animal_id}")
        info = self._c.fetchone()

        if info:
            group_id = info[0]
            cage_id = info[1]
            self.remove_animal_from_cage(cage_id)

            self.remove_animal_from_group(group_id)
            self.remove_animal_rfid(animal_id)

            self._c.execute(f"DELETE from animals WHERE animal_id = {animal_id}")
        else:
            raise LookupError(f"No animal_id matches {animal_id}.")

    def remove_animal_from_cage(self, cage_id):
        '''Removes animal from cage.'''

        self._c.execute(f"SELECT num_animals FROM cages WHERE cage_id = {cage_id}")

        num_animals = self._c.fetchone()[0]
        if num_animals:
            num_animals -= 1

            self._c.execute(f"UPDATE cages SET num_animals = {num_animals}, full = 0 WHERE cage_id = {cage_id}")
        else:
            raise LookupError(f"No cage id matches {cage_id}.")

    def remove_animal_from_group(self, group_id):
        '''Removes animal from a group.'''
        self._c.execute(f"SELECT num_animals FROM groups WHERE group_id = {group_id}")

        num_animals = self._c.fetchone()[0]

        if num_animals:
            num_animals -= 1

            self._c.execute(f"UPDATE groups SET num_animals = {num_animals}, full = 0 WHERE group_id = {group_id}")
        else:
            raise LookupError(f"No group id matches {group_id}.")


    def _get_next_cage(self):
        '''Returns the cage_id of the next cage in experiment.'''
        self._c.execute("SELECT cage_id, num_animals FROM cages WHERE full=0")
        info = self._c.fetchone()
        if info:
            cage_id = info[0]
            num_animals = info[1] + 1

            self._c.execute("SELECT cage_max FROM experiment")
            cage_max = self._c.fetchone()[0]

            full = 0
            if num_animals == cage_max:
                full=1
            self._c.execute("UPDATE cages SET num_animals=?, full=? WHERE cage_id=?", (num_animals, full, cage_id))
            self._conn.commit()

            return cage_id
        else:
            raise LookupError("All cages are full")

    def _get_next_group(self):
        '''Returns the group_id of the next group in experiment.'''
        self._c.execute("SELECT group_id, num_animals FROM groups WHERE full=0")
        info = self._c.fetchone()
        group_id = info[0]
        num_group_animals = info[1] + 1

        self._c.execute("SELECT num_animals, num_groups FROM experiment")
        animals = self._c.fetchone()
        group_max = animals[0] // animals[1]

        full = 0
        if num_group_animals == group_max:
            full = 1
        self._c.execute("UPDATE groups SET num_animals=?, full=? WHERE group_id=?",
                        (num_group_animals, full, group_id))
        self._conn.commit()

        return group_id

    def update_group_and_cage(self, animal_id, new_group, new_cage):
        '''Changes passed animal's group and cage to new_group and new_cage.'''
        self._c.execute("UPDATE animals SET group_id=?, cage_id=? WHERE animal_id=?",
                        new_group, new_cage, animal_id)
        self._conn.commit()

    def deactivate_animal(self, animal_id):
        '''Marks animal as non-active.'''
        self._c.execute("UPDATE animals SET active=0 WHERE animal_id=?", (animal_id,))
        self._conn.commit()


    def update_animals(self, animals):
        ''' Updates animal ids, groups, and cages
        arg1 list of tuples: each tuple contains 4 items (old animal id, new animal id, new group, new cage)
            the tuple should contain all the animals even if one animal does not change
        '''
        offset=10000
        for animal in animals:
            self._c.execute("UPDATE animals SET animal_id=? WHERE animal_id=?", (animal[0]+offset, animal[0]))
            self._c.execute("UPDATE animal_rfid SET animal_id=? WHERE animal_id=?", (animal[0]+offset, animal[0]))
            self._conn.commit()

        for animal in animals:
            self._c.execute("UPDATE animals SET animal_id=?, group_id=?, cage_id=? WHERE animal_id=?",
                            (animal[1], animal[2], animal[3], animal[0]+offset))
            self._c.execute("UPDATE animal_rfid SET animal_id=? WHERE animal_id=?", (animal[1], animal[0]+offset))
            self._conn.commit()

    def get_number_animals(self):
        '''Returns number of animals in experiment.'''
        self._c.execute("SELECT num_animals FROM experiment")
        return self._c.fetchone()[0]

    def get_all_animal_ids(self):
        '''Returns a list of all animal ids.'''
        self._c.execute("SELECT animal_id FROM animals")
        animal_ids = []
        raw_ids = self._c.fetchall()
        for i in range(len(raw_ids)): # pylint: disable= consider-using-enumerate
            animal_ids.append(str(raw_ids[i][0]))
        return animal_ids

    def get_number_groups(self):
        '''Returns number of groups in experiment.'''
        self._c.execute("SELECT num_groups FROM experiment")
        return self._c.fetchone()[0]

    def get_cage_max(self):
        '''Returns cage_max of experiment.'''
        self._c.execute("SELECT cage_max FROM experiment")
        return self._c.fetchone()[0]


    def get_all_groups(self):
        '''Returns all groups in experiment.'''
        self._c.execute("SELECT name FROM groups")
        return self._c.fetchall()

    def get_cages(self):
        '''Returns all cages in experiment.'''
        self._c.execute("SELECT cage_id, group_id FROM cages")
        return self._c.fetchall()

    def get_animals_in_cage(self, cage_id):
        '''Returns a list of each animal in passed cage.'''
        self._c.execute("SELECT animal_id FROM animals WHERE cage_id=?", (cage_id, ))
        return self._c.fetchall()

    def get_animals_in_group(self, group_id):
        '''Returns a list of all animals in a particular group.'''
        self._c.execute("SELECT animal_id FROM animals WHERE group_id=?", (group_id, ))
        return self._c.fetchall()

    def get_animals_by_cage(self):
        '''Returns a dict where the key is cage_id and
        the value is a list of animals in that cage.'''
        self._c.execute("SELECT cage_id FROM cages", ())
        cages = self._c.fetchall()

        animals_by_cage = {}

        for cage in cages:
            self._c.execute("SELECT animal_id FROM animals WHERE cage_id=?", (cage[0],))
            animals = self._c.fetchall()
            ans =[]
            for animal in animals:
                ans.append(str(animal[0]))
            animals_by_cage[str(cage[0])] = ans

        return animals_by_cage

    def get_animals_by_group(self):
        '''Returns a dict where the key is group_id and
        the value is a list of animals in that group.'''
        self._c.execute("SELECT group_id, name FROM groups", ())
        groups = self._c.fetchall()

        animals_by_group = {}

        for group in groups:
            self._c.execute("SELECT animal_id FROM animals WHERE group_id=?", (group[0],))
            animals = self._c.fetchall()
            ans =[]
            for animal in animals:
                ans.append(str(animal[0]))
            animals_by_group[str(group[1])] = ans

        return animals_by_group

    def get_cages_by_group(self):
        '''Returns a dict where the key is group_id and
        the value is a list of cages in that group.'''
        self._c.execute("SELECT group_id, name FROM groups", ())
        groups = self._c.fetchall()

        cages_by_group = {}

        for group in groups:
            self._c.execute("SELECT cage_id FROM cages WHERE group_id=?", (group[0],))
            cages = self._c.fetchall()

            ans = []
            for cage in cages:
                ans.append(str(cage[0]))
            cages_by_group[str(group[1])] = ans

        return cages_by_group


    def get_name(self):
        '''Returns a string of the experiment name.'''
        self._c.execute("SELECT name FROM experiment")
        return self._c.fetchall()
    
    def get_animals(self):
        '''Returns a list of tuples representing each animal in experiment.'''
        self._c.execute("SELECT animal_id, group_id, cage_id, weight, active FROM animals")
        return self._c.fetchall()

    def get_animal_id(self, rfid):
        '''Returns the id of the animal with the passed RFID.'''
        self._c.execute("SELECT animal_id FROM animal_rfid WHERE rfid=?", (rfid,))
        return self._c.fetchone()[0]

    def get_animal_rfid(self, animal_id):
        '''Returns the rfid number of the passed animal'''
        self._c.execute("SELECT rfid FROM animal_rfid WHERE animal_id=?", (int(animal_id),))
        return self._c.fetchone()[0]

    def get_animals_rfid(self):
        '''Returns a list of all animal rfids.'''
        self._c.execute("SELECT rfid FROM animal_rfid")
        return self._c.fetchall()

    def experiment_uses_rfid(self):
        self._c.execute("SELECT uses_rfid FROM experiment")
        do_we_use_rfid = self._c.fetchone()[0]  # Fetch the first result and get the integer value
        return do_we_use_rfid
        

    def get_all_experiment_info(self):
        '''Prints all experiment info to terminal.'''
        self._c.execute("SELECT name, species, uses_rfid, num_animals, num_groups, cage_max FROM experiment")
        print('Experiment: name, species, uses_rfid, num_animals, num_groups, cage_max')
        print(self._c.fetchall())
        self._c.execute("SELECT name, num_animals, full FROM groups")
        print('Groups: name, num_animals, full')
        print(self._c.fetchall())
        self._c.execute("SELECT cage_id, group_id, num_animals, full FROM cages")
        print('cages: cage_id, group_id, num_animals, full')
        print(self._c.fetchall())
        self._c.execute("SELECT item, auto FROM measurement_items")
        print('Measurement Items: item, auto')
        print(self._c.fetchall())

    def close(self):
        '''Closes database file.'''
        self._conn.close()

    def export_all_tables_to_csv(self, export_dir):
        '''Exports all tables in the database to separate CSV files.'''
        # Get the base name of the database file (without extension)
        db_name = os.path.splitext(os.path.basename(self.db_file))[0]

        # Create a directory with the database name to save CSV files
        export_dir = os.path.join(export_dir, db_name)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        # Get all table names from the database
        self._c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self._c.fetchall()

        # Export each table to a CSV file
        for table_name in tables:
            table_name = table_name[0]  # Extract table name from tuple
            csv_file_path = os.path.join(export_dir, f"{table_name}.csv")

            # Fetch all data from the table
            self._c.execute(f"SELECT * FROM {table_name}")
            rows = self._c.fetchall()

            # Get column names for the table
            self._c.execute(f"PRAGMA table_info({table_name})")
            column_info = self._c.fetchall()
            column_names = [col[1] for col in column_info]  # Column names are in the second position

            # Write data to CSV
            with open(csv_file_path, mode='w', newline='') as file:
                csv_writer = csv.writer(file)
                # Write the header
                csv_writer.writerow(column_names)
                # Write the rows
                csv_writer.writerows(rows)

            print(f"Table '{table_name}' exported to {csv_file_path}")

        print("All tables have been exported successfully.")

    def export_all_tables_to_single_csv(self, output_file):
        import pandas as pd

        db_name = os.path.splitext(os.path.basename(self.db_file))[0]

        # Create a directory with the database name to save CSV files
        export_dir = os.path.join(output_file, db_name)
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        # Get all table names from the database
        self._c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self._c.fetchall()

        animal_rfid_df = pd.DataFrame()
        collected_data_df = pd.DataFrame()
        animals_df = pd.DataFrame()
        cages_df = pd.DataFrame()
        groups_df = pd.DataFrame()

        for table_name in tables:
            table_name = table_name[0]  # Extract table name from tuple
            if table_name == 'animal_rfid':
                animal_rfid_df = pd.read_sql_query(f"SELECT * FROM {table_name}", self._conn)
            elif table_name == 'collected_data':
                collected_data_df = pd.read_sql_query(f"SELECT * FROM {table_name}", self._conn)
            elif table_name == 'animals':
                animals_df = pd.read_sql_query(f"SELECT * FROM {table_name}", self._conn)
            elif table_name == 'cages':
                cages_df = pd.read_sql_query(f"SELECT * FROM {table_name}", self._conn)
            elif table_name == 'groups':
                groups_df = pd.read_sql_query(f"SELECT * FROM {table_name}", self._conn)

        # Merge DataFrames
        merged_df = animal_rfid_df.merge(collected_data_df, on='animal_id', how='outer')
        merged_df = merged_df.merge(animals_df, on='animal_id', how='outer')

        merged_cages_df = cages_df.merge(groups_df, on='group_id', how='inner')

        # Write the merged DataFrames to a single CSV file
        csv_file_path = os.path.join(export_dir, f"experiment_data.csv")
        merged_df.to_csv(csv_file_path, index=False)


        # Write the merged_cages_df DataFrame to a CSV file
        csv_file_path = os.path.join(export_dir, f"cage_setup.csv")
        merged_cages_df.to_csv(csv_file_path, index=False)

    
    def set_number_animals(self, number):
        '''Sets the maximum number of animals for the experiment'''
        self._c.execute("UPDATE experiment SET num_animals = ?", (number,))
        self._conn.commit()



