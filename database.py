import sqlite3
from pathlib import Path
from crypto import encrypt_pass
from crypto import generate_salt, derive_key
import hashlib, base64
from crypto import derive_key, encrypt_pass, decrypt_pass
import sqlite3
import sys




# ---- DB location: <folder_with_exe>/_internal/cryptography/databasename.db ----
def app_base_dir() -> Path:
    # when frozen (PyInstaller) -> рядом с .exe
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # when running from source -> рядом с проектом (можно поменять на что тебе надо)
    return Path(__file__).resolve().parent

DB_DIR = app_base_dir() / "_internal" / "cryptography"
DB_FILE = hashlib.sha256(b"PWKeeper::dbfile::v1").hexdigest()[:16] + ".db"
DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / DB_FILE


#return connection with DB 
def get_connection():
    return sqlite3.connect(str(DB_PATH))

def init_db (): 
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""CREATE TABLE IF NOT EXISTS master_password (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   password_hash TEXT NOT NULL,
                   salt TEXT NOT NULL
                );""")

    conn.commit()
    #For passwords
    init_passwords_table()

    conn.close()
    print("Database is ready")
    
def hash_password (password: str) -> str: 
    sha = hashlib.sha256()
    sha.update(password.encode('utf-8'))
    return sha.hexdigest()

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64

ITERATIONS = 200_000  # количество итераций PBKDF2

def hash_master_password_pbkdf2(password: str, salt: str) -> str:
    salt_bytes = base64.b64decode(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=ITERATIONS
    )
    key = kdf.derive(password.encode())
    return base64.b64encode(key).decode()

def verify_master_password_pbkdf2(input_password: str, stored_hash: str, salt: str) -> bool:
    salt_bytes = base64.b64decode(salt)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=ITERATIONS
    )
    try:
        kdf.verify(input_password.encode(), base64.b64decode(stored_hash))
        return True
    except Exception:
        return False



def save_master_password(password: str) -> bytes:
    conn = get_connection()
    cur = conn.cursor()
    salt = generate_salt()

    password_hash = hash_master_password_pbkdf2(password, salt)
    cur.execute("DELETE FROM master_password;")
    
    cur.execute(
        "INSERT INTO master_password (password_hash, salt) VALUES (?, ?)",
        (password_hash, salt)
    )

    conn.commit()   # Сохраняем изменения
    conn.close()    # Закрываем соединение

    # Генерация ключа из мастер-пароля и соли
    master_key = derive_key(password, salt)
    print("Master password saved with salt.")
    return master_key
    
def reencrypt_passwords(old_master_key, new_master_key):
    import sqlite3
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, password FROM passwords")
    rows = cur.fetchall()
    
    for row_id, encrypted_pass in rows:
        try:
            # Дешифруем старым ключом
            decrypted = decrypt_pass(encrypted_pass, old_master_key)
            # Шифруем новым ключом
            re_encrypted = encrypt_pass(decrypted, new_master_key)
            # Обновляем в базе
            cur.execute("UPDATE passwords SET password=? WHERE id=?", (re_encrypted, row_id))
        except Exception as e:
            print(f"Error re-encrypting password id={row_id}: {e}")
    
    conn.commit()
    conn.close()



def check_master_password(input_password: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT password_hash, salt FROM master_password LIMIT 1;")
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    stored_hash, salt = row
    return verify_master_password_pbkdf2(input_password, stored_hash, salt)

    

def is_master_password_set():
    conn = get_connection()
    cur  = conn.cursor()
    
    cur.execute("SELECT id FROM master_password LIMIT 1;")
    row = cur.fetchone()
    conn.close()
    return row is not None

def init_passwords_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(""" CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    resource TEXT NOT NULL, 
                    username TEXT NOT NULL,
                    password TEXT NOT NULL  
                );
                
                 """)
                 
    conn.commit()
    conn.close()

def add_new_entry(resource: str, username: str, password: str, master_key: bytes):
    conn = get_connection()
    cur = conn.cursor()

    encrypted_password = encrypt_pass(password, master_key)

    cur.execute(
        "INSERT INTO passwords (resource, username, password) VALUES (?, ?, ?)",
        (resource, username, encrypted_password)
    )
    conn.commit()
    conn.close()


    
if __name__ == "__main__":
    init_db()