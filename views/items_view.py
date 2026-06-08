"""Items management view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
                               QMenu, QDialog, QFormLayout, QDialogButtonBox)
from PySide6.QtCore import Qt

# =======================================================
# NEW: Pop-up window for editing an item
# =======================================================
class EditItemDialog(QDialog):
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item Details")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog { background-color: #F9FAFB; }
            QLabel { font-weight: bold; color: #333; }
            QLineEdit, QComboBox { padding: 6px; border: 1px solid #cccccc; border-radius: 4px; background-color: white; color: black; }
        """)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.desc_input = QLineEdit()
        self.location_input = QLineEdit()

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Lost", "Found"])

        self.category_combo = QComboBox()
        if categories:
            for cat in categories:
                self.category_combo.addItem(cat["category_name"], cat["category_id"])

        form_layout.addRow("Item Name:", self.name_input)
        form_layout.addRow("Description:", self.desc_input)
        form_layout.addRow("Type:", self.type_combo)
        form_layout.addRow("Category:", self.category_combo)
        form_layout.addRow("Location:", self.location_input)

        layout.addLayout(form_layout)

        # Standard Save/Cancel buttons for a pop-up window
        self.btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        
        # --- THE FIX ---
        # We hook these buttons into your global styles.qss so they look perfect!
        save_btn = self.btns.button(QDialogButtonBox.Save)
        save_btn.setObjectName("btnSubmit")
        save_btn.setText("Save Changes")
        
        cancel_btn = self.btns.button(QDialogButtonBox.Cancel)
        cancel_btn.setObjectName("btnCancel")
        # ---------------

        layout.addWidget(self.btns)

    def load_data(self, item_data):
        """Pre-fills the boxes with the item's current database values."""
        self.name_input.setText(item_data.get("name", ""))
        self.desc_input.setText(item_data.get("description", ""))
        self.location_input.setText(item_data.get("location", ""))

        type_idx = self.type_combo.findText(item_data.get("type", ""))
        if type_idx >= 0:
            self.type_combo.setCurrentIndex(type_idx)

        cat_id = item_data.get("category_id")
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == cat_id:
                self.category_combo.setCurrentIndex(i)
                break

    def get_data(self):
        """Extracts the newly typed data."""
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "type": self.type_combo.currentText(),
            "category_id": self.category_combo.currentData(),
            "location": self.location_input.text().strip()
        }

# =======================================================
# MAIN VIEW
# =======================================================
class ItemsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        title = QLabel("Manage Active Items")
        title.setStyleSheet("QLabel { font-size: 25px; font-weight: bold; background-color: #b81417; color: white; padding: 15px; }")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(20, 10, 20, 0)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or description...")
        self.search_input.setStyleSheet("padding: 6px;")
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Lost", "Found"])
        self.type_filter.setStyleSheet("padding: 6px; background-color: white;")

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        self.category_filter.setStyleSheet("padding: 6px; background-color: white;")

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("btnSubmit") 
        self.search_btn.setFixedWidth(100)

        filter_layout.addWidget(self.search_input, 3) 
        filter_layout.addWidget(self.type_filter, 1)
        filter_layout.addWidget(self.category_filter, 2)
        filter_layout.addWidget(self.search_btn)
        
        self.layout.addLayout(filter_layout)

        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 10, 20, 0)

        self.table = QTableWidget(0, 5) 
        self.table.setHorizontalHeaderLabels(["Item ID", "Name", "Type", "Category", "Priority"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) 
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) 
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.table.setStyleSheet("""
            QTableWidget { background-color: white; alternate-background-color: #f9f9f9; gridline-color: #e0e0e0; border: 1px solid #cccccc; }
            QHeaderView::section { background-color: #f0f0f0; padding: 4px; border: 1px solid #cccccc; font-weight: bold; }
        """)
        table_layout.addWidget(self.table)
        self.layout.addLayout(table_layout)

        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(20, 10, 20, 10)
        
        self.selected_label = QLabel("Selected Item: None")
        self.selected_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Claimed", "Archived"])
        self.status_combo.setEnabled(False) 
        
        self.update_btn = QPushButton("Update Status")
        self.update_btn.setObjectName("btnSubmit")
        self.update_btn.setEnabled(False) 

        action_layout.addWidget(self.selected_label)
        action_layout.addStretch() 
        action_layout.addWidget(QLabel("Change Status To:"))
        action_layout.addWidget(self.status_combo)
        action_layout.addWidget(self.update_btn)

        self.layout.addLayout(action_layout)

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
            self.table.setItem(row_idx, 4, QTableWidgetItem(item["priority_level"]))

    def get_selected_item_id(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            return int(self.table.item(selected_rows[0].row(), 0).text())
        return None

    def get_item_at_position(self, position):
        item = self.table.itemAt(position)
        if item:
            row = item.row()
            self.table.selectRow(row) 
            item_id = int(self.table.item(row, 0).text())
            item_name = self.table.item(row, 1).text()
            return item_id, item_name
        return None, None

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def ask_confirmation(self, title, message):
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes