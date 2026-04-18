'''SQLite Database module for Mouser.'''
import sqlite3
import os
from datetime import datetime

class ExperimentDatabase:
    '''SQLite Database Object for Experiments.'''
    _instances = {}  # Dictionary to store instances by file path


    def get_number_groups(self):
        '''Returns the number of groups in the experiment.'''
        self._c.execute("SELECT COUNT(*) FROM groups")
        result = self._c.fetchone()
        return result[0] if result else 0


    def __new__(cls, file=":memory:"):
        '''Builds Database connections if singleton does not exist for this file'''
        if file not in cls._instances:
            instance = super(ExperimentDatabase, cls).__new__(cls)
            # Absolute path prevents file locking issues caused by relative path resolution differences
            # check_same_thread=False allows access from multiple Tkinter callbacks
            # timeout=5.0 allows retry if DB is briefly locked by another thread
            if file == ":memory:":
                abs_path = file
            else:
                abs_path = os.path.abspath(file)
            abs_path = os.path.abspath(file)
            instance.db_file = abs_path
            instance._conn = sqlite3.connect(abs_path, timeout=5.0, check_same_thread=False)
            instance._c = instance._conn.cursor()
            instance._initialize_tables()
            cls._instances[file] = instance
        return cls._instances[file]


    def _initialize_tables(self):  # Call to work with singleton changes
        """Create base tables if missing and upgrade legacy schemas."""
        try:
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
                                measurement TEXT,
                                organization TEXT,
                                cell_line TEXT,
                                strain TEXT,
                                calc_method INTEGER,
                                tumors_per_animal INTEGER,
                                tumor_labels TEXT,
                                measurement_mode TEXT
                            );''')

            self._c.execute('''CREATE TABLE IF NOT EXISTS animals (
                                animal_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                cage_id INTEGER,
                                rfid TEXT UNIQUE,
                                remarks TEXT,
                                active INTEGER
                            );''')

            self._c.execute('''CREATE TABLE IF NOT EXISTS animal_measurements (
                                measurement_id INTEGER,
                                animal_id INTEGER,
                                timestamp TEXT,
                                value REAL,
                                FOREIGN KEY(animal_id) REFERENCES animals(animal_id),
                                PRIMARY KEY (animal_id, timestamp, measurement_id)
                            );''')

            self._c.execute('''CREATE TABLE IF NOT EXISTS groups (
                                group_id INTEGER PRIMARY KEY,
                                name TEXT,
                                num_animals INTEGER,
                                cage_capacity INTEGER
                            );''')

            self._c.execute('''CREATE TABLE IF NOT EXISTS cages (
                                cage_id INTEGER PRIMARY KEY,
                                group_id INTEGER,
                                cage_number INTEGER,
                                label TEXT,
                                FOREIGN KEY(group_id) REFERENCES groups(group_id)
                            );''')

            self._c.execute('''CREATE TABLE IF NOT EXISTS tumors (
                                tumor_id INTEGER PRIMARY KEY,
                                animal_id INTEGER,
                                group_id INTEGER,
                                cage_id INTEGER,
                                tumor_index INTEGER,
                                location_label TEXT,
                                measurement_order INTEGER,
                                date_removed TEXT,
                                censored INTEGER,
                                FOREIGN KEY(animal_id) REFERENCES animals(animal_id)
                            );''')

            self._c.execute('''CREATE TABLE IF NOT EXISTS tumor_measurements (
                                measurement_id INTEGER PRIMARY KEY,
                                tumor_id INTEGER,
                                date_measured TEXT,
                                length REAL,
                                width REAL,
                                status TEXT,
                                FOREIGN KEY(tumor_id) REFERENCES tumors(tumor_id)
                            );''')

            self._conn.commit()
            self._ensure_schema()
        except sqlite3.OperationalError:
            pass

    def _table_has_column(self, table_name, column_name):
        self._c.execute(f"PRAGMA table_info({table_name})")
        return any(row[1] == column_name for row in self._c.fetchall())

    def _add_column_if_missing(self, table_name, column_name, column_type, default_sql=None):
        if self._table_has_column(table_name, column_name):
            return
        self._c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        if default_sql is not None:
            self._c.execute(f"UPDATE {table_name} SET {column_name} = {default_sql}")

    def _ensure_schema(self):
        """Upgrade legacy schema in-place to support tumor-level data."""
        # Experiment table upgrades
        self._add_column_if_missing("experiment", "organization", "TEXT")
        self._add_column_if_missing("experiment", "cell_line", "TEXT")
        self._add_column_if_missing("experiment", "strain", "TEXT")
        self._add_column_if_missing("experiment", "calc_method", "INTEGER", "0")
        self._add_column_if_missing("experiment", "tumors_per_animal", "INTEGER", "1")
        self._add_column_if_missing("experiment", "tumor_labels", "TEXT", "'Tumor 1'")
        self._add_column_if_missing("experiment", "measurement_mode", "TEXT", "'weight'")

        # Animals table upgrades
        self._add_column_if_missing("animals", "cage_id", "INTEGER")

        self._conn.commit()
        self._ensure_cages_for_groups()

    def _ensure_cages_for_groups(self):
        """Create cages and assign animals to cages if missing."""
        # If cages table already has rows, assume migration done.
        self._c.execute("SELECT COUNT(*) FROM cages")
        existing = self._c.fetchone()[0]
        if existing and existing > 0:
            return

        # Build cages per group based on capacity and animal count.
        self._c.execute("SELECT group_id, cage_capacity FROM groups ORDER BY group_id")
        groups = self._c.fetchall()
        if not groups:
            return

        for group_id, capacity in groups:
            if not capacity or int(capacity) <= 0:
                capacity = 1
            self._c.execute(
                "SELECT animal_id FROM animals WHERE group_id = ? ORDER BY animal_id",
                (group_id,),
            )
            animal_ids = [row[0] for row in self._c.fetchall()]
            num_cages = max(1, (len(animal_ids) + capacity - 1) // capacity)
            cage_ids = []
            for cage_number in range(1, num_cages + 1):
                self._c.execute(
                    "INSERT INTO cages (group_id, cage_number, label) VALUES (?, ?, ?)",
                    (group_id, cage_number, f"Cage {cage_number}"),
                )
                cage_ids.append(self._c.lastrowid)

            # Assign animals to cages sequentially
            for idx, animal_id in enumerate(animal_ids):
                cage_idx = idx // capacity
                if cage_idx >= len(cage_ids):
                    cage_idx = len(cage_ids) - 1
                self._c.execute(
                    "UPDATE animals SET cage_id = ? WHERE animal_id = ?",
                    (cage_ids[cage_idx], animal_id),
                )

        self._conn.commit()

    def setup_experiment(
        self,
        name,
        species,
        uses_rfid,
        num_animals,
        num_groups,
        cage_max,
        measurement_type,
        experiment_id,
        investigators,
        measurement,
        organization=None,
        cell_line=None,
        strain=None,
        calc_method=0,
        tumors_per_animal=1,
        tumor_labels=None,
        measurement_mode="tumor",
    ):
        """Initializes Experiment."""
        investigators_str = ", ".join(investigators)  # Convert list to comma-separated string
        # Normalize inputs
        try:
            calc_method = int(calc_method)
        except Exception:
            calc_method = 0
        calc_method = max(0, min(10, calc_method))
        try:
            tumors_per_animal = int(tumors_per_animal)
        except Exception:
            tumors_per_animal = 1
        tumors_per_animal = max(1, min(4, tumors_per_animal))

        if tumor_labels is None:
            tumor_labels = ["Tumor 1"]
        labels = [str(t).strip() for t in tumor_labels if str(t).strip()]
        while len(labels) < tumors_per_animal:
            labels.append(f"Tumor {len(labels) + 1}")
        if len(labels) > tumors_per_animal:
            labels = labels[:tumors_per_animal]
        tumor_labels_str = ", ".join(labels)

        self._c.execute(
            '''INSERT INTO experiment (
                name, species, uses_rfid, num_animals, num_groups, cage_max,
                measurement_type, id, investigators, measurement,
                organization, cell_line, strain, calc_method, tumors_per_animal,
                tumor_labels, measurement_mode
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                name,
                species,
                uses_rfid,
                num_animals,
                num_groups,
                cage_max,
                measurement_type,
                experiment_id,
                investigators_str,
                measurement,
                organization,
                cell_line,
                strain,
                calc_method,
                tumors_per_animal,
                tumor_labels_str,
                measurement_mode,
            ),
        )
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
            cage_id = self._assign_animal_to_cage(group_id)
            self._c.execute('''INSERT INTO animals (animal_id, group_id, cage_id, rfid, remarks, active)
                            VALUES (?, ?, ?, ?, ?, 1)''',
                            (animal_id, group_id, cage_id, rfid, remarks))

            # Update group animal count
            self._c.execute('''UPDATE groups
                            SET num_animals = num_animals + 1
                            WHERE group_id = ?''', (group_id,))

            self._conn.commit()
            # Auto-create tumors for tumor-mode experiments
            if self.get_measurement_mode() == "tumor":
                self.ensure_tumors_for_animal(animal_id)
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

    def get_investigators(self):
        """Return investigators as a list of names."""
        self._c.execute("SELECT investigators FROM experiment")
        result = self._c.fetchone()
        if not result or result[0] is None:
            return []
        return [item.strip() for item in str(result[0]).split(",") if item.strip()]

    def update_investigators(self, investigators):
        """Persist investigators list to experiment table."""
        investigators_str = ", ".join([name.strip() for name in investigators if name and name.strip()])
        self._c.execute("UPDATE experiment SET investigators = ?", (investigators_str,))
        self._conn.commit()

    def get_measurement_items(self):
        '''Returns the list of measurement items for the experiment.'''
        self._c.execute("SELECT measurement FROM experiment")
        result = self._c.fetchone()

        return result

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
        '''Returns the number of active animals in the database.'''
        self._c.execute("SELECT COUNT(*) FROM animals WHERE active = 1")
        result = self._c.fetchone()
        return result[0] if result else 0

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
        '''Returns a dictionary of group IDs mapped to their cage information.'''
        self._c.execute(
            '''
            SELECT g.group_id, c.cage_id
            FROM groups g
            JOIN cages c ON c.group_id = g.group_id
            ORDER BY g.group_id, c.cage_number
            '''
        )
        cages_by_group = {}
        for group_id, cage_id in self._c.fetchall():
            cages_by_group.setdefault(group_id, []).append(cage_id)
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
        '''Returns animals in a group (legacy behavior).'''
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

    def get_cages(self):
        """Return list of cages with group and label."""
        self._c.execute(
            '''
            SELECT c.cage_id, c.group_id, c.cage_number, c.label, g.name
            FROM cages c
            JOIN groups g ON g.group_id = c.group_id
            ORDER BY c.group_id, c.cage_number
            '''
        )
        return self._c.fetchall()

    def get_animals_in_cage_id(self, cage_id):
        """Returns animals assigned to a specific cage_id."""
        self._c.execute(
            '''
            SELECT animal_id
            FROM animals
            WHERE cage_id = ? AND active = 1
            ORDER BY animal_id
            ''',
            (cage_id,),
        )
        return self._c.fetchall()

    def get_cage_assignments(self):
        '''Returns a dictionary of animal IDs mapped to their cage assignments.'''
        cage_assignments = {}
        animals = self._c.execute(
            '''
            SELECT animal_id, group_id, cage_id
            FROM animals
            WHERE active = 1
            ORDER BY animal_id
            '''
        ).fetchall()
        for animal_id, group_id, cage_id in animals:
            cage_assignments[animal_id] = (group_id, cage_id)

        return cage_assignments

    def get_groups(self):
        '''Returns a list of all group names in the database.'''
        self._c.execute("SELECT name FROM groups ORDER BY group_id")
        return [group[0] for group in self._c.fetchall()]

    def update_group_names(self, group_names):
        """Update group names in order of group_id.

        This keeps existing group rows and only renames them.
        """
        self._c.execute("SELECT group_id FROM groups ORDER BY group_id")
        rows = self._c.fetchall()
        group_ids = [row[0] for row in rows]
        for index, group_id in enumerate(group_ids):
            if index < len(group_names):
                self._c.execute(
                    "UPDATE groups SET name = ? WHERE group_id = ?",
                    (group_names[index], group_id),
                )
        self._conn.commit()

    def get_animal_current_cage(self, animal_id):
        '''Returns the current cage_id for an animal'''
        self._c.execute('''
            SELECT cage_id
            FROM animals
            WHERE animal_id = ? AND active = 1
        ''', (animal_id,))
        result = self._c.fetchone()
        return result[0] if result else None

    def update_animal_cage(self, animal_id, new_group_id):
        '''Updates an animal's cage assignment by updating its cage_id and group_id'''
        try:
            # Get current group_id
            self._c.execute('''
                SELECT group_id
                FROM animals
                WHERE animal_id = ? AND active = 1
            ''', (animal_id,))
            old_group = self._c.fetchone()

            # new_group_id is now a cage_id
            cage_id = new_group_id
            self._c.execute(
                "SELECT group_id FROM cages WHERE cage_id = ?",
                (cage_id,),
            )
            new_group_row = self._c.fetchone()
            if not new_group_row:
                return False
            new_group_id = new_group_row[0]

            if old_group:
                old_group_id = old_group[0]

                # Update animal's group + cage
                self._c.execute(
                    '''
                    UPDATE animals
                    SET group_id = ?, cage_id = ?
                    WHERE animal_id = ? AND active = 1
                    ''',
                    (new_group_id, cage_id, animal_id),
                )

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

    def get_measurement_type(self):
        '''Returns whether the measurement is automatic (1) or manual (0).'''
        self._c.execute("SELECT measurement_type FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else 0  # Default to manual (0)

    def update_measurement_type(self, measurement_type):
        '''Updates measurement_type in the experiment table.'''
        self._c.execute("UPDATE experiment SET measurement_type = ?", (measurement_type,))
        self._conn.commit()

    def get_measurement_mode(self):
        """Returns measurement mode: 'tumor' or 'weight'."""
        self._c.execute("SELECT measurement_mode FROM experiment")
        result = self._c.fetchone()
        return result[0] if result and result[0] else "weight"

    def set_measurement_mode(self, mode):
        """Set measurement mode for experiment."""
        self._c.execute("UPDATE experiment SET measurement_mode = ?", (mode,))
        self._conn.commit()

    def get_calc_method(self):
        self._c.execute("SELECT calc_method FROM experiment")
        result = self._c.fetchone()
        return int(result[0]) if result and result[0] is not None else 0

    def get_tumors_per_animal(self):
        self._c.execute("SELECT tumors_per_animal FROM experiment")
        result = self._c.fetchone()
        return int(result[0]) if result and result[0] is not None else 1

    def get_tumor_labels(self):
        self._c.execute("SELECT tumor_labels FROM experiment")
        result = self._c.fetchone()
        if not result or not result[0]:
            return ["Tumor 1"]
        return [t.strip() for t in str(result[0]).split(",") if t.strip()]

    def get_organization(self):
        self._c.execute("SELECT organization FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else None

    def get_cell_line(self):
        self._c.execute("SELECT cell_line FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else None

    def get_strain(self):
        self._c.execute("SELECT strain FROM experiment")
        result = self._c.fetchone()
        return result[0] if result else None

    def _assign_animal_to_cage(self, group_id):
        """Assign animal to a cage within group, creating cages if needed."""
        self._c.execute("SELECT cage_capacity FROM groups WHERE group_id = ?", (group_id,))
        row = self._c.fetchone()
        capacity = int(row[0]) if row and row[0] else 1

        self._c.execute("SELECT COUNT(*) FROM animals WHERE group_id = ?", (group_id,))
        count_row = self._c.fetchone()
        existing_count = count_row[0] if count_row else 0
        # Determine cage number for the next animal
        cage_number = (existing_count // capacity) + 1

        # Find existing cage
        self._c.execute(
            "SELECT cage_id FROM cages WHERE group_id = ? AND cage_number = ?",
            (group_id, cage_number),
        )
        existing = self._c.fetchone()
        if existing:
            return existing[0]

        # Create new cage
        self._c.execute(
            "INSERT INTO cages (group_id, cage_number, label) VALUES (?, ?, ?)",
            (group_id, cage_number, f"Cage {cage_number}"),
        )
        return self._c.lastrowid

    def ensure_tumors_for_animal(self, animal_id):
        """Create tumors for animal if missing."""
        self._c.execute("SELECT COUNT(*) FROM tumors WHERE animal_id = ?", (animal_id,))
        count = self._c.fetchone()[0]
        if count and count > 0:
            return

        self._c.execute("SELECT group_id, cage_id FROM animals WHERE animal_id = ?", (animal_id,))
        row = self._c.fetchone()
        if not row:
            return
        group_id, cage_id = row
        tumors_per_animal = self.get_tumors_per_animal()
        labels = self.get_tumor_labels()
        # Pad labels if needed
        while len(labels) < tumors_per_animal:
            labels.append(f"Tumor {len(labels) + 1}")

        for tumor_index in range(1, tumors_per_animal + 1):
            measurement_order = (int(animal_id) - 1) * tumors_per_animal + tumor_index
            self._c.execute(
                '''INSERT INTO tumors (
                    animal_id, group_id, cage_id, tumor_index, location_label,
                    measurement_order, date_removed, censored
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    animal_id,
                    group_id,
                    cage_id,
                    tumor_index,
                    labels[tumor_index - 1],
                    measurement_order,
                    None,
                    0,
                ),
            )
        self._conn.commit()

    def get_tumors_for_animal(self, animal_id):
        self._c.execute(
            '''SELECT tumor_id, tumor_index, location_label, measurement_order, date_removed, censored
               FROM tumors
               WHERE animal_id = ?
               ORDER BY tumor_index''',
            (animal_id,),
        )
        return self._c.fetchall()

    def get_all_tumors(self):
        self._c.execute(
            '''SELECT tumor_id, animal_id, group_id, cage_id, tumor_index, location_label, measurement_order
               FROM tumors
               ORDER BY measurement_order'''
        )
        return self._c.fetchall()

    def add_tumor_measurement(self, tumor_id, date_measured, length, width, status="measured"):
        self._c.execute(
            '''INSERT INTO tumor_measurements (tumor_id, date_measured, length, width, status)
               VALUES (?, ?, ?, ?, ?)''',
            (tumor_id, date_measured, length, width, status),
        )
        self._conn.commit()

    def upsert_tumor_measurement(self, tumor_id, date_measured, length, width, status="measured"):
        allowed = {"measured", "dead", "skipped", "censored"}
        if status not in allowed:
            status = "measured"
        self._c.execute(
            '''SELECT measurement_id FROM tumor_measurements
               WHERE tumor_id = ? AND date_measured = ?''',
            (tumor_id, date_measured),
        )
        row = self._c.fetchone()
        if row:
            self._c.execute(
                '''UPDATE tumor_measurements
                   SET length = ?, width = ?, status = ?
                   WHERE tumor_id = ? AND date_measured = ?''',
                (length, width, status, tumor_id, date_measured),
            )
        else:
            self._c.execute(
                '''INSERT INTO tumor_measurements (tumor_id, date_measured, length, width, status)
                   VALUES (?, ?, ?, ?, ?)''',
                (tumor_id, date_measured, length, width, status),
            )
        self._conn.commit()

    def get_tumor_measurements_by_date(self, date_measured):
        self._c.execute(
            '''SELECT t.tumor_id, t.animal_id, t.group_id, t.cage_id, t.tumor_index,
                      m.date_measured, m.length, m.width, m.status
               FROM tumor_measurements m
               JOIN tumors t ON t.tumor_id = m.tumor_id
               WHERE m.date_measured = ?
               ORDER BY t.measurement_order''',
            (date_measured,),
        )
        return self._c.fetchall()

    def get_tumor_measurement(self, tumor_id, date_measured):
        self._c.execute(
            '''SELECT length, width, status
               FROM tumor_measurements
               WHERE tumor_id = ? AND date_measured = ?''',
            (tumor_id, date_measured),
        )
        return self._c.fetchone()

    def get_tumor_measurements_for_group_date(self, group_id, date_measured):
        self._c.execute(
            '''SELECT t.tumor_id, t.animal_id, t.tumor_index, t.location_label,
                      m.length, m.width, m.status
               FROM tumor_measurements m
               JOIN tumors t ON t.tumor_id = m.tumor_id
               WHERE t.group_id = ? AND m.date_measured = ?
               ORDER BY t.measurement_order''',
            (group_id, date_measured),
        )
        return self._c.fetchall()

    def get_all_animal_ids(self):
        '''Returns a list of all active animal IDs that have RFIDs mapped to them.'''
        self._c.execute('''
            SELECT animal_id
            FROM animals
            WHERE rfid IS NOT NULL
            AND active = 1
        ''')
        return [animal[0] for animal in self._c.fetchall()]

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
        2. Animals table with RFID mappings
        3. Groups table with header
        """
        import os
        import pandas as pd

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

            # Write animals section to always include animal_id/rfid mapping
            f.write("### Table: animals ###\n")
            animals_df.to_csv(f, index=False)
            f.write("\n")

            # Write measurement matrix
            pivot_df.to_csv(f, index=False)
            f.write("\n")

            # Write groups section
            f.write("### Table: groups ###\n")
            groups_df.to_csv(f, index=False)

        print(f"Exported to formatted CSV: {output_file}")


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
        self._c.execute("SELECT group_id, active FROM animals WHERE animal_id = ?", (animal_id,))
        row = self._c.fetchone()
        if row:
            group_id, current_status = row
            if int(current_status) != int(status):
                if int(status) == 0:
                    self._c.execute(
                        "UPDATE groups SET num_animals = CASE WHEN num_animals > 0 THEN num_animals - 1 ELSE 0 END WHERE group_id = ?",
                        (group_id,),
                    )
                else:
                    self._c.execute(
                        "UPDATE groups SET num_animals = num_animals + 1 WHERE group_id = ?",
                        (group_id,),
                    )
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
            self._ensure_cages_for_groups()
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
            self._ensure_cages_for_groups()
            return True

        except Exception as e:
            print(f"Error during autosort: {e}")
            self._conn.rollback()
            return False

    def get_cage_number(self, cage_name):
        self._c.execute('''
                        SELECT group_id FROM groups
                        WHERE name = ?''', (cage_name,))
        result = self._c.fetchone()
        return result[0] if result else None

    def assign_cages_for_group(self, group_id):
        """Rebuild cages for group and assign animals sequentially."""
        self._c.execute("SELECT cage_capacity FROM groups WHERE group_id = ?", (group_id,))
        row = self._c.fetchone()
        capacity = int(row[0]) if row and row[0] else 1
        self._c.execute("DELETE FROM cages WHERE group_id = ?", (group_id,))
        self._c.execute(
            "SELECT animal_id FROM animals WHERE group_id = ? AND active = 1 ORDER BY animal_id",
            (group_id,),
        )
        animal_ids = [row[0] for row in self._c.fetchall()]
        num_cages = max(1, (len(animal_ids) + capacity - 1) // capacity)
        cage_ids = []
        for cage_number in range(1, num_cages + 1):
            self._c.execute(
                "INSERT INTO cages (group_id, cage_number, label) VALUES (?, ?, ?)",
                (group_id, cage_number, f"Cage {cage_number}"),
            )
            cage_ids.append(self._c.lastrowid)
        for idx, animal_id in enumerate(animal_ids):
            cage_idx = idx // capacity
            cage_id = cage_ids[min(cage_idx, len(cage_ids) - 1)]
            self._c.execute(
                "UPDATE animals SET cage_id = ? WHERE animal_id = ?",
                (cage_id, animal_id),
            )
        self._conn.commit()
