import sqlite3

class idDatabase:
    def __init__(self):
        self._conn = sqlite3.connect('conversion.db')
        try:
            self._conn.execute('''CREATE TABLE conversion (
                      rfid INTEGER,
                      animalid INTEGER);''')
            self._conn.commit()
        except:
            pass
 
    def addAnimal(self, rf, id):
        self._conn.execute("INSERT INTO conversion (rfid, animalid)\
                VALUES ('{}', '{}')".format(rf, id));

    def getAnimals(self):
        cursor = self._conn.execute("SELECT rfid, animalid from conversion")
        animals = []
        for row in cursor:
            animals.append((row[0], row[1]))
        return animals

    def close(self):
        self._conn.close()


if __name__ == "__main__":
    db = idDatabase()
    db.addAnimal(1234, 1111)
    print(db.getAnimals())
