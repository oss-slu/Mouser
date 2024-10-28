# pylint: skip-file
from pathlib import Path
import pandas as pd
import os

class DataCollectionDatabase:
    def __init__(self, experiment: str = None, measurement_items: list = ["Weight", "Length"]):

        #gets the name of the file from the file path
        experiment_name = os.path.basename(experiment)
        experiment_name = os.path.splitext(experiment_name)[0]


    #     if not experiment_name:
    #         self.filename = "data.csv"
    #     else:
    #         self.filename = experiment_name + ".csv"
        
    #     self.filename = "database_apis/fake_data/" + self.filename
    #     try:
    #         os.mkdir("./database_apis/fake_data/")
    #     except:
    #         pass
    #     path = Path(self.filename)
    #     if not path.is_file():
    #         f = open(self.filename, "x")
    #         string = "Date,Animal ID,"
    #         for item in measurement_items:
    #             string += item + ","
    #         string = string[:-1]
    #         f.write(string)
    #         f.close()
        
    #     self.measurement_items = measurement_items
      
        # Updated to ensure the file creation logic works if the file doesn’t exist
        # path = Path(self.filename)
        # if not path.is_file():
        #     with open(self.filename, 'w') as f:
        #         headers = "Date,Animal ID," + ",".join(self.measurement_items) + "\n"
        #         f.write(headers)



    def get_all_data(self):
    #     data_file = pd.read_csv(self.filename)
    #     list_of_csv = [tuple(row) for row in data_file.values]
        return []
          
    def get_data_for_date(self, date: str):
    #     data = self.get_all_data()
    #     new_data = []
    #     for entry in data:
    #         if entry[0] == date:
    #             new_data.append(entry)
        return []
    
    def set_data_for_entry(self, values: tuple):
    #     data_file = pd.read_csv(self.filename)
    #     data = self.get_all_data()
    #     for i, entry in enumerate(data):
    #         if entry[0] == values[0] and entry[1] == values[1]:
    #             for x, item in enumerate(self.measurement_items):
    #                 data_file.loc[i, item] = values[x+2]
    #             break
    #     else:
    #         data_file.loc[len(data_file.index)] = values
                
    #     data_file.to_csv(self.filename, index=False)
        data = []

    # updated the set_data_for_entry method so it can properly write data to the CSV file
    # def set_data_for_entry(self, values: tuple):
    #     """Sets or updates data entries in the CSV file."""
    #     data_file = pd.read_csv(self.filename)

    #     # Check if entry already exists
    #     for i, entry in data_file.iterrows():
    #         if entry['Date'] == values[0] and entry['Animal ID'] == values[1]:
    #             # Update existing entry
    #             for x, item in enumerate(self.measurement_items):
    #                 data_file.loc[i, item] = values[x + 2]
    #             break
    #     else:
    #         # Add new entry if it doesn't exist
    #         new_row = pd.Series(values, index=data_file.columns)
    #         data_file = data_file.append(new_row, ignore_index=True)

    #     data_file.to_csv(self.filename, index=False)
