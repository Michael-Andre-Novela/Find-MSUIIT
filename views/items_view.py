"""Items management view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt

<<<<<<< Updated upstream
=======
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
            "name": self.name_input.text().strip(),
            "description": "" # Passed as blank so we don't break the presenter
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
>>>>>>> Stashed changes
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

        # Add to layout with stretch factors (Search bar gets the most space)
        filter_layout.addWidget(self.search_input, 3) 
        filter_layout.addWidget(self.type_filter, 1)
        filter_layout.addWidget(self.category_filter, 2)
<<<<<<< Updated upstream
=======
        filter_layout.addWidget(self.add_category_btn)
        filter_layout.addWidget(self.delete_category_btn) # Placed right next to the add button
>>>>>>> Stashed changes
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