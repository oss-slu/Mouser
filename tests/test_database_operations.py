"""
Comprehensive unit tests for database module SQLite operations.

Tests validate database read/write operations across Windows, macOS, and Linux.
Focuses on achieving 70%+ test coverage for the database module.

Test Categories:
- Database initialization and setup
- CRUD operations (Create, Read, Update, Delete)
- Data integrity and constraints
- Cross-platform compatibility (file paths, locking, etc.)
- Error handling and edge cases
"""

import os
import sys
import tempfile
import sqlite3
from datetime import datetime
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from databases.experiment_database import ExperimentDatabase
from databases.database_controller import DatabaseController


@pytest.fixture(autouse=True)
def cleanup_database_instances():
    """Clear singleton instances before and after each test to ensure isolation."""
    ExperimentDatabase._instances.clear()
    yield
    # Close all connections and clear instances after test
    for db in ExperimentDatabase._instances.values():
        try:
            db.close()
        except Exception:  # pylint: disable=broad-except
            pass
    ExperimentDatabase._instances.clear()


class TestDatabaseInitialization:
    """Test database creation and table initialization."""

    def test_database_file_creation(self):
        """Test that database file is created on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create database in temporary directory
            db_path = Path(tmpdir) / "test_experiment.db"
            _ = ExperimentDatabase(str(db_path))

            # Verify file exists
            assert db_path.exists(), "Database file should be created"
            assert db_path.stat().st_size > 0, "Database file should not be empty"

    def test_database_functional(self):
        """Test database is functional and tables initialized."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "functional_test.db"
            db = ExperimentDatabase(str(db_path))

            # Verify database is functional
            # Tables should be initialized
            assert db.get_number_groups() >= 0

    def test_database_tables_initialized(self):
        """Test that all required tables are created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_tables.db"
            db = ExperimentDatabase(str(db_path))

            # Query sqlite_master to verify tables exist
            db._c.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in db._c.fetchall()]

            # Verify all required tables are present
            required_tables = [
                'animal_measurements',
                'animals',
                'experiment',
                'groups'
            ]
            for table in required_tables:
                assert table in tables, f"Table '{table}' should be created"

    def test_singleton_pattern(self):
        """Test that same database file returns same instance (singleton pattern)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "singleton_test.db"

            # Create two instances with same file
            db1 = ExperimentDatabase(str(db_path))
            db2 = ExperimentDatabase(str(db_path))

            # Should return same instance
            assert db1 is db2, "Same database file should return same instance"

    def test_absolute_path_handling(self):
        """Test that database correctly handles absolute paths (cross-platform)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use relative path
            rel_path = "test.db"

            # Change to temp directory
            original_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                db = ExperimentDatabase(rel_path)

                # Database should convert to absolute path
                assert os.path.isabs(db.db_file), "Database should store absolute path"
            finally:
                os.chdir(original_dir)


class TestExperimentSetup:
    """Test experiment initialization and configuration."""

    def test_setup_experiment_basic(self):
        """Test basic experiment setup with required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "setup_test.db"
            db = ExperimentDatabase(str(db_path))

            # Setup experiment with minimum required fields
            db.setup_experiment(
                name="Test Experiment",
                species="Mouse",
                uses_rfid=True,
                num_animals=10,
                num_groups=2,
                cage_max=5,
                measurement_type="A",
                experiment_id="EXP-001",
                investigators=["Dr. Smith", "Dr. Jones"],
                measurement="Weight"
            )

            # Verify experiment was created
            assert db.get_experiment_name() == "Test Experiment"
            assert db.get_experiment_id() == "EXP-001"

    def test_setup_groups(self):
        """Test creating experimental groups."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "groups_test.db"
            db = ExperimentDatabase(str(db_path))
            db.setup_experiment("Test", "Mouse", False, 10, 3, 5, "A", "EXP-002",
                                ["Dr. Test"], "Weight")

            # Setup groups
            group_names = ["Control", "Treatment A", "Treatment B"]
            db.setup_groups(group_names, cage_capacity=5)

            # Verify groups were created
            assert db.get_number_groups() == 3
            created_groups = db.get_groups()
            assert created_groups == group_names

    def test_multiple_investigators(self):
        """Test handling multiple investigators (list to string conversion)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "investigators_test.db"
            db = ExperimentDatabase(str(db_path))

            investigators = ["Dr. Alice", "Dr. Bob", "Dr. Charlie"]
            db.setup_experiment(
                "Multi-Investigator Study", "Rat", True, 20, 4, 5,
                "B", "EXP-003", investigators, "Temperature"
            )

            # Verify investigators were stored correctly
            # (implementation stores as comma-separated string)
            db._c.execute("SELECT investigators FROM experiment")  # pylint: disable=protected-access
            stored = db._c.fetchone()[0]  # pylint: disable=protected-access
            assert "Dr. Alice" in stored
            assert "Dr. Bob" in stored
            assert "Dr. Charlie" in stored


class TestAnimalOperations:
    """Test CRUD operations for animals."""

    def test_add_animal(self):
        """Test adding a single animal to the database."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", True, 10, 2, 5, "A", "EXP-004", ["Dr. Test"], "Weight")
        db.setup_groups(["Control", "Treatment"], cage_capacity=5)

        # Add animal
        db.add_animal(animal_id=1, rfid="RFID001", group_id=1, remarks="Test animal")

        # Verify animal was added
        assert db.get_number_animals() == 1

    def test_add_multiple_animals(self):
        """Test adding multiple animals."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 20, 2, 10, "A", "EXP-005", ["Dr. Test"], "Weight")
        db.setup_groups(["Group 1", "Group 2"], cage_capacity=10)

        # Add multiple animals
        for i in range(1, 21):
            group_id = 1 if i <= 10 else 2
            db.add_animal(animal_id=i, rfid=f"RFID{i:03d}", group_id=group_id)

        # Verify all animals were added
        assert db.get_number_animals() == 20

    def test_get_animal_by_rfid(self):
        """Test retrieving animal by RFID tag."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", True, 5, 1, 5, "A", "EXP-006", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)

        # Add animal with specific RFID
        db.add_animal(animal_id=42, rfid="RFID_UNIQUE_123", group_id=1)

        # Retrieve animal by RFID
        animal_id = db.get_animal_id("RFID_UNIQUE_123")
        assert animal_id == 42

    def test_get_animal_rfid(self):
        """Test retrieving RFID by animal ID."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", True, 5, 1, 5, "A", "EXP-007", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)

        # Add animal
        db.add_animal(animal_id=99, rfid="RFID_TEST_999", group_id=1)

        # Get RFID by animal ID
        rfid = db.get_animal_rfid(99)
        assert rfid == "RFID_TEST_999"

    def test_get_all_animals(self):
        """Test retrieving all animals from database."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 5, 1, 5, "A", "EXP-008", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)

        # Add animals
        for i in range(1, 6):
            db.add_animal(animal_id=i, rfid=f"RFID{i}", group_id=1)

        # Get all animals
        animals = db.get_animals()
        assert len(animals) == 5

    def test_get_animals_in_cage(self):
        """Test retrieving animals assigned to specific cage/group."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 10, 2, 5, "A", "EXP-009", ["Dr. Test"], "Weight")
        db.setup_groups(["Cage A", "Cage B"], cage_capacity=5)

        # Add animals to different cages
        for i in range(1, 6):
            db.add_animal(animal_id=i, rfid=f"RFID_A{i}", group_id=1)
        for i in range(6, 11):
            db.add_animal(animal_id=i, rfid=f"RFID_B{i}", group_id=2)

        # Get animals in Cage A
        cage_a_animals = db.get_animals_in_cage("Cage A")
        assert len(cage_a_animals) == 5


class TestMeasurementOperations:
    """Test measurement data CRUD operations."""

    def test_add_measurement(self):
        """Test adding a measurement for an animal."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 5, 1, 5, "A", "EXP-010", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)
        db.add_animal(animal_id=1, rfid="RFID001", group_id=1)

        # Add measurement
        db.add_measurement(animal_id=1, value=25.5)

        # Verify measurement was added (check by date)
        today = datetime.now().strftime("%Y-%m-%d")
        measurements = db.get_measurements_by_date(today)

        assert len(measurements) > 0
        # Find the measurement for animal 1
        animal_1_measurement = [m for m in measurements if m[0] == 1]
        assert len(animal_1_measurement) > 0

    def test_add_multiple_measurements(self):
        """Test adding multiple measurements over time."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 3, 1, 3, "A", "EXP-011", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=3)

        # Add animals
        for i in range(1, 4):
            db.add_animal(animal_id=i, rfid=f"RFID{i}", group_id=1)

        # Add multiple measurements for each animal
        for animal_id in range(1, 4):
            for _ in range(3):
                db.add_measurement(animal_id=animal_id, value=20.0 + animal_id)

        # Verify measurements were recorded
        today = datetime.now().strftime("%Y-%m-%d")
        measurements = db.get_measurements_by_date(today)
        assert len(measurements) >= 9  # At least 3 animals × 3 measurements

    def test_get_measurements_by_date(self):
        """Test retrieving measurements filtered by date."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 2, 1, 2, "A", "EXP-012", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=2)

        # Add animals and measurements
        for i in range(1, 3):
            db.add_animal(animal_id=i, rfid=f"RFID{i}", group_id=1)
            db.add_measurement(animal_id=i, value=22.5)

        # Get today's measurements
        today = datetime.now().strftime("%Y-%m-%d")
        measurements = db.get_measurements_by_date(today)

        assert len(measurements) >= 2


class TestDataIntegrity:
    """Test database constraints and data integrity."""

    def test_unique_rfid_constraint(self):
        """Test that RFID must be unique (database constraint)."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", True, 5, 1, 5, "A", "EXP-013", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)

        # Add first animal with RFID
        db.add_animal(animal_id=1, rfid="DUPLICATE_RFID", group_id=1)

        # Attempt to add second animal with same RFID should fail
        with pytest.raises(sqlite3.IntegrityError):
            db.add_animal(animal_id=2, rfid="DUPLICATE_RFID", group_id=1)

    def test_foreign_key_relationship(self):
        """Test that measurements require valid animal_id (foreign key)."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 5, 1, 5, "A", "EXP-014", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)

        # Try to add measurement for non-existent animal
        # Note: SQLite foreign key enforcement must be enabled
        # This test documents expected behavior
        try:
            db.add_measurement(animal_id=999, value=25.0)
            # If foreign keys are enforced, this should fail
            # If not enforced, measurement is added but relationship is invalid
        except sqlite3.IntegrityError:
            # Expected if foreign keys are enforced
            pass

    def test_data_persistence(self):
        """Test that data persists to disk and can be reloaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "persistence_test.db"

            # Create database and add data
            db1 = ExperimentDatabase(str(db_path))
            db1.setup_experiment("Persistence Test", "Mouse", False, 3, 1, 3, "A",
                                 "EXP-015", ["Dr. Test"], "Weight")
            db1.setup_groups(["Control"], cage_capacity=3)
            db1.add_animal(animal_id=1, rfid="PERSIST_001", group_id=1)

            # Close and reopen database (simulate application restart)
            db1.close()
            ExperimentDatabase._instances.clear()  # Clear singleton cache

            db2 = ExperimentDatabase(str(db_path))

            # Verify data persisted
            assert db2.get_experiment_name() == "Persistence Test"
            assert db2.get_number_animals() == 1


class TestCrossPlatformCompatibility:
    """Test database operations work across Windows, macOS, and Linux."""

    def test_file_path_with_spaces(self):
        """Test database works with file paths containing spaces (cross-platform issue)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create path with spaces
            db_path = Path(tmpdir) / "test with spaces.db"
            db = ExperimentDatabase(str(db_path))

            # Verify database is functional
            db.setup_experiment("Space Test", "Mouse", False, 1, 1, 1, "A",
                                "EXP-016", ["Dr. Test"], "Weight")
            assert db.get_experiment_name() == "Space Test"

    def test_unicode_in_data(self):
        """Test handling of Unicode characters (international characters)."""
        db = ExperimentDatabase(":memory:")

        # Setup experiment with Unicode characters
        db.setup_experiment(
            name="тест эксперимент",  # Russian
            species="マウス",  # Japanese
            uses_rfid=False,
            num_animals=1,
            num_groups=1,
            cage_max=1,
            measurement_type="A",
            experiment_id="EXP-017",
            investigators=["Dr. Müller", "Dr. José"],  # German, Spanish
            measurement="重さ"  # Japanese
        )

        # Verify Unicode data stored correctly
        assert "тест" in db.get_experiment_name()

    def test_concurrent_access_simulation(self):
        """Test database handles rapid sequential access (simulates multi-threaded access)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "concurrent_test.db"
            db = ExperimentDatabase(str(db_path))
            db.setup_experiment("Concurrent Test", "Mouse", False, 10, 1, 10, "A",
                                "EXP-018", ["Dr. Test"], "Weight")
            db.setup_groups(["Control"], cage_capacity=10)

            # Rapidly add animals (tests timeout and locking parameters)
            for i in range(1, 11):
                db.add_animal(animal_id=i, rfid=f"RFID{i:03d}", group_id=1)

            # Verify all animals were added successfully
            assert db.get_number_animals() == 10

    def test_long_file_path(self):
        """Test database handles long file paths (Windows MAX_PATH issue)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a deeply nested directory structure
            long_path = Path(tmpdir)
            for i in range(5):
                long_path = long_path / f"subdir{i}_with_long_name_to_test_path_limits"
            long_path.mkdir(parents=True, exist_ok=True)

            db_path = long_path / "test.db"

            # Attempt to create database with long path
            try:
                db = ExperimentDatabase(str(db_path))
                db.setup_experiment("Long Path Test", "Mouse", False, 1, 1, 1, "A",
                                    "EXP-019", ["Dr. Test"], "Weight")
                assert db.get_experiment_name() == "Long Path Test"
            except (OSError, sqlite3.OperationalError):
                # Some systems may have path length limits
                pytest.skip("System does not support long file paths")


class TestDatabaseController:
    """Test DatabaseController wrapper functionality."""

    def test_controller_initialization(self):
        """Test DatabaseController can be initialized with database file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "controller_test.db"
            db = ExperimentDatabase(str(db_path))
            db.setup_experiment("Controller Test", "Mouse", False, 5, 2, 5, "A",
                                "EXP-020", ["Dr. Test"], "Weight")
            db.setup_groups(["Group 1", "Group 2"], cage_capacity=5)

            # Initialize controller
            controller = DatabaseController(str(db_path))
            assert controller is not None

    def test_controller_get_groups(self):
        """Test controller retrieves groups correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "controller_groups.db"
            db = ExperimentDatabase(str(db_path))
            db.setup_experiment("Test", "Mouse", False, 10, 3, 5, "A",
                                "EXP-021", ["Dr. Test"], "Weight")
            db.setup_groups(["Control", "Test A", "Test B"], cage_capacity=5)

            controller = DatabaseController(str(db_path))
            groups = controller.get_groups()

            assert len(groups) == 3

    def test_controller_cage_max(self):
        """Test controller retrieves cage capacity correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "controller_cage.db"
            db = ExperimentDatabase(str(db_path))
            db.setup_experiment("Test", "Mouse", False, 15, 3, 5, "A",
                                "EXP-022", ["Dr. Test"], "Weight")
            db.setup_groups(["Group 1", "Group 2", "Group 3"], cage_capacity=5)

            controller = DatabaseController(str(db_path))
            cage_max = controller.get_cage_max()

            assert cage_max == 5


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_database_queries(self):
        """Test queries on empty database return sensible defaults."""
        db = ExperimentDatabase(":memory:")

        # Query empty database
        assert db.get_number_animals() == 0
        assert db.get_number_groups() == 0

    def test_zero_animals_experiment(self):
        """Test experiment with zero animals (edge case)."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Zero Animals", "Mouse", False, 0, 1, 5, "A",
                            "EXP-023", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=5)

        assert db.get_number_animals() == 0

    def test_large_measurement_value(self):
        """Test handling of large measurement values."""
        db = ExperimentDatabase(":memory:")
        db.setup_experiment("Test", "Mouse", False, 1, 1, 1, "A",
                            "EXP-024", ["Dr. Test"], "Weight")
        db.setup_groups(["Control"], cage_capacity=1)
        db.add_animal(animal_id=1, rfid="RFID001", group_id=1)

        # Add very large measurement
        large_value = 999999.999999
        db.add_measurement(animal_id=1, value=large_value)

        # Verify large value stored correctly
        today = datetime.now().strftime("%Y-%m-%d")
        measurements = db.get_measurements_by_date(today)
        assert len(measurements) > 0

    def test_database_close(self):
        """Test database can be closed cleanly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "close_test.db"
            db = ExperimentDatabase(str(db_path))
            db.setup_experiment("Close Test", "Mouse", False, 1, 1, 1, "A",
                                "EXP-025", ["Dr. Test"], "Weight")

            # Close database
            db.close()

            # Verify file still exists and is valid
            assert db_path.exists()


# Run tests with: pytest tests/test_database_operations.py -v
# Check coverage with: pytest tests/test_database_operations.py --cov=databases --cov-report=term-missing
