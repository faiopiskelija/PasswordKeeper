from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

#For random bites
import os
import base64

def encrypt_pass(plain_password: str, key: bytes) -> str:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plain_password.encode(), None)
    return base64.b64encode(nonce + ciphertext).decode("ascii")

def derive_key(master_password: str, salt: str) -> bytes:
    salt_bytes = base64.b64decode(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,   # AES-256
        salt=salt_bytes,
        iterations=100_000,
    )
    return kdf.derive(master_password.encode())


def decrypt_pass(encoded: str, key: bytes) -> str:
    data = base64.b64decode(encoded)
    nonce = data[:12]
    ciphertext = data[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")

def generate_salt() -> str:
    return base64.b64encode(os.urandom(16)).decode()
