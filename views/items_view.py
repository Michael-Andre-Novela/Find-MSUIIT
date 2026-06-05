"""Items management view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt

class ItemsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        # Title Header
        title = QLabel("Manage Active Items")
        title.setStyleSheet("""
            QLabel {
                font-size: 25px; 
                font-weight: bold; 
                background-color: #b81417; 
                color: white;              
                padding: 15px; 
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # ==========================================
        # TOP BAR: FILTERS & SEARCH
        # ==========================================
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

        # Add to layout with stretch factors (Search bar gets the most space)
        filter_layout.addWidget(self.search_input, 3) 
        filter_layout.addWidget(self.type_filter, 1)
        filter_layout.addWidget(self.category_filter, 2)
        filter_layout.addWidget(self.search_btn)
        
        self.layout.addLayout(filter_layout)

        # ==========================================
        # MIDDLE: DATA TABLE
        # ==========================================
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 10, 20, 0)

        self.table = QTableWidget(0, 5) # 0 initial rows, 5 columns
        self.table.setHorizontalHeaderLabels(["Item ID", "Name", "Type", "Category", "Priority"])
        
        # Make the columns stretch to fill the screen, but keep ID column tight
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents) 
        
        # Configure table behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # Select whole rows, not cells
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # Prevent user from typing in cells
        self.table.setAlternatingRowColors(True)
        
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                border: 1px solid #cccccc;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #cccccc;
                font-weight: bold;
            }
        """)
        table_layout.addWidget(self.table)
        self.layout.addLayout(table_layout)

        # ==========================================
        # BOTTOM BAR: ACTIONS
        # ==========================================
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(20, 10, 20, 10)
        
        self.selected_label = QLabel("Selected Item: None")
        self.selected_label.setStyleSheet("font-weight: bold; color: #555;")
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Claimed", "Archived"])
        self.status_combo.setEnabled(False) # Disabled until an item is selected
        
        self.update_btn = QPushButton("Update Status")
        self.update_btn.setObjectName("btnSubmit")
        self.update_btn.setEnabled(False) # Disabled until an item is selected

        action_layout.addWidget(self.selected_label)
        action_layout.addStretch() # Pushes the next widgets to the far right
        action_layout.addWidget(QLabel("Change Status To:"))
        action_layout.addWidget(self.status_combo)
        action_layout.addWidget(self.update_btn)

        self.layout.addLayout(action_layout)

    def populate_categories(self, categories: List[Dict]):
        """Fills the category dropdown for filtering."""
        self.category_filter.clear()
        self.category_filter.addItem("All Categories", None)
        for cat in categories:
            self.category_filter.addItem(cat["category_name"], cat["category_id"])

    def populate_table(self, items: List[Dict]):
        """Clears the table and rebuilds it with new data."""
        self.table.setRowCount(0) 
        for row_idx, item in enumerate(items):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item["item_id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item["type"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item["category_name"] or "None"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(item["priority_level"]))

    def get_selected_item_id(self):
        """Returns the ID of the currently highlighted row."""
        selected_rows = self.table.selectedItems()
        if selected_rows:
            # Column 0 contains the Item ID
            return int(self.table.item(selected_rows[0].row(), 0).text())
        return None

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)