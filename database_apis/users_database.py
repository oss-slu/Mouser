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
            self.db.execute('''
                            CREATE TABLE auto_login(
                                mac_address TEXT,
                                date TEXT
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
    
    def get_all_users_dict(self):
        users = self.get_all_users()
        all_user_dict = {}
        for user in users:
            new_dict = {}
            new_dict["id"] = user[0]
            new_dict["email"] = user[1]
            new_dict["role"] = user[2]
            new_dict["name"] = user[3]
            new_dict["password"] = user[4]
            all_user_dict[user[1]] = new_dict
        return all_user_dict
        
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
        
    def change_user_role(self, id: int, role: str):
        self.db.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, id) )
        self.connection.commit()
        
    def change_user_name(self, id: int, name: str):
        self.db.execute("UPDATE users SET name = ? WHERE user_id = ?", (name, id) )
        self.connection.commit()
        
    def change_user_password(self, id: int, password: str):
        self.db.execute("UPDATE users SET password = ? WHERE user_id = ?", (password, id) )
        self.connection.commit()
        
    def login(self, email: str, password: str):
        if (self.user):
            print("Already logged in")
        else:
            self.db.execute("SELECT * FROM users WHERE email = ?", (email,) )
            user_list = self.db.fetchall()
            if (len(user_list) > 0):
                user = user_list[0]
            else:
                user = None
            if (user and user[4] == password):
                self.user = user
                return True
            else:
                print("Cannot login with these credentials")
        return False
    
    def logout(self):
        self.user = None
        
    def get_current_user(self):
        return self.user
    
    def add_auto_login_information(self, mac_address : str):
        self.db.execute( "INSERT INTO auto_login (mac_address, date) VALUES (?, datetime('now', '+7 day'));", (mac_address) )

    def auto_login(self, mac_address : str):
        self.db.execute("SELECT * FROM auto_login WHERE mac_address = ?", (mac_address) )
        address_list = self.db.fetchall()
        if (len(address_list) > 0):
            address = address_list[0]
        else:
            address = None
        if (address[0] == mac_address):
            return True
        return False
    
    def remove_auto_login_credentials(self):
        self.db.execute("DELETE FROM auto_login WHERE date < datetime('now')")
        self.connection.commit()

    # for testing purpose
    def auto_login_remove_all(self):
        self.db.execute("DELETE FROM auto_login")
        self.connection.commit()

    


            
if __name__ == '__main__':
    database = UsersDatabase()
    
    users = database.get_all_users()
    print("Users:")
    for user in users:
        print(user)

     
