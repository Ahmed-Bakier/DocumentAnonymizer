from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def get_cipher(key: bytes) -> Fernet:
    return Fernet(key)

def encrypt_data(data: str, key: bytes) -> bytes:
    cipher = get_cipher(key)
    return cipher.encrypt(data.encode("utf-8"))

def decrypt_data(token: bytes, key: bytes) -> str:
    cipher = get_cipher(key)
    return cipher.decrypt(token).decode("utf-8")
