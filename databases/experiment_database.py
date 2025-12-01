"""SQLite Database module for Mouser."""
import sqlite3
import os
from datetime import datetime


class ExperimentDatabase:
    """SQLite Database Object for Experiments (singleton per DB file)."""

    _instances = {}  # Singleton per database file

    def __new__(cls, file=":memory:"):
        """Create or reuse the SQLite connection for a given database file."""
        if file not in cls._instances:
            instance = super().__new__(cls)

            abs_path = file if file == ":memory:" else os.path.abspath(file)
            instance.db_file = abs_path

            instance._conn = sqlite3.connect(
                abs_path,
                timeout=5.0,
                check_same_thread=False
            )
            instance._c = instance._conn.cursor()
            instance._initialize_tables()

            cls._instances[file] = instance

        return cls._instances[file]

    def _initialize_tables(self):
        """Create required tables only if they do not already exist."""
        try:
            # Experiment table
            self._c.execute(
                """CREATE TABLE experiment (
                    name TEXT,
                    species TEXT,
                    uses_rfid INTEGER,
                    num_animals INTEGER,
                    num_groups INTEGER,
                    cage_max INTEGER,
                    measurement_type INTEGER,
                    id TEXT,
                    investigators TEXT,
                    measurement TEXT
                );"""
            )

            # Animals
            self._c.execute(
                """CREATE TABLE animals (
                    animal_id INTEGER PRIMARY KEY,
                    group_id INTEGER,
                    rfid TEXT UNIQUE,
                    remarks TEXT,
                    active INTEGER
                );"""
            )

            # Measurements
            self._c.execute(
                """CREATE TABLE animal_measurements (
                    measurement_id INTEGER,
                    animal_id INTEGER,
                    timestamp TEXT,
                    value REAL,
                    FOREIGN KEY(animal_id) REFERENCES animals(animal_id),
                    PRIMARY KEY (animal_id, timestamp, measurement_id)
                );"""
            )

            # Groups
            self._c.execute(
                """CREATE TABLE groups (
                    group_id INTEGER PRIMARY KEY,
                    name TEXT,
                    num_animals INTEGER,
                    cage_capacity INTEGER
                );"""
            )

            self._conn.commit()

        except sqlite3.OperationalError:
            # Tables already exist
            pass

    def setup_experiment(self, *args, **kwargs):
        """Supports both new and old experiment signatures."""
        # New signature if kwargs exist
        if kwargs:
            return self._setup_experiment_new(**kwargs)

        # New signature positional
        if len(args) == 10:
            return self._setup_experiment_new(*args)

        # Old signature expected by tests
        return self._setup_experiment_old(*args)

    def _setup_experiment_old(self, *args):
        """
        OLD SIGNATURE:
        name, species, uses_rfid, num_animals, num_groups,
        cage_max, experiment_id, investigators(list), measurement
        """
        if len(args) != 9:
            raise TypeError("Invalid old setup_experiment signature")

        (
            name,
            species,
            uses_rfid,
            num_animals,
            num_groups,
            cage_max,
            experiment_id,
            investigators,
            measurement
        ) = args

        # Old signature had no measurement_type → assume manual=0
        measurement_type = 0

        return self._setup_experiment_new(
            name,
            species,
            uses_rfid,
            num_animals,
            num_groups,
            cage_max,
            measurement_type,
            experiment_id,
            investigators,
            measurement
        )

    def _setup_experiment_new(
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
        measurement
    ):
        """Actual experiment insert logic."""
        investigators_str = ", ".join(investigators)

        self._c.execute(
            """INSERT INTO experiment (
                name, species, uses_rfid, num_animals, num_groups,
                cage_max, measurement_type, id, investigators, measurement
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name, species, uses_rfid, num_animals, num_groups,
                cage_max, measurement_type, experiment_id,
                investigators_str, measurement
            )
        )
        self._conn.commit()

    def get_number_groups(self):
        self._c.execute("SELECT COUNT(*) FROM groups")
        res = self._c.fetchone()
        return res[0] if res else 0

    def get_number_animals(self):
        self._c.execute("SELECT COUNT(*) FROM animals WHERE active = 1")
        res = self._c.fetchone()
        return res[0] if res else 0

    def get_total_number_animals(self):
        self._c.execute("SELECT num_animals FROM experiment")
        row = self._c.fetchone()
        return row[0] if row else 0

    def get_groups(self):
        self._c.execute("SELECT name FROM groups")
        return [g[0] for g in self._c.fetchall()]

    def get_cage_capacity(self, group_id):
        self._c.execute("SELECT cage_capacity FROM groups WHERE group_id = ?", (group_id,))
        row = self._c.fetchone()
        return row[0] if row else None

    def get_animal_rfid(self, animal_id):
        self._c.execute("SELECT rfid FROM animals WHERE animal_id=?", (animal_id,))
        row = self._c.fetchone()
        return row[0] if row else None

    def get_all_animals_rfid(self):
        self._c.execute("""SELECT rfid FROM animals 
                           WHERE active=1 AND rfid IS NOT NULL 
                           ORDER BY animal_id""")
        return [r[0] for r in self._c.fetchall()]

    def get_animal_id(self, rfid):
        self._c.execute("SELECT animal_id FROM animals WHERE rfid=?", (rfid,))
        row = self._c.fetchone()
        return row[0] if row else None

    def get_animals_in_cage(self, group_name):
        """Return active animals based on group name."""
        try:
            self._c.execute(
                """SELECT animal_id
                   FROM animals
                   WHERE group_id = (
                        SELECT group_id FROM groups WHERE name = ?
                   ) AND active = 1
                   ORDER BY animal_id""",
                (group_name,)
            )
            return self._c.fetchall()
        except sqlite3.Error:
            return []

    def get_cage_assignments(self):
        """Return animal_id → (group_id, cage_number)."""
        assignments = {}
        groups = self._c.execute("SELECT group_id, cage_capacity FROM groups").fetchall()

        for gid, capacity in groups:
            animals = self._c.execute(
                """SELECT animal_id 
                   FROM animals 
                   WHERE group_id=? AND active=1
                   ORDER BY animal_id""",
                (gid,)
            ).fetchall()

            for idx, (animal_id,) in enumerate(animals):
                cage_number = (idx // capacity) + 1
                assignments[animal_id] = (gid, cage_number)

        return assignments

    def get_cages_by_group(self):
        """Return dictionary: group_id → list of cage numbers."""
        self._c.execute("SELECT group_id, cage_capacity FROM groups")
        out = {}
        for gid, capacity in self._c.fetchall():
            animal_count = self.get_group_animal_count(gid)
            num_cages = (animal_count + capacity - 1) // capacity
            out[gid] = list(range(1, num_cages + 1))
        return out

    def get_group_animal_count(self, group_id):
        self._c.execute(
            """SELECT COUNT(*) FROM animals 
               WHERE group_id=? AND active=1""",
            (group_id,)
        )
        return self._c.fetchone()[0]


    def get_measurement_name(self):
        self._c.execute("SELECT measurement FROM experiment")
        row = self._c.fetchone()
        return row[0] if row else None

    def get_measurement_type(self):
        self._c.execute("SELECT measurement_type FROM experiment")
        row = self._c.fetchone()
        return row[0] if row else 0

    def add_data_entry(self, date, animal_id, values, measurement_id=1):
        try:
            value = values[0] if isinstance(values, (list, tuple)) else values
            self._c.execute(
                """INSERT INTO animal_measurements 
                   (animal_id, timestamp, value, measurement_id)
                   VALUES (?, ?, ?, ?)""",
                (animal_id, date, value, measurement_id)
            )
            self._conn.commit()
        except sqlite3.Error:
            self._conn.rollback()

    def change_data_entry(self, date, animal_id, value, measurement_id=1):
        try:
            self._c.execute(
                """UPDATE animal_measurements
                   SET value=?
                   WHERE animal_id=? AND timestamp=? AND measurement_id=?""",
                (value, animal_id, date, measurement_id)
            )
            if self._c.rowcount == 0:
                self.add_data_entry(date, animal_id, value, measurement_id)
            self._conn.commit()
        except sqlite3.Error:
            self._conn.rollback()

    def get_data_for_date(self, date):
        try:
            self._c.execute(
                """SELECT animal_id, value
                   FROM animal_measurements
                   WHERE timestamp=? AND (measurement_id=1)""",
                (date,)
            )
            return self._c.fetchall()
        except sqlite3.Error:
            return []

    def export_to_csv(self, directory):
        import pandas as pd

        self._c.execute("SELECT name FROM experiment")
        row = self._c.fetchone()
        name = row[0] if row else "default_experiment"

        folder = os.path.join(directory, name)
        os.makedirs(folder, exist_ok=True)

        tables = {
            'experiment': 'experiment.csv',
            'animals': 'animals.csv',
            'animal_measurements': 'animal_measurements.csv',
            'groups': 'groups.csv',
        }

        for table, filename in tables.items():
            df = pd.read_sql_query(f"SELECT * FROM {table}", self._conn)
            df.to_csv(os.path.join(folder, filename), index=False)

    def randomize_cages(self):
        import random

        try:
            # Get all groups
            groups = self._c.execute(
                "SELECT group_id, cage_capacity FROM groups ORDER BY group_id"
            ).fetchall()

            # Shuffle active animals
            animals = [a[0] for a in self._c.execute(
                "SELECT animal_id FROM animals WHERE active=1"
            ).fetchall()]
            random.shuffle(animals)

            self._c.execute("UPDATE groups SET num_animals=0")

            idx = 0
            for animal_id in animals:
                gid, capacity = groups[idx]

                # Check if group is full
                count = self._c.execute(
                    "SELECT num_animals FROM groups WHERE group_id=?",
                    (gid,)
                ).fetchone()[0]

                if count >= capacity:
                    idx += 1
                    if idx >= len(groups):
                        idx = 0
                    gid, capacity = groups[idx]

                # Assign animal
                self._c.execute(
                    "UPDATE animals SET group_id=? WHERE animal_id=?",
                    (gid, animal_id)
                )
                self._c.execute(
                    "UPDATE groups SET num_animals=num_animals+1 WHERE group_id=?",
                    (gid,)
                )

            self._conn.commit()
            return True

        except sqlite3.Error:
            self._conn.rollback()
            return False

    def autosort(self):
        """Sort animals by size (largest ↔ smallest alternating)."""
        try:
            # Fetch latest measurements
            self._c.execute(
                """SELECT a.animal_id, m.value, MAX(m.timestamp)
                   FROM animals a
                   JOIN animal_measurements m ON a.animal_id=m.animal_id
                   WHERE a.active=1
                   GROUP BY a.animal_id"""
            )
            measurements = self._c.fetchall()

            measurements.sort(key=lambda x: x[1], reverse=True)

            # Mark used measurements
            for animal_id, _, timestamp in measurements:
                self._c.execute(
                    "UPDATE animal_measurements SET measurement_id=0 WHERE animal_id=? AND timestamp=?",
                    (animal_id, timestamp)
                )

            groups = self._c.execute(
                "SELECT group_id, cage_capacity FROM groups"
            ).fetchall()

            # Reset
            self._c.execute("UPDATE groups SET num_animals=0")

            large = 0
            small = len(measurements) - 1
            use_large = True

            while large <= small:
                for gid, capacity in groups:
                    if large > small:
                        break

                    # Check space
                    count = self._c.execute(
                        "SELECT num_animals FROM groups WHERE group_id=?", (gid,)
                    ).fetchone()[0]
                    if count >= capacity:
                        continue

                    # Choose animal
                    if use_large:
                        animal_id = measurements[large][0]
                        large += 1
                    else:
                        animal_id = measurements[small][0]
                        small -= 1

                    # Assign
                    self._c.execute(
                        "UPDATE animals SET group_id=? WHERE animal_id=?",
                        (gid, animal_id)
                    )
                    self._c.execute(
                        "UPDATE groups SET num_animals=num_animals+1 WHERE group_id=?",
                        (gid,)
                    )

                use_large = not use_large

            self._conn.commit()
            return True

        except sqlite3.Error:
            self._conn.rollback()
            return False

    def close(self):
        """Close SQLite connection and remove from singleton registry."""
        try:
            if self._conn:
                self._conn.commit()

                if hasattr(self, "_c") and self._c:
                    self._c.close()
                    self._c = None

                self._conn.close()
                self._conn = None

                if self.db_file in ExperimentDatabase._instances:
                    del ExperimentDatabase._instances[self.db_file]

                return True

        except sqlite3.Error:
            return False
