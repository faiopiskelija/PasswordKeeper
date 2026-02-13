from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QMessageBox, QPushButton, QLineEdit
from database import add_new_entry
from crypto import encrypt_pass
from utils import resource_path


def AddNewEntryWindow(resource=None, username=None, password=None, row=None, model=None, master_key=None):
    loader = QUiLoader()
    ui_file = QFile(resource_path("addentryform.ui"))
    ui_file.open(QFile.ReadOnly)
    window = loader.load(ui_file, None) 
    ui_file.close()

    if window is None:
        QMessageBox.critical(None, "Error", "Failed to load addentryform.ui")
        return

    # find fields
    name_input = window.findChild(QLineEdit, "resource_name")
    username_input = window.findChild(QLineEdit, "username")
    password_input = window.findChild(QLineEdit, "resource_password")
    save_button = window.findChild(QPushButton, "saveButton")

    # fill in if editing
    if resource is not None:
        name_input.setText(resource)
        username_input.setText(username)
        password_input.setText(password)

    def save():
        name = name_input.text().strip()
        user = username_input.text().strip()
        passwd = password_input.text().strip()

        if not name or not user or not passwd:
            QMessageBox.warning(window, "Error", "Please fill in all fields!")
            return

        encrypted_password = encrypt_pass(passwd, master_key)

        if model is not None and row is not None:
            model.setData(model.index(row, 1), name)
            model.setData(model.index(row, 2), user)
            model.setData(model.index(row, 3), encrypted_password)
            model.submitAll()
            QMessageBox.information(window, "Updated", "Details updated successfully.")
        else:
            add_new_entry(name, user, passwd, master_key)
            QMessageBox.information(window, "Saved", "Information saved successfully.")
            parent = window.parent()
            if parent and hasattr(parent, "refresh_table"):
                parent.refresh_table()

        window.close()

    save_button.clicked.connect(save)
    return window
