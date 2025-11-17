'''Password Utilities'''
import base64

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class PasswordManager:
    '''Manages encrypted files with passwords.'''
    def __init__(self, password):
        self.salt = b'\xc5\xd2\x1c\x85#\xa5\x95\xa1\t\xd4\x98\x1e\x154`\xd4'
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=390000
        )
        self.key = base64.urlsafe_b64encode(self.kdf.derive(password.encode()))
        self.fernet = Fernet(self.key)

    def encrypt_file(self,file_path):
        '''Encrypts passed file.'''
        with open(file_path, "rb") as dbfile:
            original_data = dbfile.read()

        self.encrypted_data = self.fernet.encrypt(original_data)

        with open(file_path, "wb") as dbfile:
            dbfile.write(self.encrypted_data)

    def decrypt_file(self, file_path):
        '''returns the decrypted data of the passed file.'''
        try:
            with open(file_path, "rb") as file:
                encrypted_data = file.read()
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data

        except Exception as e: # pylint: disable= broad-exception-caught
            print(e)
            return False
