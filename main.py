import sys
from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QPushButton, QTableView, QStyleFactory, QHeaderView, QLabel
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QPropertyAnimation
from PySide6.QtSql import QSqlDatabase, QSqlTableModel
from database import init_db, check_master_password, is_master_password_set, DB_PATH
from addNewEntry import AddNewEntryWindow
from searchForm import AddNewSearchWindow
from reset_password import OpenResetWindow
from anim import animation
from decrypt_proxy import DecryptProxyModel
from crypto import decrypt_pass, derive_key
from create_master_password_window import CreateMasterPasswordWindow
from utils import resource_path
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

def make_taskbar_window(w):
    # trying to make a window not just a dialog
    w.setParent(None)
    w.setWindowFlag(Qt.Window, True)

    
    w.setWindowFlag(Qt.WindowSystemMenuHint, True)
    w.setWindowFlag(Qt.WindowMinimizeButtonHint, True)
    w.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
    w.setWindowFlag(Qt.WindowCloseButtonHint, True)

    
    w.setWindowFlag(Qt.Tool, False)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        ui_file = QFile(resource_path("login.ui"))
        ui_file.open(QFile.ReadOnly)
        self.login_form = loader.load(ui_file)
        ui_file.close()



        self.login_form.setWindowTitle("Enter to Application")
        self.password = self.login_form.findChild(QWidget, "passwordInput")
        self.enter_btn = self.login_form.findChild(QWidget, "loginButton")
        
        self.enter_btn.clicked.connect(self.check_password)
        
    def check_password(self):
        user_input = self.password.text()
        if check_master_password(user_input):
            # Taking salt from DB 
            from database import get_connection
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT salt FROM master_password LIMIT 1;")
            salt = cur.fetchone()[0]
            conn.close()

            # Generating a master key for encryption/decryption
            master_key = derive_key(user_input, salt)

            # Pass master_key to MainWindow
            self.main_window = MainWindow(master_key)
            make_taskbar_window(self.main_window.main_form)   
            animation(self.main_window.main_form)
            self.login_form.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid password!")

class MainWindow(QWidget):
    def __init__(self, master_key):
        super().__init__()
        self.master_key = master_key
        loader = QUiLoader()
        ui_file = QFile(resource_path("main.ui"))
        ui_file.open(QFile.ReadOnly)
        self.main_form = loader.load(ui_file)       
        ui_file.close()

        self.main_form.setWindowTitle("PWKeeper")

        # Installing logo to main window from normal path. resource_path
        from PySide6.QtGui import QPixmap
        label_logo = self.main_form.findChild(QLabel, "label")
        pixmap = QPixmap(resource_path("logo.png"))
        label_logo.setPixmap(pixmap)


        #add button
        self.add_btn = self.main_form.findChild(QPushButton, "addButton")
        self.add_btn.clicked.connect(self.open_add_window)
        #delete button
        self.delete_btn = self.main_form.findChild(QPushButton, "delButton")
        self.delete_btn.clicked.connect(self.confirm_delete)
        #edit button
        self.edit_btn = self.main_form.findChild(QPushButton, "editButton")
        self.edit_btn.clicked.connect(self.edit_selected_row)
        #search button
        self.search_btn = self.main_form.findChild(QPushButton, "searchButton")
        self.search_btn.clicked.connect(self.search_form)
         #reset password button
        self.reset_btn = self.main_form.findChild(QPushButton, "resetMasterPassword_btn") 
        self.reset_btn.clicked.connect(self.reset_masterpassword_form)


        # --- Find QTableView ---
        self.table = self.main_form.findChild(QTableView)
        self.table.doubleClicked.connect(self.open_edit_by_double_click)
        # --- connection to DB trough Qt ---
        # Create connection type QSQLITE (SQLite)
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        # Indicate name of DB database.py (mainDB.db)
        self.db.setDatabaseName(str(DB_PATH))
        # Openning DB
        if not self.db.open():
            QMessageBox.critical(self.main_form, "Data Base Error", self.db.lastError().text())
        else: 
            # If ok -> setup table for passwords
            self.setup_model()


    def setup_model(self):
        # Configure QSqlTableModel and bind it to QTableView.
        # create a model bound to our connection self.db
        self.model = QSqlTableModel(self.main_form, self.db)
        #  tell the model which table to work with
        self.model.setTable("passwords")
        # Making a select from the Passwords table 
        self.model.select()

        # Set column headers (by index: 0=id, 1=resource, 2=password)
        self.model.setHeaderData(0, Qt.Horizontal, "№")
        self.model.setHeaderData(1, Qt.Horizontal, "Resource")
        self.model.setHeaderData(2, Qt.Horizontal, "Username")
        self.model.setHeaderData(3, Qt.Horizontal, "Password")
        # Creating a proxy model 
        self.proxy = DecryptProxyModel(self.main_form, master_key=self.master_key)
        self.proxy.setSourceModel(self.model)
        # linking the model to our QTableView
        self.table.setModel(self.proxy)
        # So that rows are selected entirely, and not by cells
        self.table.setSelectionBehavior(QTableView.SelectRows)
        # We prohibit manual editing of cells
        self.table.setEditTriggers(QTableView.NoEditTriggers)
        # Hide vertical headers (line numbers on the left)
        self.table.verticalHeader().setVisible(False)
        # Stretch the last column to nicely fill the space
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        # content stretching
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        # painting
        self.table.setAlternatingRowColors(True)


    def confirm_delete(self):
        reply = QMessageBox.question(
            self.main_form,
            "Confirmation",
            "Are you sure you want to delete?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.delete_selected_row()
 # Delete a row
    def delete_selected_row(self):
        selected = self.table.selectionModel().selectedRows()

        if not selected: 
            QMessageBox.warning(self, "Error", "Choose a row to delete")
            return
        
        proxy_index = selected[0]

        source_index = self.proxy.mapToSource(proxy_index)

        row = source_index.row()

        self.model.removeRow(row)
        self.model.submitAll()
        self.refresh_table()
        

    def edit_selected_row(self):
         # если edit уже открыт — просто вывести наверх
        if hasattr(self, "edit_window") and self.edit_window is not None and self.edit_window.isVisible():
            self.edit_window.raise_()
            self.edit_window.activateWindow()
            return
        selected = self.table.selectionModel().selectedRows()

        if not selected: 
            QMessageBox.warning(self, "Error", "Choose a row to edit")
            return
        proxy_index = selected[0]
        source_index = self.proxy.mapToSource(proxy_index)
        row = source_index.row()

    # We take data through a proxy (it decrypts the password automatically)
        resource = self.proxy.data(self.proxy.index(proxy_index.row(), 1))
        username = self.proxy.data(self.proxy.index(proxy_index.row(), 2))
        password_decrypted = self.proxy.data(self.proxy.index(proxy_index.row(), 3))


        #  editing window
        self.edit_window = AddNewEntryWindow(
            resource=resource, 
            username=username, 
            password=password_decrypted,
            row=row, 
            model=self.model,
            master_key=self.master_key
        )
        self.edit_window.setParent(self)
        self.edit_window.setWindowFlag(Qt.Window)

        label = self.edit_window.findChild(QLabel, "label_top_window")
        edit_button = self.edit_window.findChild(QPushButton, "saveButton")
        edit_button.setText("Save")
        label.setText("Edit row")
        self.edit_window.destroyed.connect(lambda: setattr(self, "edit_window", None))
        self.edit_window.destroyed.connect(self.refresh_table)
        animation(self.edit_window)

        
    def open_add_window(self):
        # if the window already exists and is open, just bring it to the top
        if hasattr(self, "add_window") and self.add_window is not None and self.add_window.isVisible():
            self.add_window.raise_()
            self.add_window.activateWindow()
            return
        # otherwise we create a new window
        self.add_window = AddNewEntryWindow(master_key=self.master_key)
        self.add_window.setParent(self)
        self.add_window.setWindowFlag(Qt.Window)
        self.add_window.destroyed.connect(self.refresh_table)

        # so that the link is cleared after closing
        self.add_window.destroyed.connect(lambda: setattr(self, "add_window", None))

        animation(self.add_window)

    def refresh_table(self):
        if hasattr(self, "model"):
            self.model.select()
            
    def search_form(self):
        if hasattr(self, "search_window") and self.search_window is not None and self.search_window.isVisible():
            self.search_window.raise_()
            self.search_window.activateWindow()
            return
        self.search_window = AddNewSearchWindow(self.table, self.model)
        self.search_window.setParent(self)
        self.search_window.setWindowFlag(Qt.Window)

        self.search_window.destroyed.connect(lambda: setattr(self, "search_window", None))

        animation(self.search_window)

    def reset_masterpassword_form(self):
        if hasattr(self, "reset_window") and self.reset_window is not None and self.reset_window.isVisible():
            self.reset_window.raise_()
            self.reset_window.activateWindow()
            return

        self.reset_window = OpenResetWindow(self)
        self.reset_window.destroyed.connect(lambda: setattr(self, "reset_window", None))
        animation(self.reset_window)
        
    def open_edit_by_double_click(self, index):
        # index приходит из proxy модели
        if not index.isValid():
           return
     # если окно уже открыто — просто поднять
        if hasattr(self, "edit_window") and self.edit_window is not None and self.edit_window.isVisible():
            self.edit_window.raise_()
            self.edit_window.activateWindow()
            return
            #строка в proxy
        proxy_row = index.row()

        # данные через proxy (уже расшифрованные)
        resource = self.proxy.data(self.proxy.index(proxy_row, 1))
        username = self.proxy.data(self.proxy.index(proxy_row, 2))
        password_decrypted = self.proxy.data(self.proxy.index(proxy_row, 3))

        # переводим индекс в source (для редактирования)
        source_index = self.proxy.mapToSource(self.proxy.index(proxy_row, 0))
        row = source_index.row()

    # открываем окно редактирования
        self.edit_window = AddNewEntryWindow(
            resource=resource,
            username=username,
            password=password_decrypted,
            row=row,
            model=self.model,
            master_key=self.master_key
        )

        self.edit_window.setParent(self)
        self.edit_window.setWindowFlag(Qt.Window)

        label = self.edit_window.findChild(QLabel, "label_top_window")
        edit_button = self.edit_window.findChild(QPushButton, "saveButton")
        edit_button.setText("Save")
        label.setText("Edit entry")

        self.edit_window.destroyed.connect(lambda: setattr(self, "edit_window", None))
        self.edit_window.destroyed.connect(self.refresh_table)

        animation(self.edit_window)

def main():
    init_db()
    print("DB:", DB_PATH)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(resource_path("logo.png")))

    if is_master_password_set():
        window = LoginWindow()
        make_taskbar_window(window.login_form)
        animation(window.login_form)
    else: 
        window = CreateMasterPasswordWindow()
        make_taskbar_window(window.form)
        animation(window.form)
    sys.exit(app.exec())        
if __name__ == "__main__":
    main()