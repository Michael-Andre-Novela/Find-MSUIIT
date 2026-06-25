"""Items management view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
                               QMenu, QDialog, QFormLayout, QDialogButtonBox, QScrollArea, QFileDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class ItemDetailsDialog(QDialog):
    """Dialog to display item details with image preview."""
    
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle(f"Item Details: {item_data.get('name', 'Unknown')}")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        
        main_layout = QVBoxLayout(self)
        
        # Scroll area for content
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_layout.setSpacing(15)
        
        # Header - Item Name
        title = QLabel(f"{item_data.get('name', 'N/A')}")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #7A1C1C;") # Maroon title matches theme
        scroll_layout.addWidget(title)
        
        # Image Display
        photo_filepath = item_data.get("photo_filepath")
        if photo_filepath:
            try:
                import os
                if os.path.exists(photo_filepath):
                    pixmap = QPixmap(photo_filepath)
                    if not pixmap.isNull():
                        img_label = QLabel()
                        # Scale image smoothly
                        scaled_pixmap = pixmap.scaledToWidth(450, Qt.SmoothTransformation)
                        img_label.setPixmap(scaled_pixmap)
                        img_label.setAlignment(Qt.AlignCenter)
                        img_label.setStyleSheet("border: 1px solid #D1D5DB; border-radius: 8px; padding: 4px;")
                        scroll_layout.addWidget(img_label)
                    else:
                        img_label = QLabel("⚠️ Image file is corrupt or invalid.")
                        img_label.setStyleSheet("font-style: italic;")
                        scroll_layout.addWidget(img_label)
                else:
                    img_label = QLabel("📷 No image file found on disk.")
                    img_label.setStyleSheet("font-style: italic;")
                    scroll_layout.addWidget(img_label)
            except Exception as e:
                img_label = QLabel(f"⚠️ Error loading image: {e}")
                img_label.setStyleSheet("font-style: italic;")
                scroll_layout.addWidget(img_label)
        else:
            img_label = QLabel("📷 No image attached.")
            img_label.setStyleSheet("font-style: italic;")
            scroll_layout.addWidget(img_label)
            
        # Grid/Form layout for details
        details_widget = QWidget()
        details_layout = QFormLayout(details_widget)
        details_layout.setSpacing(8)
        details_layout.setLabelAlignment(Qt.AlignRight)
        
        def add_detail_row(label_name, value):
            lbl = QLabel(f"<b>{label_name}:</b>")
            val = QLabel(str(value) if value is not None and value != "" else "N/A")
            val.setWordWrap(True)
            details_layout.addRow(lbl, val)
            
        add_detail_row("Item ID", item_data.get("item_id"))
        add_detail_row("Report Type", item_data.get("type"))
        add_detail_row("Current Status", item_data.get("status"))
        add_detail_row("Category", item_data.get("category_name"))
        add_detail_row("Priority Level", item_data.get("priority_level"))
        
        # Details about date and location
        event_type = "Lost" if item_data.get("type") == "Lost" else "Found"
        add_detail_row(f"Date {event_type}", item_data.get("event_date"))
        add_detail_row(f"Location {event_type}", item_data.get("event_location"))
        
        # Details about constituent
        reporter_label = "Reporter Name" if item_data.get("type") == "Lost" else "Finder Name"
        add_detail_row(reporter_label, item_data.get("constituent_name"))
        add_detail_row("Constituent ID", item_data.get("constituent_id_number"))
        
        # Description (larger display)
        desc_title = QLabel("<b>Description:</b>")
        desc_val = QLabel(item_data.get("description") or "No description provided.")
        desc_val.setWordWrap(True)
        desc_val.setStyleSheet("font-style: italic; padding-left: 10px;")
        details_layout.addRow(desc_title, desc_val)
        
        scroll_layout.addWidget(details_widget)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
        # Action layout buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setObjectName("btnCancel")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        main_layout.addLayout(btn_layout)
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

        form_layout.addRow("Category Name:", self.name_input)
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
            "name": self.name_input.text().strip()
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

        # Image Attachment field
        photo_container = QWidget()
        photo_layout = QHBoxLayout(photo_container)
        photo_layout.setContentsMargins(0, 0, 0, 0)
        self.photo_input = QLineEdit()
        self.photo_input.setPlaceholderText("Optional image filepath...")
        self.photo_btn = QPushButton("Browse")
        self.photo_btn.setObjectName("btnSecondary")
        self.photo_btn.setFixedWidth(80)
        self.photo_btn.clicked.connect(self.handle_browse_photo)
        photo_layout.addWidget(self.photo_input)
        photo_layout.addWidget(self.photo_btn)
        form_layout.addRow("Image:", photo_container)

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

    def handle_browse_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Photo", "", "Images (*.png *.jpg *.jpeg *.webp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)

    def load_data(self, item_data):
        self.name_input.setText(item_data.get("name", ""))
        self.desc_input.setText(item_data.get("description", ""))
        self.location_input.setText(item_data.get("location", ""))
        self.photo_input.setText(item_data.get("photo_filepath", ""))

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
            "location": self.location_input.text().strip(),
            "photo_filepath": self.photo_input.text().strip()
        }

# =======================================================
# MAIN VIEW
# =======================================================
class ItemsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 10)

        title = QLabel("Manage Active Items")
        title.setObjectName("viewTitle")
        title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(title)

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

        # --- NEW: Delete Category Button ---
        self.delete_category_btn = QPushButton("- Delete Category")
        self.delete_category_btn.setStyleSheet("""
            QPushButton { background-color: #ef4444; color: white; font-weight: bold; border-radius: 4px; padding: 6px 12px; }
            QPushButton:hover { background-color: #dc2626; }
        """)
        # -----------------------------------

        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("btnSubmit")
        self.search_btn.setFixedWidth(100)

        filter_layout.addWidget(self.search_input, 3)
        filter_layout.addWidget(self.type_filter, 1)
        filter_layout.addWidget(self.category_filter, 2)
        filter_layout.addWidget(self.add_category_btn)
        filter_layout.addWidget(self.delete_category_btn) # Placed right next to the add button
        filter_layout.addWidget(self.search_btn)
        
        self.main_layout.addLayout(filter_layout)

        # ─── FIXED TABLE LAYOUT MANAGEMENT ─────────────────────────────────
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 10, 20, 10)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Item ID", "Name", "Type", "Category", "Priority"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)

        # 1. Add the table widget DIRECTLY into our sub-layout container
        table_layout.addWidget(self.table)
        
        # 2. Append the structured sub-layout to the primary master layout wrapper
        self.main_layout.addLayout(table_layout)
        # ──────────────────────────────────────────────────────────────────

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

    def showEvent(self, event):
        super().showEvent(event)
        self.search_btn.click()
    
