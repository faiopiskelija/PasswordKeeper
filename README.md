🔐 PWKeeper

Secure Local Password Manager (Python + PySide6)


<img width="922" height="875" alt="image" src="https://github.com/user-attachments/assets/99a4e09e-bbb6-4c5e-ae69-8996efb80177" />



PWKeeper is a lightweight and secure desktop password manager that stores your credentials locally using strong encryption.
It is built with Python, PySide6, and modern cryptographic practices.

All sensitive data stays on your device — no cloud, no network, no tracking.

✨ Features
🔑 Password Management

Master Password authentication

Add new credentials (Resource / Username / Password)

Edit existing entries

Delete entries with confirmation

View decrypted passwords only after login

🔍 Search & Organization

Quick search by resource or username

Highlights all matching rows

Scrolls to the first result automatically

🛡 Security

AES-256-GCM encryption for all stored passwords

Master Password protected with PBKDF2 (SHA-256, 200k iterations)

Unique salt for each installation

Password strength validation

Automatic re-encryption when Master Password is changed

No plaintext passwords stored anywhere

🖥 User Experience

Clean desktop interface (Qt / PySide6)

Table view with automatic decryption via proxy model

Smooth fade-in window animations

Show/Hide password option

Standalone executable support (PyInstaller)

⚙️ How It Works
First Launch

User creates a Master Password

Password strength is validated

A salt is generated

Secure hash is stored in the database

Login

Master Password is verified using PBKDF2

Encryption key is derived

Main window opens

Passwords are decrypted only in memory

Data Storage

Tables

master_password
- id
- password_hash
- salt

passwords
- id
- resource
- username
- password (AES encrypted)

Database is stored locally near the application.

🔄 Changing Master Password

When the Master Password is updated:

Old password is verified

New encryption key is generated

All stored passwords are decrypted with the old key

Re-encrypted with the new key

Application restarts automatically

🧰 Technologies

Python 3

PySide6 (Qt)

SQLite

cryptography (AES-GCM, PBKDF2)

PyInstaller

🚀 Running from Source
pip install -r requirements.txt
python main.py
📦 Build Executable (PyInstaller example)
pyinstaller --onefile --windowed main.py
🔒 Security Notes

All encryption is performed locally

No internet connection required

No cloud storage

Master Password cannot be recovered if lost

Passwords are decrypted only when displayed

🎯 Project Purpose

PWKeeper was created as a practical project demonstrating:

Secure password storage

Modern encryption techniques

Desktop development with Qt

Clean architecture (UI / DB / Crypto separation)

💡 Future Improvements

Password generator

Auto-lock after inactivity

Clipboard copy with timeout

Export / Import

Dark mode

📄 License

MIT License
