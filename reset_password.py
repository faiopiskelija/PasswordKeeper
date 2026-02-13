from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QMessageBox, QPushButton, QLineEdit
from database import check_master_password, save_master_password, reencrypt_passwords
import subprocess
import sys, os
from PySide6.QtWidgets import QMessageBox
from utils import resource_path
import time

def restart_program():
    QMessageBox.information(None, "Restart", "The program will restart to apply the new master password.")

    # если собран exe
    if getattr(sys, "frozen", False):
        exe_path = sys.executable

        # сохранить окружение + сброс
        new_env = {**os.environ, "PYINSTALLER_RESET_ENVIRONMENT": "1"}

        subprocess.Popen(
            [exe_path],
            env=new_env
        )
    else:
        # режим IDE — всё запускаем через python
        subprocess.Popen(
            [sys.executable, os.path.abspath(sys.argv[0])]
        )

    sys.exit()



def OpenResetWindow(main_window):
    loader = QUiLoader()
    ui_file = QFile(resource_path("resetMasterPassword.ui"))
    ui_file.open(QFile.ReadOnly)
    window = loader.load(ui_file, main_window)
    ui_file.close()

    change_btn = window.findChild(QPushButton, "change_masterpassworrd_btn")
    old_pw_input = window.findChild(QLineEdit, "old_password")
    new_pw_input = window.findChild(QLineEdit, "new_password")
    repeat_pw_input = window.findChild(QLineEdit, "repeat_password")

    def change():
        old_pw = old_pw_input.text().strip()
        new_pw = new_pw_input.text().strip()
        repeat_pw = repeat_pw_input.text().strip()

        # Проверки
        if not check_master_password(old_pw):
            QMessageBox.warning(window, "Error", "Incorrect old password!")
            return

        if old_pw == new_pw:
            QMessageBox.warning(window, "Error", "New password cannot be the same as old!")
            return

        if new_pw != repeat_pw:
            QMessageBox.warning(window, "Error", "New passwords do not match!")
            return

        # Генерация нового мастер-пароля и ключа
        new_master_key = save_master_password(new_pw)

        # Перешифровка всех паролей из старого ключа в новый
        reencrypt_passwords(main_window.master_key, new_master_key)

        # Обновляем мастер-ключ в MainWindow
        main_window.master_key = new_master_key

        QMessageBox.information(window, "Success", "Master password successfully changed!")
        window.close()

        restart_program()

    change_btn.clicked.connect(change)
    return window
