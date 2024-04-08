'''Contains functions to create and save from temporary files.'''
import tempfile
import os
from shared.password_utils import PasswordManager


TEMP_FOLDER_NAME = "Mouser"

def create_temp_copy(filepath:str):
    '''Creates a new temporary file and returns the file path of the temporary file.'''

    temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
    os.makedirs(temp_folder_path, exist_ok=True)
    temp_file_name =  os.path.basename(filepath)
    temp_file_path = os.path.join(temp_folder_path, temp_file_name)

    with open(filepath, 'rb') as file:
        data = file.read()

    with open(temp_file_path, 'wb') as file:
        file.write(data)
        file.seek(0)

    return temp_file_path

def create_temp_from_encrypted(filepath:str, password:str):
    '''Creates a new decrypted copy of a file.'''

    print(filepath)
    temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
    os.makedirs(temp_folder_path, exist_ok=True)
    temp_file_name =  os.path.basename(filepath)
    temp_file_path = os.path.join(temp_folder_path, temp_file_name)

    manager = PasswordManager(password)

    data = manager.decrypt_file(filepath)

    with open(temp_file_path, 'wb') as file:
        file.write(data)
        file.seek(0)

    return temp_file_path


def save_temp_to_file(temp_file_path: str, permanent_file_path: str):
    '''Save data from temporary file to a permanent file'''

    with open(temp_file_path, 'rb') as temp_file:
        data = temp_file.read()

    with open(permanent_file_path, 'wb') as file:
        file.write(data)

def save_temp_to_encrypted(temp_file_path: str, permanent_file_path: str, password:str):
    '''Save data from temporary file to an encrypted file.'''
    manager = PasswordManager(password)

    manager.encrypt_file(temp_file_path)
    with open(temp_file_path, 'rb') as encrypted:
        data = encrypted.read()
    
    with open(permanent_file_path, 'wb') as file:
        file.write(data)
