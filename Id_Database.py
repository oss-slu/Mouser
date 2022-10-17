import sqlite3

class Id_Database:
    def __init__(self):
        self._conn = sqlite3.connect(':memory:') #can input file name instead of memory, need to add that functionality later.
        self._c = self._conn.cursor()
        try:
            self._c.execute('''CREATE TABLE conversion (
                                rfid TEXT UNIQUE,
                                animal_id TEXT UNIQUE
                                );''')
            self._conn.commit()
        except:
            pass
 
    def add_animal(self, rf, an):          #problem - can add animals with same rfid and/or animalid
        self._c.execute("INSERT INTO conversion VALUES (?, ?)", (rf, an)) #automatically generate animals id 1001+
        self._conn.commit()

    def get_all_animals(self):
        self._c.execute("SELECT * FROM conversion")
        return self._c.fetchall()

    def get_animal_id(self, rf):
        self._c.execute("SELECT animal_id FROM conversion WHERE rfid=?", (rf,))
        return self._c.fetchone()[0]

    def close(self):
        self._conn.close()


if __name__ == "__main__":
    db = Id_Database()
    db.add_animal(1234, 1111)
    print(db.get_animal_id(1234))
    print(db.get_all_animals())
