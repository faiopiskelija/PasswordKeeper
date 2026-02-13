from PySide6.QtCore import QIdentityProxyModel, Qt
from crypto import decrypt_pass

class DecryptProxyModel(QIdentityProxyModel):
    def __init__(self, parent=None, master_key=None):
        super().__init__(parent)
        self.master_key = master_key

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return super().data(index, role)

        # Все колонки кроме пароля выводим как есть
        if index.column() != 3:
            return super().data(index, role)

        # Колонка Password
        encrypted = super().data(index, Qt.DisplayRole)
        if not encrypted:
            return ""

        try:
            decrypted = decrypt_pass(encrypted, self.master_key)
            return decrypted
        except Exception as e:
            print(f"Decrypt error: {e} для значения {encrypted}")
            return ""
