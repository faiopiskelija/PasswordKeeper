from PySide6.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from database import save_master_password
from anim import animation
import re
from utils import resource_path


def is_strong_password(pw: str) -> bool:
    # Минимум 8 символов
    if len(pw) < 8:
        return False
    # Минимум одна цифра
    if not re.search(r"\d", pw):
        return False
    # Минимум одна заглавная буква
    if not re.search(r"[A-Z]", pw):
        return False
    # Минимум одна строчная буква
    if not re.search(r"[a-z]", pw):
        return False
    # Минимум один спецсимвол
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", pw):
        return False
    return True


class CreateMasterPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile(resource_path("create_master_password.ui"))
        ui_file.open(QFile.ReadOnly)
        self.form = loader.load(ui_file, self)
        ui_file.close()

        self.password_input = self.form.findChild(QLineEdit, "new_password")
        self.repeat_input = self.form.findChild(QLineEdit, "repeat_password")
        self.create_btn = self.form.findChild(QPushButton, "create_master_password")
        
        self.toggle_btn = self.form.findChild(QPushButton, "toggle_password_btn")

        # Скрытый ввод по умолчанию (точки)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.repeat_input.setEchoMode(QLineEdit.Password)

        # Подключаем кнопку Show/Hide (если кнопка реально есть в .ui)
        if self.toggle_btn is not None:
            self.toggle_btn.setCheckable(True)
            self.toggle_btn.setChecked(False)
            self.toggle_btn.setText("Show")
            self.toggle_btn.toggled.connect(self.toggle_password_visibility)
        

        # Подключаем кнопку и сигнал изменения текста
        self.create_btn.clicked.connect(self.create_master_password)
        self.password_input.textChanged.connect(self.check_password_strength)

    def check_password_strength(self):
        pw = self.password_input.text()
        if not pw:
            self.password_input.setStyleSheet("")
            return
        if is_strong_password(pw):
            color = "green"
        else:
            if len(pw) < 8:
                color = "red"
            else:
                color = "orange"

        self.password_input.setStyleSheet(f"border: 2px solid {color};")

    def create_master_password(self):
        pw = self.password_input.text().strip()
        pw_repeat = self.repeat_input.text().strip()
        if not pw or not pw_repeat:
            QMessageBox.warning(self, "Error", "Введите пароль")
            return
        if pw != pw_repeat:
            QMessageBox.warning(self, "Error", "Пароли не совпадают")
            return
        if not is_strong_password(pw):
            QMessageBox.warning(
                self, "Error",
                "Пароль слишком простой. Используйте минимум 8 символов, "
                "с заглавными и строчными буквами, цифрами и спецсимволами."
            )
            return

        save_master_password(pw)
        self.close()
        QMessageBox.information(self, "OK", "Master Password created")
        self.form.close()
        

        # После создания мастер-пароля можно сразу открыть LoginWindow
        from main import LoginWindow
        self.login_window = LoginWindow()
        animation(self.login_window.login_form)
        
    def toggle_password_visibility(self, checked: bool):
        if checked:
            mode = QLineEdit.Normal
            self.toggle_btn.setText("Hide")
        else:
            mode = QLineEdit.Password
            self.toggle_btn.setText("Show")

        self.password_input.setEchoMode(mode)
        self.repeat_input.setEchoMode(mode)
