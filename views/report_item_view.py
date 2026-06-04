"""Report item view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt

class ReportItemView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        # Title
        title = QLabel("Report Lost or Found Item")
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

        # We switch from QFormLayout to QVBoxLayout to stack labels on top of inputs
        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(20, 20, 20, 0)
        self.form_layout.setSpacing(5) # Space between the fields

        # --- HELPER FUNCTION FOR CLEAN CODE ---
        def add_field(label_text, widget):
            """Creates a bold label and adds it directly above the input widget."""
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; color: #333; margin-top: 10px;") 
            self.form_layout.addWidget(lbl)
            self.form_layout.addWidget(widget)
        # --------------------------------------

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Lost", "Found"])
        add_field("Report Type", self.type_combo)

        # Category
        self.category_combo = QComboBox()
        add_field("Category", self.category_combo)

        # Item Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Black Leather Wallet")
        add_field("Item Name", self.name_input)

        # Description
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Provide detailed features...")
        add_field("Description", self.desc_input)

        # Reporter ID
        self.constituent_input = QLineEdit()
        self.constituent_input.setPlaceholderText("e.g. 2021-0023")
        add_field("Reporter ID Number", self.constituent_input)
        
        # Location
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g. Main Library, 2nd Floor")
        add_field("Location", self.location_input)
        
        # Date
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        add_field("Date", self.date_input)

        self.layout.addLayout(self.form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 20, 20, 0) # Added margin above buttons
        
        self.submit_btn = QPushButton("Submit Report")
        self.submit_btn.setObjectName("btnSubmit") 
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("btnCancel")  
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()

    def populate_categories(self, categories: List[Dict]):
        """Fills the dropdown with categories from the database."""
        self.category_combo.clear()
        for cat in categories:
            self.category_combo.addItem(cat["category_name"], cat["category_id"])
        
    def get_form_data(self):
        """Gathers all input fields into a single dictionary."""
        return {
            "type": self.type_combo.currentText(),
            "category_id": self.category_combo.currentData(),
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "reporter_id": self.constituent_input.text().strip(),
            "location": self.location_input.text().strip(),
            "date": self.date_input.text().strip()
        }
        
    def clear_form(self):
        self.name_input.clear()
        self.desc_input.clear()
        self.constituent_input.clear()
        self.location_input.clear()
        self.date_input.clear()
        
    def show_message(self, title, message):
        """Helper to show popup alerts."""
        QMessageBox.information(self, title, message)