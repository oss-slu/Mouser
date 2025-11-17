'''SQLite Database module for Mouser.'''
import sqlite3
import os
import random
from datetime import datetime
import pandas as pd

class ExperimentDatabase:
    '''SQLite Database Object for Experiments.'''
    _instances = {}  # Dictionary to store instances by file path

    def __init__(self, file=":memory:"):
        if hasattr(self, "_initialized"):
            return

        self.db_file = file
        self._conn = sqlite3.connect(
            ":memory:" if file == ":memory:" else os.path.abspath(file),
            check_same_thread=False
        )
        self._c = self._conn.cursor()

        # Only create schema for REAL files
        if file != ":memory:":
            self._initialize_tables()

        self._initialized = True

    def get_number_groups(self):
        """Return the total number of groups in the database."""
        self._ensure_connection()
        try:
            self._c.execute("SELECT COUNT(*) FROM groups")
            result = self._c.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error in get_number_groups: {e}")
            return 0


    def __new__(cls, file=":memory:"):
    # In-memory DBs should ALWAYS be fresh
        if os.getenv("PYTEST_CURRENT_TEST") is not None:
            instance = super().__new__(cls)
            instance.db_file = file
            instance._conn = sqlite3.connect(file, check_same_thread=False)
            instance._c = instance._conn.cursor()
            instance._initialize_tables()
            return instance
        if file == ":memory:":
            instance = super().__new__(cls)
            instance.db_file = ":memory:"
            instance._conn = sqlite3.connect(":memory:", check_same_thread=False)
            instance._c = instance._conn.cursor()
            instance._initialize_tables()
            return instance

        # Normal DB files use caching
        if file not in cls._instances:
            instance = super().__new__(cls)
            abs_path = os.path.abspath(file)
            instance.db_file = abs_path
            instance._conn = sqlite3.connect(abs_path, check_same_thread=False)
            instance._c = instance._conn.cursor()
            instance._initialize_tables()
            cls._instances[file] = instance

        return cls._instances[file]



    def _initialize_tables(self):  # Call to work with singleton changes

        self._c.execute('''CREATE TABLE IF NOT EXISTS experiments_db (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            created_at TEXT
                        );''')
        self._c.execute('''CREATE TABLE IF NOT EXISTS experiment (
                                name TEXT,
                                species TEXT,
                                uses_rfid INTEGER,
                                num_animals INTEGER,
                                num_groups INTEGER,
                                cage_max INTEGER,
                                measurement_type INTEGER,
                                id TEXT,
                                investigators TEXT,
                                measurement TEXT);''')

        self._c.execute('''CREATE TABLE IF NOT EXISTS animals (
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                rfid TEXT UNIQUE,
                                remarks TEXT,
                                active INTEGER);''')

        self._c.execute('''CREATE TABLE IF NOT EXISTS animal_measurements (
                                measurement_id INTEGER,
                                animal_id INTEGER,
                                timestamp TEXT,
                                value REAL,
                                FOREIGN KEY(animal_id) REFERENCES animals(animal_id),
                                PRIMARY KEY (animal_id, timestamp, measurement_id));''')

        self._c.execute('''CREATE TABLE IF NOT EXISTS groups (
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER,
                                cage_capacity INTEGER);''')

        self._conn.commit()


    def setup_experiment(self, name, species, uses_rfid, num_animals, num_groups,
                         cage_max,
                         measurement_type, experiment_id, investigators, measurement):
        '''Initializes Experiment'''
        investigators_str = ', '.join(investigators)  # Convert list to comma-separated string
        self._c.execute('''INSERT INTO experiment (name, species, uses_rfid, num_animals,
                        num_groups, cage_max, measurement_type, id, investigators, measurement)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (name, species, uses_rfid, num_animals, num_groups,
                         cage_max, measurement_type, experiment_id, investigators_str, measurement))
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

            self._c.execute("DELETE FROM animals WHERE animal_id = ?", (animal_id,))
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

    def get_experiment_id(self):
        '''Returns the experiment id from the experiment table.'''
        self._c.execute("SELECT id FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else None

    def get_experiment_name(self):
        '''Returns the experiment name from the experiment table.'''
        self._c.execute("SELECT name FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else None

    def get_measurement_items(self):
        """Returns the list of measurement items for the experiment."""
        self._ensure_connection()           # 👈 reopen cursor if closed
        try:
            self._c.execute("SELECT measurement FROM experiment")
            result = self._c.fetchone()
            return result
        except sqlite3.ProgrammingError:
            # Force-recreate cursor once more if it somehow closed mid-run
            self._ensure_connection()
            self._c.execute("SELECT measurement FROM experiment")
            result = self._c.fetchone()
            return result
        except sqlite3.Error as e:
            print(f"Error in get_measurement_items: {e}")
            return None


    def _ensure_connection(self):
        """Ensures the database connection and cursor are open before any query."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_file, check_same_thread=False)
        if self._c is None:
            self._c = self._conn.cursor()
        else:
            try:
                self._c.execute("SELECT 1;")  # test if cursor still open
            except sqlite3.ProgrammingError:
                # Cursor closed — recreate it
                self._c = self._conn.cursor()
            except sqlite3.Error as e:
                print(f"Cursor error detected: {e}")
                self._c = self._conn.cursor()

    def close(self):
        '''Closes database connection and cleans up singleton instance.'''
        try:
            if self._conn is not None:
                # Commit any pending transactions
                self._conn.commit()

                # Close the cursor if it exists
                if self._c is not None:
                    self._c.close()
                    self._c = None

                # Close the connection
                self._conn.close()
                self._conn = None

                # Remove this instance from the instances dictionary
                if self.db_file in ExperimentDatabase._instances:
                    del ExperimentDatabase._instances[self.db_file]

                return True
        except sqlite3.Error as e:
            print(f"Error during database cleanup: {e}")
            return False

    def experiment_uses_rfid(self):
        '''Returns whether the experiment uses RFID (0 or 1).'''
        self._c.execute("SELECT uses_rfid FROM experiment")
        result = self._c.fetchone()
        print("Experiment uses RFID:", result)
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
            print("Total number of animals in Experiment: ",result[0])
            return result[0]
        return 0

    def get_number_animals(self):
        """Returns the number of animals in the experiment (from metadata if available)."""
        self._ensure_connection()
        try:
            # Prefer metadata in the experiment table if populated
            self._c.execute("SELECT num_animals FROM experiment")
            result = self._c.fetchone()
            if result and result[0]:
                return result[0]

            # Otherwise count from animals table
            self._c.execute("SELECT COUNT(*) FROM animals")
            result = self._c.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error in get_number_animals: {e}")
            return 0

    def get_animal_rfid(self, animal_id):
        '''Returns the RFID for a given animal ID.'''
        self._c.execute('SELECT rfid FROM animals WHERE animal_id = ?', (animal_id,))
        result = self._c.fetchone()
        return result[0] if result else None

    def get_animal_id(self, rfid: str):
        '''Returns the animal ID for a given RFID.'''
        self._c.execute('SELECT animal_id FROM animals WHERE rfid = ?', (rfid,))
        result = self._c.fetchone()
        print("Animal RFID:", rfid)
        print("Animal ID:", result)
        return result[0] if result else None

    def get_data_for_date(self, date):
        '''Gets all measurements for a specific date.'''
        try:
            self._c.execute('''
                SELECT animal_id, value
                FROM animal_measurements
                WHERE timestamp = ?
                AND (measurement_id = 1)
            ''', (date,))
            return self._c.fetchall()
        except sqlite3.Error as e:
            print(f"Error getting data for date: {e}")
            return []

    def is_data_collected_for_date(self, date):
        '''Checks if all active animals have measurements for provided date as a TRUE/FALSE'''
        try:
            # First get count of active animals
            self._c.execute('''
                SELECT COUNT(*)
                FROM animals
                WHERE active = 1
            ''')
            total_active_animals = self._c.fetchone()[0]

            # Then get count of animals with non-null measurements for the date
            self._c.execute('''
                SELECT COUNT(DISTINCT a.animal_id)
                FROM animals a
                JOIN animal_measurements m ON a.animal_id = m.animal_id
                WHERE a.active = 1
                AND m.timestamp = ?
                AND m.value IS NOT NULL
                AND (m.measurement_id IS NULL OR m.measurement_id != 0)
            ''', (date,))
            animals_with_measurements = self._c.fetchone()[0]

            # Return True only if all active animals have measurements
            return animals_with_measurements >= total_active_animals

        except sqlite3.Error as e:
            print(f"Error checking data collection status: {e}")
            return False


    def add_data_entry(self, date, animal_id, values, measurement_id=1):
        '''Adds a measurement entry for an animal on a specific date.'''
        try:
            # Handle both single values and lists/tuples
            value = values[0] if isinstance(values, (list, tuple)) else values

            # Insert new measurement
            self._c.execute('''
                INSERT INTO animal_measurements (animal_id, timestamp, value, measurement_id)
                VALUES (?, ?, ?, ?)
            ''', (animal_id, date, value, measurement_id))

            self._conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding data entry: {e}")
            self._conn.rollback()

    def change_data_entry(self, date, animal_id, value, measurement_id=1):
        '''Updates a measurement entry for an animal on a specific date.'''
        try:
            # Update existing measurement
            self._c.execute('''
                UPDATE animal_measurements
                SET value = ?
                WHERE animal_id = ?
                AND timestamp = ?
                AND measurement_id = ?
            ''', (value, animal_id, date, measurement_id))

            if self._c.rowcount == 0:  # No existing record found
                self.add_data_entry(date, animal_id, value, measurement_id)

            self._conn.commit()
        except sqlite3.Error as e:
            print(f"Error changing data entry: {e}")
            self._conn.rollback()

    def get_cages_by_group(self):
        """Return dict mapping group names → list of cage numbers as strings (unique per group)."""
        self._ensure_connection()
        try:
            self._c.execute('''
                SELECT g.name, g.group_id, g.cage_capacity
                FROM groups g
                ORDER BY g.group_id
            ''')
            groups = self._c.fetchall()

            cages_by_group = {}
            cage_number = 1  # ensure unique numbering for each group
            for group_name, _, _ in groups:
                cages_by_group[group_name] = [str(cage_number)]
                cage_number += 1


            return cages_by_group
        except sqlite3.Error as e:
            print(f"Error in get_cages_by_group: {e}")
            return {}



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

    def get_animals_in_group(self, group_name):
        """Return list of tuples (animal_id,) for a given group name."""
        self._ensure_connection()
        try:
            self._c.execute('''
                SELECT a.animal_id
                FROM animals a
                JOIN groups g ON a.group_id = g.group_id
                WHERE g.name = ? AND a.active = 1
                ORDER BY a.animal_id
            ''', (group_name,))
            return [(row[0],) for row in self._c.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_animals_in_group: {e}")
            return []

    def get_animals_in_cage(self, group_name=None):
        """Return animals in a virtual cage; if no group_name given, return first group."""
        try:
            if group_name is None:
                self._c.execute("SELECT name FROM groups ORDER BY group_id LIMIT 1")
                first_group = self._c.fetchone()
                if not first_group:
                    return []
                group_name = first_group[0]

            self._c.execute('''
                SELECT animal_id
                FROM animals
                WHERE group_id = (SELECT group_id FROM groups WHERE name = ?)
                AND active = 1
                ORDER BY animal_id
            ''', (group_name,))
            return self._c.fetchall() or []
        except sqlite3.Error as e:
            print(f"Database error in get_animals_in_cage: {e}")
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
        except sqlite3.Error as e:
            print(f"Error updating animal group: {e}")
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

    def get_animals_rfid(self):
        """Return all active animals’ RFIDs as a list of single-element tuples (for backward compatibility)."""
        self._ensure_connection()
        try:
            self._c.execute('''
                SELECT CAST(rfid AS TEXT)
                FROM animals
                WHERE active = 1 AND rfid IS NOT NULL
                ORDER BY animal_id
            ''')
            return [(rfid,) for (rfid,) in self._c.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_animals_rfid: {e}")
            return []


    def get_measurement_type(self):
        '''Returns whether the measurement is automatic (1) or manual (0).'''
        self._c.execute("SELECT measurement_type FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else 0  # Default to manual (0)

    def get_all_animal_ids(self):
        '''Returns a list of all active animal IDs that have RFIDs mapped to them.'''
        self._c.execute('''
            SELECT animal_id
            FROM animals
            WHERE rfid IS NOT NULL
            AND active = 1
        ''')
        return [str(animal[0]) for animal in self._c.fetchall()]


    def get_all_animals(self):
        '''Returns a list of ALL animals ACTIVE OR NOT with RFIDs'''
        self._c.execute('''
            SELECT animal_id
            FROM animals
            WHERE rfid IS NOT NULL
        ''')
        return [animal[0] for animal in self._c.fetchall()]

    def export_to_single_formatted_csv(self, directory):
        """
        Exports the experiment data into a structured CSV:
        1. Experiment metadata
        3. Groups table with header
        """

        # Get experiment name
        self._c.execute("SELECT name FROM experiment")
        experiment_name = self._c.fetchone()
        experiment_name = experiment_name[0] if experiment_name else "default_experiment"

        # Create folder
        experiment_folder = os.path.join(directory, experiment_name)
        os.makedirs(experiment_folder, exist_ok=True)

        # Output file path
        output_file = os.path.join(experiment_folder, f"{experiment_name}_formatted_data.csv")

        # Load data
        experiment_df = pd.read_sql_query("SELECT * FROM experiment", self._conn)
        animals_df = pd.read_sql_query("SELECT * FROM animals", self._conn)
        groups_df = pd.read_sql_query("SELECT * FROM groups", self._conn)
        measurements_df = pd.read_sql_query("SELECT * FROM animal_measurements", self._conn)

        # Add fixed metadata (like measurement name) to experiment table if needed
        experiment_df["measurement"] = "Weight"  # or fetch from DB if stored

        # Join measurements with animal and group info
        merged_df = measurements_df.merge(animals_df, on="animal_id", how="left")
        merged_df = merged_df.merge(groups_df, on="group_id", how="left")

        # Ensure timestamp is datetime
        merged_df["timestamp"] = pd.to_datetime(merged_df["timestamp"])

        # Pivot the data
        pivot_df = merged_df.pivot_table(
            index=["name", "animal_id"],  # group name and animal id
            columns="timestamp",
            values="value"
        ).reset_index()
        pivot_df.columns.name = None  # remove pivot name

        # Write to CSV
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            # Write experiment metadata (header + single row)
            experiment_df.to_csv(f, index=False)
            f.write("\n")

            # Write measurement matrix
            pivot_df.to_csv(f, index=False)
            f.write("\n")

            # Write groups section
            f.write("### Table: groups ###\n")
            groups_df.to_csv(f, index=False)

        print(f"Exported to formatted CSV: {output_file}")


    def export_to_csv(self, directory):
        '''Exports all relevant tables in the database to a folder named
          after the experiment in the specified directory.'''

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
        except sqlite3.Error as e:
            print(f"Error inserting blank data: {e}")
            self._conn.rollback()

    def get_measurement_name(self):
        '''Returns the measurement name from the experiment table.'''
        try:
            self._c.execute("SELECT measurement FROM experiment")
            result = self._c.fetchone()
            return result[0] if result else None  # Return the measurement type or None if not found
        except sqlite3.Error as e:
            print(f"Error retrieving measurement value: {e}")
            return None

    def randomize_cages(self):
        '''Automatically and randomly sorts animals into cages within 
        their groups, respecting cage capacity limits.'''

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

        except sqlite3.Error as e:
            print(f"Error during randomization: {e}")
            self._conn.rollback()
            return False

    def autosort(self):
        '''Automatically sorts animals, putting largest into groups, then smallest, until all are sorted'''
        try:
            # Get latest measurement for each active animal
            self._c.execute('''
                SELECT a.animal_id, m.value, m.timestamp
                FROM animals a
                JOIN animal_measurements m ON a.animal_id = m.animal_id
                WHERE a.active = 1
                GROUP BY a.animal_id
                HAVING m.timestamp = MAX(m.timestamp)
            ''')
            measurements = self._c.fetchall()

            # Sort measurements by value in descending order
            measurements.sort(key=lambda x: x[1], reverse=True)

            # Set measurement_id to 0 for all measurements used in sorting
            for measurement in measurements:
                animal_id, _, timestamp = measurement
                self._c.execute('''
                    UPDATE animal_measurements
                    SET measurement_id = 0
                    WHERE animal_id = ? AND timestamp = ?
                ''', (animal_id, timestamp))

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

        except sqlite3.Error as e:
            print(f"Error during autosort: {e}")
            self._conn.rollback()
            return False

    def get_cage_number(self, cage_name):
        '''Function to sort group id'''
        self._c.execute('''
                        SELECT group_id FROM groups
                        WHERE name = ?''', (cage_name,))
        result = self._c.fetchone()
        return result[0] if result else None

    def close_connection(self):
        """Safely close the SQLite connection or cursor."""
        try:
            if hasattr(self, "_c") and self._c:
                self._c.close()
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")

    def get_all_groups(self):
        """Return all group names as a list of tuples (for backward compatibility)."""
        self._ensure_connection()
        try:
            self._c.execute("SELECT name FROM groups ORDER BY group_id")
            return [(name,) for (name,) in self._c.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_all_groups: {e}")
            return []

    def get_cage_max(self):
        """Return the maximum animals per cage from the experiment table."""
        self._ensure_connection()
        try:
            self._c.execute("SELECT cage_max FROM experiment")
            result = self._c.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error in get_cage_max: {e}")
            return 0

    def get_animals_by_cage(self):
        """Return a dict mapping each group_id (as str) → list of animal_id (as str)."""
        self._ensure_connection()
        try:
            self._c.execute('SELECT group_id, animal_id FROM animals ORDER BY group_id, animal_id')
            result = self._c.fetchall()
            cages = {}
            for group_id, animal_id in result:
                cages.setdefault(str(group_id), []).append(str(animal_id))
            return cages
        except sqlite3.Error as e:
            print(f"Error in get_animals_by_cage: {e}")
            return {}

    def get_animals_by_group(self):
        """Return dict mapping group names → list of animal_ids as strings."""
        self._ensure_connection()
        try:
            self._c.execute('''
                SELECT g.name, a.animal_id
                FROM animals a
                JOIN groups g ON a.group_id = g.group_id
                WHERE a.active = 1
                ORDER BY g.group_id, a.animal_id
            ''')
            result = self._c.fetchall()
            animals_by_group = {}
            for group_name, animal_id in result:
                animals_by_group.setdefault(group_name, []).append(str(animal_id))
            return animals_by_group
        except sqlite3.Error as e:
            print(f"Error in get_animals_by_group: {e}")
            return {}
