from pathlib import Path
import pandas as pd

class DataCollectionDatabase:
    def __init__(self, experiment: str = None, measurement_items: list = ["Weight", "Length"]):
        if not experiment:
            self.filename = "data.csv"
        else:
            self.filename = experiment + ".csv"
        
        self.filename = "database_apis/fake_data/" + self.filename
        path = Path(self.filename)
        if not path.is_file():
            f = open(self.filename, "x")
            string = "Date,Animal ID,"
            for item in measurement_items:
                string += item[1] + ","
            string = string[:-1]
            f.write(string)
            f.close()
        
        self.measurement_items = measurement_items
      
    def get_all_data(self):
        data_file = pd.read_csv(self.filename)
        list_of_csv = [tuple(row) for row in data_file.values]
        return list_of_csv
          
    def get_data_for_date(self, date: str):
        data = self.get_all_data()
        new_data = []
        for entry in data:
            if entry[0] == date:
                new_data.append(entry)
        return new_data
    
    def set_data_for_entry(self, values: tuple):
        data_file = pd.read_csv(self.filename)
        data = self.get_all_data()
        found = False
        for i, entry in enumerate(data):
            if entry[0] == values[0] and entry[1] == values[1]:
                found = True
                for x, item in enumerate(self.measurement_items):
                    data_file.loc[i, item] = values[x+2]
        if not found:
            data_file.loc[len(data_file.index)] = values
                
        data_file.to_csv(self.filename, index=False)