from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt, QItemSelectionModel
from PySide6.QtWidgets import QMessageBox, QPushButton, QLineEdit
from utils import resource_path


def AddNewSearchWindow(table_view, model=None):
    """
    Окно поиска по таблице.
    table_view: QTableView из MainWindow
    model: не используется напрямую, можно передавать None
    """
    # Загружаем UI
    loader = QUiLoader()
    ui_file = QFile(resource_path("searchForm.ui"))
    ui_file.open(QFile.ReadOnly)
    window = loader.load(ui_file, None)
    ui_file.close()

    # Находим виджеты
    search_button = window.findChild(QPushButton, "search_btn")
    search_input = window.findChild(QLineEdit, "text_to_find")

    # Берем модель прокси (DecryptProxyModel) из таблицы
    proxy_model = table_view.model()

    def do_search():
        text_to_find = search_input.text().strip().lower()
        if not text_to_find:
            QMessageBox.information(window, "Search", "Введите текст для поиска")
            return

        # Получаем selection model таблицы
        selection_model = table_view.selectionModel()
        selection_model.clearSelection()  # убираем старые выделения

        matches = []

        # Проходим по всем строкам прокси модели
        for row in range(proxy_model.rowCount()):
            resource = proxy_model.index(row, 1).data()
            username = proxy_model.index(row, 2).data()

            # Если значение None, заменяем на пустую строку
            resource = resource.lower() if resource else ""
            username = username.lower() if username else ""

            if text_to_find in resource or text_to_find in username:
                matches.append(row)

        if matches:
            # Выделяем все найденные строки
            for row in matches:
                index = proxy_model.index(row, 0)
                selection_model.select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)
            # Скроллим к первой найденной строке
            table_view.scrollTo(proxy_model.index(matches[0], 0))
        else:
            QMessageBox.information(window, "Search", "Совпадений не найдено")

    # Привязываем поиск к кнопке
    search_button.clicked.connect(do_search)

    return window
