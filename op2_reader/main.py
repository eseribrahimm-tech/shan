import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QComboBox, QSpinBox,
                             QTableWidget, QTableWidgetItem, QTabWidget, QLineEdit,
                             QMessageBox, QSplitter, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from op2_handler import Op2Handler


class LoadingThread(QThread):
    """Op2 dosyasını arka planda yüklemek için thread"""
    finished = pyqtSignal(bool, str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.op2_handler = None

    def run(self):
        try:
            self.op2_handler = Op2Handler(self.file_path)
            self.finished.emit(True, "Dosya başarıyla yüklendi")
        except Exception as e:
            self.finished.emit(False, str(e))


class Op2ReaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.op2_handler = None
        self.current_subcase = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("MSC Nastran Op2 Reader")
        self.setGeometry(100, 100, 1400, 900)

        # Ana widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()

        # Üst panel - Dosya seçimi ve kontroller
        top_panel = self.create_top_panel()
        main_layout.addLayout(top_panel)

        # Ortam bölümü - Loadcase ve sonuçlar
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.addWidget(self.create_left_panel())
        content_splitter.addWidget(self.create_right_panel())
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 2)
        main_layout.addWidget(content_splitter)

        main_widget.setLayout(main_layout)

    def create_top_panel(self):
        layout = QHBoxLayout()

        # Dosya seçme
        self.btn_open = QPushButton("Dosya Aç")
        self.btn_open.clicked.connect(self.open_file)
        layout.addWidget(self.btn_open)

        self.lbl_file = QLabel("Dosya seçilmedi")
        self.lbl_file.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        layout.addWidget(self.lbl_file)

        layout.addStretch()
        return layout

    def create_left_panel(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Loadcase seçimi
        lbl_loadcase = QLabel("Loadcase Seç:")
        lbl_loadcase.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(lbl_loadcase)

        self.combo_loadcase = QComboBox()
        self.combo_loadcase.currentIndexChanged.connect(self.on_loadcase_changed)
        layout.addWidget(self.combo_loadcase)

        # Result type seçimi
        lbl_result = QLabel("Result Type:")
        lbl_result.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(lbl_result)

        self.list_results = QListWidget()
        self.list_results.itemClicked.connect(self.on_result_type_selected)
        layout.addWidget(self.list_results)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_right_panel(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Node/Element seçimi
        filter_layout = QHBoxLayout()

        lbl_type = QLabel("Tür:")
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Node ID", "Element ID"])
        filter_layout.addWidget(lbl_type)
        filter_layout.addWidget(self.combo_type)

        lbl_id = QLabel("ID:")
        self.spin_id = QSpinBox()
        self.spin_id.setMinimum(1)
        self.spin_id.setMaximum(999999)
        filter_layout.addWidget(lbl_id)
        filter_layout.addWidget(self.spin_id)

        self.btn_search = QPushButton("Ara")
        self.btn_search.clicked.connect(self.search_results)
        filter_layout.addWidget(self.btn_search)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Sonuçlar tabı
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        widget.setLayout(layout)
        return widget

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Op2 Dosyası Seç", "", "Op2 Files (*.op2);;All Files (*)"
        )

        if file_path:
            self.lbl_file.setText(file_path)
            self.load_file(file_path)

    def load_file(self, file_path):
        self.thread = LoadingThread(file_path)
        self.thread.finished.connect(self.on_file_loaded)
        self.thread.start()

    def on_file_loaded(self, success, message):
        if success:
            self.op2_handler = self.thread.op2_handler
            self.populate_loadcases()
            QMessageBox.information(self, "Başarı", message)
        else:
            QMessageBox.critical(self, "Hata", f"Dosya yüklenirken hata: {message}")

    def populate_loadcases(self):
        self.combo_loadcase.clear()
        if self.op2_handler:
            loadcases = self.op2_handler.get_loadcases()
            for subcase_id, description in sorted(loadcases.items()):
                self.combo_loadcase.addItem(description, subcase_id)

    def on_loadcase_changed(self):
        self.list_results.clear()
        self.tab_widget.clear()

        if self.combo_loadcase.currentIndex() >= 0:
            self.current_subcase = self.combo_loadcase.currentData()
            result_types = self.op2_handler.get_result_types(self.current_subcase)

            for result_type in result_types:
                item = QListWidgetItem(result_type.capitalize())
                item.setData(Qt.UserRole, result_type)
                self.list_results.addItem(item)

    def on_result_type_selected(self, item):
        result_type = item.data(Qt.UserRole)
        self.populate_results(result_type)

    def populate_results(self, result_type):
        # Tüm sonuçları göster
        if not self.op2_handler or not self.current_subcase:
            return

        obj = self.op2_handler.result_types[self.current_subcase].get(result_type)
        if not obj:
            return

        # Yeni tab oluştur
        tab = QWidget()
        layout = QVBoxLayout()

        # Tablo oluştur
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["ID Type", "ID", "Value"])

        row = 0

        # Node sonuçlarını göster
        if hasattr(obj, 'node_gridtype'):
            node_ids = obj.node_gridtype[:, 0].astype(int)
            for idx, node_id in enumerate(node_ids[:100]):  # İlk 100 göster
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem("Node"))
                table.setItem(row, 1, QTableWidgetItem(str(node_id)))

                # Data değerini göster
                if hasattr(obj, 'data'):
                    data_str = str(obj.data[idx][:3]) if len(obj.data[idx]) > 0 else "N/A"
                    table.setItem(row, 2, QTableWidgetItem(data_str))
                row += 1

        # Element sonuçlarını göster
        if hasattr(obj, 'element_node'):
            element_ids = obj.element_node[:, 0].astype(int)
            for idx, element_id in enumerate(element_ids[:100]):  # İlk 100 göster
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem("Element"))
                table.setItem(row, 1, QTableWidgetItem(str(element_id)))

                if hasattr(obj, 'data'):
                    data_str = str(obj.data[idx][:3]) if len(obj.data[idx]) > 0 else "N/A"
                    table.setItem(row, 2, QTableWidgetItem(data_str))
                row += 1

        table.resizeColumnsToContents()
        layout.addWidget(table)

        tab.setLayout(layout)
        self.tab_widget.addTab(tab, result_type.capitalize())

    def search_results(self):
        if not self.op2_handler or not self.current_subcase:
            QMessageBox.warning(self, "Uyarı", "Lütfen önce bir dosya yükleyip loadcase seçin")
            return

        search_id = self.spin_id.value()
        search_type = self.combo_type.currentText()
        result_types = self.op2_handler.get_result_types(self.current_subcase)

        # Yeni tab oluştur
        tab = QWidget()
        layout = QVBoxLayout()

        found = False

        for result_type in result_types:
            if search_type == "Node ID":
                results = self.op2_handler.get_node_results(
                    self.current_subcase, search_id, result_type
                )
            else:
                results = self.op2_handler.get_element_results(
                    self.current_subcase, search_id, result_type
                )

            if results and 'error' not in results:
                found = True

                # Altbaşlık
                subheader = QLabel(f"{result_type.upper()} Sonuçları")
                subheader.setFont(QFont("Arial", 10, QFont.Bold))
                layout.addWidget(subheader)

                # Tablo
                table = QTableWidget()
                table.setColumnCount(2)
                table.setHorizontalHeaderLabels(["Parametre", "Değer"])

                row = 0
                for key, value in results.items():
                    table.insertRow(row)
                    table.setItem(row, 0, QTableWidgetItem(str(key)))
                    table.setItem(row, 1, QTableWidgetItem(str(value)))
                    row += 1

                table.resizeColumnsToContents()
                layout.addWidget(table)
                layout.addSpacing(10)

        if not found:
            layout.addWidget(QLabel(f"{search_type} {search_id} için sonuç bulunamadı"))

        layout.addStretch()
        tab.setLayout(layout)

        # Tab'ı ekle
        tab_name = f"{search_type} {search_id}"
        self.tab_widget.addTab(tab, tab_name)
        self.tab_widget.setCurrentWidget(tab)


def main():
    app = QApplication(sys.argv)
    window = Op2ReaderApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
