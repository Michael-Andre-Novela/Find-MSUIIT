"""Activity log and Archives view."""

from typing import Optional, List, Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout,
                               QComboBox, QPushButton, QTextEdit, QTabWidget,
                               QTableWidget, QTableWidgetItem, QHeaderView,
                               QAbstractItemView, QLineEdit, QMessageBox)

class ActivityLogView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        # Main Title Header
        title = QLabel("System History & Archives")
        title.setObjectName("viewTitle")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # --- CREATE SUB-TABS ---
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # ==========================================
        # TAB 1: SYSTEM ACTIVITY LOGS
        # ==========================================
        self.tab_logs = QWidget()
        logs_layout = QVBoxLayout(self.tab_logs)
        logs_layout.setContentsMargins(20, 20, 20, 20)

        log_controls = QHBoxLayout()
        self.lbl_filter = QLabel("Filter by Type:")
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["All Activity", "Items Registration", "Claims Processed", "System Alerts"])

        self.btn_export = QPushButton("Export to CSV")
        self.btn_export.setObjectName("btnExport")

        self.btn_refresh_logs = QPushButton("Refresh Logs")
        self.btn_refresh_logs.setObjectName("btnSubmit")

        log_controls.addWidget(self.lbl_filter)
        log_controls.addWidget(self.combo_filter)
        log_controls.addStretch()
        log_controls.addWidget(self.btn_export)
        log_controls.addWidget(self.btn_refresh_logs)

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet("font-family: 'Courier New', monospace; font-size: 13px;")

        logs_layout.addLayout(log_controls)
        logs_layout.addWidget(self.log_display)
        self.tabs.addTab(self.tab_logs, "📜 System Activity Log")

        # ==========================================
        # TAB 2: ARCHIVED ITEMS
        # ==========================================
        self.tab_archives = QWidget()
        archives_layout = QVBoxLayout(self.tab_archives)
        archives_layout.setContentsMargins(20, 20, 20, 20)

        archive_controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search archives by name or description...")
        
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Lost", "Found"])
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        
        self.search_btn = QPushButton("Search Archives")
        self.search_btn.setObjectName("btnSubmit")
        
        self.search_btn.setFixedWidth(130)

        archive_controls.addWidget(self.search_input, 3)
        archive_controls.addWidget(self.type_filter, 1)
        archive_controls.addWidget(self.category_filter, 2)
        archive_controls.addWidget(self.search_btn)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Item ID", "Name", "Type", "Category", "Final Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        archive_actions = QHBoxLayout()
        self.selected_label = QLabel("Selected Item: None")
        self.selected_label.setStyleSheet("font-weight: bold;")
        
        self.restore_btn = QPushButton("Restore to Active List")
        self.restore_btn.setEnabled(False)
        self.restore_btn.setObjectName("btnRestore")

        archive_actions.addWidget(self.selected_label)
        archive_actions.addStretch()
        archive_actions.addWidget(self.restore_btn)

        archives_layout.addLayout(archive_controls)
        archives_layout.addWidget(self.table)
        archives_layout.addLayout(archive_actions)
        self.tabs.addTab(self.tab_archives, "📦 Historical Item Archives")

    # --- Helper Methods ---
    def show_logs(self, log_entries: List[str]) -> None:
        self.log_display.clear()
        if not log_entries:
            self.log_display.append("No log records found.")
            return
        for entry in log_entries:
            self.log_display.append(entry)

    def populate_categories(self, categories: List[Dict]):
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", None)
        for cat in categories:
            self.category_filter.addItem(cat["category_name"], cat["category_id"])

    def populate_table(self, items: List[Dict]):
        self.table.setRowCount(0)
        for row_idx, item in enumerate(items):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item["item_id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item["type"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item["category_name"] or "None"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(item["status"]))

    def get_selected_item_id(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            return int(self.table.item(selected_rows[0].row(), 0).text())
        return None

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def ask_confirmation(self, title, message):
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes
    

    def get_item_at_position(self, position):
        """Finds exactly which row the user right-clicked."""
        item = self.table.itemAt(position)
        if item:
            row = item.row()
            self.table.selectRow(row) 
            item_id = int(self.table.item(row, 0).text())
            item_name = self.table.item(row, 1).text()
            return item_id, item_name
        return None, None