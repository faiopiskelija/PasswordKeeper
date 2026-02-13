<div align="center">

# 🔐 PWKeeper  
### Secure Local Password Manager

Python • PySide6 • AES-256 • SQLite

<img src="https://github.com/user-attachments/assets/99a4e09e-bbb6-4c5e-ae69-8996efb80177" width="600"/>

</div>

---

## 📌 About

**PWKeeper** is a lightweight and secure desktop password manager that stores your credentials locally using strong encryption.

The application is built with **Python** and **PySide6** and follows modern security practices.

✔ All data stays on your device  
✔ No cloud  
✔ No network  
✔ No tracking  

---

## ✨ Features

### 🔑 Password Management
- Master Password authentication  
- Add new credentials (Resource / Username / Password)  
- Edit existing entries  
- Delete entries with confirmation  
- View decrypted passwords only after login  

### 🔍 Search & Organization
- Quick search by resource or username  
- Highlights all matching rows  
- Automatically scrolls to the first result  

### 🛡 Security
- AES-256-GCM encryption for all stored passwords  
- Master Password protected with **PBKDF2 (SHA-256, 200k iterations)**  
- Unique salt for each installation  
- Password strength validation  
- Automatic re-encryption when Master Password is changed  
- No plaintext passwords stored anywhere  

### 🖥 User Experience
- Clean desktop interface (Qt / PySide6)  
- Table view with automatic decryption via proxy model  
- Smooth fade-in window animations  
- Show / Hide password option  
- Standalone executable support (PyInstaller)  

---

## ⚙️ How It Works

### First Launch
1. User creates a Master Password  
2. Password strength is validated  
3. A unique salt is generated  
4. Secure hash is stored in the database  

### Login Process
1. Master Password is verified using PBKDF2  
2. Encryption key is derived  
3. Main window opens  
4. Passwords are decrypted **only in memory**

---

## 🗄 Data Storage

Database tables:

```
master_password
- id
- password_hash
- salt

passwords
- id
- resource
- username
- password (AES encrypted)
```

The database is stored locally near the application.

---

## 🔄 Changing Master Password

When the Master Password is updated:

1. Old password is verified  
2. New encryption key is generated  
3. All stored passwords are decrypted with the old key  
4. Re-encrypted with the new key  
5. Application restarts automatically  

---

## 🧰 Technologies

- Python 3  
- PySide6 (Qt)  
- SQLite  
- cryptography (AES-GCM, PBKDF2)  
- PyInstaller  


---

## 📦 Build Executable

```bash
pyinstaller --onefile --windowed main.py
```

---

## 🔒 Security Notes

- All encryption is performed locally  
- No internet connection required  
- No cloud storage  
- Master Password **cannot be recovered** if lost  
- Passwords are decrypted only when displayed  

---

## 🎯 Project Purpose

PWKeeper was created as a practical project to demonstrate:

- Secure password storage  
- Modern encryption techniques  
- Desktop application development with Qt  
- Clean architecture (UI / Database / Crypto separation)  

---

## 💡 Future Improvements

- Password generator  
- Auto-lock after inactivity  
- Clipboard copy with timeout  
- Export / Import  
- Dark mode  

---

## 📄 License

MIT License
