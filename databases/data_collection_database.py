import os
import csv
from pathlib import Path
from shared.file_utils import create_temp_copy, save_temp_to_file

class DataCollectionDatabase:
    def __init__(self, experiment: str = None, measurement_items: list = ["Weight", "Length"]):
        # Get the experiment name and file path
        self.experiment_name = os.path.splitext(os.path.basename(experiment))[0] if experiment else "data"
        self.filename = f"{self.experiment_name}.csv"
        self.measurement_items = measurement_items
        self.data = []  # In-memory storage for data entries
        self.modified = False  # Flag to track if data has changed

        # Ensure the CSV file exists with headers
        if not Path(self.filename).is_file():
            with open(self.filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Date", "Animal ID"] + self.measurement_items)
        
        # Load data from the temporary file
        self.temp_file_path = create_temp_copy(self.filename)
        self.load_data()

    def load_data(self):
        """Load data from CSV into the in-memory list."""
        self.data.clear()  # Clear any existing in-memory data
        if Path(self.temp_file_path).is_file():
            with open(self.temp_file_path, mode='r') as file:
                reader = csv.DictReader(file)
                self.data.extend(reader)  # Append rows to self.data

    def get_all_data(self):
        """Returns all data entries from in-memory storage."""
        return self.data
    
    def get_data_for_date(self, date: str):
        """Returns entries for a specific date from in-memory data."""
        return [entry for entry in self.data if entry["Date"] == date]


    def set_data_for_entry(self, values: tuple):
        """Sets or updates data entries in the database and exports immediately."""
        print("Saving data:", values)  # Debugging print
        self.export_to_csv()  # Save immediately after setting data
        """Sets or updates data entries in the CSV or database directly upon entry."""
        date, animal_id, *measurements = values

        # Load current data if not already loaded
        self.load_data()
        
        # Find if the entry exists and update it
        entry_found = False
        for entry in self.data:
            if entry["Date"] == date and entry["Animal ID"] == animal_id:
                for i, item in enumerate(self.measurement_items):
                    entry[item] = measurements[i]
                entry_found = True
                break

        if not entry_found:
            # Add a new entry if it does not exist
            new_entry = {"Date": date, "Animal ID": animal_id}
            for i, item in enumerate(self.measurement_items):
                new_entry[item] = measurements[i]
            self.data.append(new_entry)

        self.export_to_csv()

    def save(self):
        """Saves in-memory data to the CSV file if modified, using temporary file."""
        if self.modified:
            # Export in-memory data to temporary file first
            with open(self.temp_file_path, mode='w', newline='') as file:
                fieldnames = ["Date", "Animal ID", "Weight"] + self.measurement_items
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.data)

            # Save from temp file to the main file
            save_temp_to_file(self.temp_file_path, self.filename)
            self.modified = False
