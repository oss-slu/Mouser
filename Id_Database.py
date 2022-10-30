import sqlite3

class Id_Database:
    def __init__(self, file=":memory:"):
        self._conn = sqlite3.connect(file) #can input file name instead of memory, need to add that functionality later.
        self._c = self._conn.cursor()
        try:
            self._c.execute('''CREATE TABLE conversion (
                                rfid TEXT NOT NULL UNIQUE,
                                animal_id TEXT NOT NULL UNIQUE
                                );''')
            self._conn.commit()
        except:
            pass
 
    def add_animal(self, rf):          #problem - can add animals with same rfid and/or animalid
        an = self.get_next_animal_id()
        self._c.execute("INSERT INTO conversion VALUES (?, ?)", (rf, an))
        self._conn.commit()

    def get_all_animals(self):
        self._c.execute("SELECT * FROM conversion")
        return self._c.fetchall()

    def get_animal_id(self, rf):
        self._c.execute("SELECT animal_id FROM conversion WHERE rfid=?", (rf,))
        return self._c.fetchone()[0]

    def close(self):
        self._conn.close()


    def get_next_animal_id(self):
        self._c.execute("SELECT animal_id FROM conversion")
        ids = self._c.fetchall()
        num = 0
        for i in ids:
            if (int(i[0]) > num):
                num = int(i[0])
        return str(num+1)



if __name__ == "__main__":
    db = Id_Database("convert.db")
    db.add_animal('1234')
    db.add_animal('4562')
    db.add_animal('4682')
    db.add_animal('5782')
    print(db.get_animal_id('1234'))
    print(db.get_all_animals())
