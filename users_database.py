import sqlite3
import random
import string

def get_random_email():
    letters = string.ascii_lowercase
    emails = ["gmail.com", "hotmail.com", "aol.com", "yahoo.com", "test.org"]
    email = (''.join((random.choice(letters)) for i in range(random.randint(10, 20)))) + "@" + random.choice(emails)
    return email
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
            self.db.execute( "INSERT INTO users (email, role) VALUES (?, ?);", (email, role) )
        else:
            self.db.execute( "INSERT INTO users (email) VALUES (?);", (email,) )
        self.connection.commit()
        
    def get_all_users(self):
        self.db.execute("SELECT * FROM users")
        return self.db.fetchall()
        
    def get_user_from_id(self, id: int):
        self.db.execute("SELECT * FROM users WHERE user_id = ?", (id,) )
        return self.db.fetchall()[0]
    
    def get_email_from_id(self, id: int):
        user = self.get_user_from_id(id)
        return user[1]
        
    def get_role_from_id(self, id: int):
        user = self.get_user_from_id(id)
        return user[2]
    
    def change_user_email(self, id: int, email: str):
        self.db.execute("UPDATE users SET email = ? WHERE user_id = ?", (email, id) )
        self.connection.commit()
            
if __name__ == '__main__':
    database = UsersDatabase()
    
    users = database.get_all_users()
    print("Users:")
    for user in users:
        print(user)
    
    print("\nGetting roles from method in class:")
    for user in users:
        user_id = user[0]
        print("User with id", user_id, "has role:", database.get_role_from_id(user_id))
        
    print("\nChange random user's email:")
    user = random.choice(users)
    user_id = user[0]
    database.change_user_email(user_id, get_random_email())
    print("Old user:", user)
    print("New user:", database.get_user_from_id(user_id))
    
    