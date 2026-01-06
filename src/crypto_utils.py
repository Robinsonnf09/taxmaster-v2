from cryptography.fernet import Fernet
import os
from pathlib import Path

class CryptoUtils:
    def __init__(self):
        key_file = Path("config/.secret.key")
        if key_file.exists():
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        return self.cipher.decrypt(encrypted_data.encode()).decode()

crypto = CryptoUtils()
