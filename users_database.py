import sqlite3
import random
import string

def get_random_email(users: list):
    letters = string.ascii_lowercase
    emails = ["gmail.com", "hotmail.com", "aol.com", "yahoo.com", "test.org"]
    email = random.choice(["test", "foo", "bar", "abc", "someone"]) + "@" + random.choice(emails)
    for user in users:
        if user[1] == email:
            return get_random_email(users)
    return email

class UsersDatabase:
    def __init__(self):
        self.connection = None
        self.db = None
        self.user = None
        try:
            self.connection = sqlite3.connect("./databases/users.db")
            self.db = self.connection.cursor()
            self.db.execute('''
                            CREATE TABLE users (
                                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                email TEXT,
                                role TEXT CHECK( role IN ('admin', 'general', 'investigator') ) NOT NULL DEFAULT 'general',
                                name TEXT,
                                password TEXT
                            );
                            ''')
            self.connection.commit()
        except sqlite3.OperationalError:
            pass
        except sqlite3.Error as e:
            print(e)
            
    def add_user(self, email: str, name: str, role: str = None):
        if role:
            self.db.execute( "INSERT INTO users (email, role, name, password) VALUES (?, ?, ?, ?);", (email, role, name, "password") )
        else:
            self.db.execute( "INSERT INTO users (email, name, password) VALUES (?, ?, ?);", (email, name, "password") )
        self.connection.commit()
        
    def get_all_users(self):
        self.db.execute("SELECT * FROM users")
        return self.db.fetchall()
        
    def get_user_from_id(self, id: int):
        self.db.execute("SELECT * FROM users WHERE user_id = ?", (id,) )
        users = self.db.fetchall()
        if len(users) == 0:
            print("User with this ID is not found.")
            return None
        else:
            return users[0]
    
    def get_email_from_id(self, id: int):
        user = self.get_user_from_id(id)
        if user:
            return user[1]
        return None
        
    def get_role_from_id(self, id: int):
        user = self.get_user_from_id(id)
        if user:
            return user[2]
        return None
    
    def change_user_email(self, id: int, email: str):
        self.db.execute("UPDATE users SET email = ? WHERE user_id = ?", (email, id) )
        self.connection.commit()
        
    def login(self, email: str, password: str):
        if (self.user):
            print("Already logged in")
        else:
            self.db.execute("SELECT * FROM users WHERE email = ?", (email,) )
            user = self.db.fetchall()[0]
            if (user and user[3] == password):
                self.user = user
            else:
                print("Cannot login with these credentials")
    
    def logout(self):
        self.user = None
        
    def get_current_user(self):
        return self.user
            
if __name__ == '__main__':
    database = UsersDatabase()
    
    users = database.get_all_users()
    database.add_user(get_random_email(users), "Jemma Simmons", "general")
    
    users = database.get_all_users()
    print("Users:")
    for user in users:
        print(user)
     