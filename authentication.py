logins = {
    "test@gmail.com": "password",
    "foo@bar.com": "foobar",
    "":""
}

current_user = None


def login(email: str, password: str):
    if (email in logins.keys()) and (logins[email] == password):
        current_user = email
        return True
    return False


def logout():
    current_user = None


def get_current_user():
    return current_user
