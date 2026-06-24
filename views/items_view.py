"""Items management view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
                               QMenu, QDialog, QFormLayout, QDialogButtonBox)
from PySide6.QtCore import Qt

# =======================================================
# Pop-up window for adding a Category
# =======================================================
class AddCategoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Category")
        self.setMinimumWidth(350)
        self.setStyleSheet("""
            QDialog { background-color: #F9FAFB; }
            QLabel { font-weight: bold; color: #333; }
            QLineEdit { padding: 6px; border: 1px solid #cccccc; border-radius: 4px; background-color: white; color: black; }
        """)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Tumblers, Umbrellas...")
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Optional description")

        form_layout.addRow("Category Name:", self.name_input)
        form_layout.addRow("Description:", self.desc_input)
        layout.addLayout(form_layout)

        self.btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        
        save_btn = self.btns.button(QDialogButtonBox.Save)
        save_btn.setObjectName("btnSubmit")
        save_btn.setText("Add Category")
        
        cancel_btn = self.btns.button(QDialogButtonBox.Cancel)
        cancel_btn.setObjectName("btnCancel")

        layout.addWidget(self.btns)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip()
        }

# =======================================================
# Pop-up window for editing an item
# =======================================================
class EditItemDialog(QDialog):
    def __init__(self, parent=None, categories=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Item Details")
        self.setMinimumWidth(400)

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

        self.btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        
        save_btn = self.btns.button(QDialogButtonBox.Save)
        save_btn.setObjectName("btnSubmit")
        save_btn.setText("Save Changes")
        
        cancel_btn = self.btns.button(QDialogButtonBox.Cancel)
        cancel_btn.setObjectName("btnCancel")

        layout.addWidget(self.btns)

    def load_data(self, item_data):
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
        title.setObjectName("viewTitle")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # ── Filter / Search Bar ───────────────────────────────────────
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(20, 10, 20, 0)
        filter_layout.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or description...")
        # Enter key triggers search without clicking the button
        self.search_input.returnPressed.connect(self._emit_search)

        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Lost", "Found"])
        # Changing type auto-triggers a new search
        self.type_filter.currentIndexChanged.connect(self._emit_search)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", None)
        # Changing category auto-triggers a new search
        self.category_filter.currentIndexChanged.connect(self._emit_search)

        self.add_category_btn = QPushButton("+ New Category")
        self.add_category_btn.setObjectName("btnSecondary")

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("btnSubmit")
        self.search_btn.setFixedWidth(100)

        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(self.type_filter, 1)
        filter_layout.addWidget(self.category_filter, 2)
        filter_layout.addWidget(self.add_category_btn)
        filter_layout.addWidget(self.search_btn)

        self.layout.addLayout(filter_layout)

        # ── Items Table ───────────────────────────────────────────────
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

        table_layout.addWidget(self.table)
        self.layout.addLayout(table_layout)

    # ── Internal helpers ──────────────────────────────────────────────

    def _emit_search(self):
        """Fires search whether triggered by Enter key, button click, or filter change.
        Routes everything through search_btn.click() so the presenter only
        needs a single connection point."""
        self.search_btn.click()

    # ── Public interface ──────────────────────────────────────────────

    def populate_categories(self, categories: List[Dict]):
        # Block signals while rebuilding the combo so we don't fire spurious searches
        self.category_filter.blockSignals(True)
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", None)
        for cat in categories:
            self.category_filter.addItem(cat["category_name"], cat["category_id"])
        self.category_filter.blockSignals(False)

    def populate_table(self, items: List[Dict]):
        self.table.setRowCount(0)

        if not items:
            # Show a friendly empty-state row that spans all columns
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No items found matching your search criteria.")
            empty_item.setTextAlignment(Qt.AlignCenter)
            empty_item.setFlags(Qt.ItemIsEnabled)   # Not selectable / not editable
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 5)
            return

        # Clear any leftover column span from a previous empty state
        self.table.setSpan(0, 0, 1, 1)

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
            # Guard against the empty-state row (no valid item_id)
            id_cell = self.table.item(row, 0)
            if not id_cell or not id_cell.text().isdigit():
                return None, None
            self.table.selectRow(row)
            item_id = int(id_cell.text())
            item_name = self.table.item(row, 1).text()
            return item_id, item_name
        return None, None

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def ask_confirmation(self, title, message):
        reply = QMessageBox.question(self, title, message,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        return reply == QMessageBox.Yes