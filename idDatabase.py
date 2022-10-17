import sqlite3

class idDatabase:
    def __init__(self):
        self._conn = sqlite3.connect(':memory:') #can input file name instead of memory, need to add that functionality later.
        self._c = self._conn.cursor()
        try:
            self._c.execute('''CREATE TABLE conversion (
                                rfid INTEGER,
                                animalid INTEGER
                                );''')
            self._conn.commit()
        except:
            pass
 
    def addAnimal(self, rf, an):          #problem - can add animals with same rfid and/or animalid
        self._c.execute("INSERT INTO conversion VALUES (?, ?)", (rf, an))
        self._conn.commit()

    def getAnimals(self):
        self._c.execute("SELECT * FROM conversion")
        return self._c.fetchall()

    def getAnimalId(self, rf):
        self._c.execute("SELECT animalid FROM conversion WHERE rfid=?", (rf,))
        return self._c.fetchone()[0]

    def close(self):
        self._conn.close()


if __name__ == "__main__":
    db = idDatabase()
    db.addAnimal(1234, 1111)
    print(db.getAnimalId(1234))
    print(db.getAnimals())
