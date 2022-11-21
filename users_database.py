import sqlite3
import random
import string

class UsersDatabase:
    def __init__(self):
        self.connection = None
        self.db = None
        try:
            self.connection = sqlite3.connect("./databases/users.db")
            self.db = self.connection.cursor()
            self.db.execute('''
                            CREATE TABLE users (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                email TEXT,
                                role TEXT CHECK( role IN ('admin', 'general', 'investigator') ) NOT NULL DEFAULT 'general'
                            );
                            ''')
            self.connection.commit()
        except sqlite3.OperationalError:
            pass
        except sqlite3.Error as e:
            print(e)
            
    def add_user(self, email: str, role: str = None):
        if role:
            self.db.execute('''
                            INSERT INTO users (email, role) VALUES (?, ?);
                            ''', (email, role))
        else:
            self.db.execute('''
                            INSERT INTO users (email) VALUES (?);
                            ''', (email,))
        self.connection.commit()
            
if __name__ == '__main__':
    database = UsersDatabase()
    letters = string.ascii_lowercase
    emails = ["gmail.com", "hotmail.com", "aol.com", "yahoo.com", "test.org"]
    email = (''.join((random.choice(letters)) for i in range(random.randint(10, 20)))) + "@" + random.choice(emails)
    database.add_user(email)
    
    