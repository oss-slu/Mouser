'''Functions to create, manage, encrypt, and save temporary files for the Mouser app.'''

import tempfile
import os
import sys
from shared.password_utils import PasswordManager


TEMP_FOLDER_NAME = "Mouser"


def create_temp_copy(filepath: str):
    '''Create a temporary copy of the given file and return the temp file path.'''
    filepath = os.path.abspath(filepath)

    temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
    os.makedirs(temp_folder_path, exist_ok=True)

    temp_file_name = os.path.basename(filepath)
    temp_file_path = os.path.join(temp_folder_path, temp_file_name)

    with open(filepath, 'rb') as file:
        data = file.read()

    with open(temp_file_path, 'wb') as file:
        file.write(data)
        file.seek(0)

    return temp_file_path


def create_temp_from_encrypted(filepath: str, password: str):
    '''Create a temporary decrypted copy of an encrypted file.'''
    filepath = os.path.abspath(filepath)

    print(filepath)  # Debug print left intentionally

    temp_folder_path = os.path.join(tempfile.gettempdir(), TEMP_FOLDER_NAME)
    os.makedirs(temp_folder_path, exist_ok=True)

    temp_file_name = os.path.basename(filepath)
    temp_file_path = os.path.join(temp_folder_path, temp_file_name)

    manager = PasswordManager(password)
    data = manager.decrypt_file(filepath)

    with open(temp_file_path, 'wb') as file:
        file.write(data)
        file.seek(0)

    return temp_file_path


def save_temp_to_file(temp_file_path: str, permanent_file_path: str):
    '''
    Save data from a temporary file to a permanent file.

    The filename is normalized so only the base name before any underscore is used.
    '''
    temp_file_path = os.path.abspath(temp_file_path)
    permanent_file_path = os.path.abspath(permanent_file_path)

    base, ext = os.path.splitext(permanent_file_path)
    base = base.split('_')[0]
    permanent_file_path = f"{base}{ext}"

    with open(temp_file_path, 'rb') as temp_file:
        data = temp_file.read()

    with open(permanent_file_path, 'wb') as file:
        file.write(data)


def save_temp_to_encrypted(temp_file_path: str, permanent_file_path: str, password: str):
    '''Save data from a temporary file into an encrypted permanent file.'''
    temp_file_path = os.path.abspath(temp_file_path)
    permanent_file_path = os.path.abspath(permanent_file_path)

    base, ext = os.path.splitext(permanent_file_path)
    base = base.split('_')[0]
    permanent_file_path = f"{base}{ext}"

    manager = PasswordManager(password)
    manager.encrypt_file(temp_file_path)

    with open(temp_file_path, 'rb') as encrypted:
        data = encrypted.read()

    with open(permanent_file_path, 'wb') as file:
        file.write(data)


def get_resource_path(relative_path: str):
    '''
    Get the absolute path to a resource.

    Works both during development and in PyInstaller executables.
    '''
    try:
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller extracts bundled files here
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.abspath(relative_path)
    except Exception as e:  # pylint: disable=broad-except
        print(f"Error accessing resource: {relative_path}")
        raise e


SUCCESS_SOUND = get_resource_path("shared/sounds/rfid_success.wav")
ERROR_SOUND = get_resource_path("shared/sounds/error.wav")
