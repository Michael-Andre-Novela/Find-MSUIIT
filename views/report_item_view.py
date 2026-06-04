"""Report item view."""

from typing import Optional, List, Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QFormLayout, QHBoxLayout, QMessageBox)

class ReportItemView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
       # Title
        title = QLabel("Report Lost or Found Item")
        title.setStyleSheet("""
            QLabel {
                font-size: 25px; 
                font-weight: bold; 
                margin-bottom: 10px;
                background-color: #b81417; 
                color: white;            
                padding: 10px; 
                border-radius: 5px;
            }
        """)
        title.setAlignment(Qt.AlignCenter) 
        self.layout.addWidget(title)

        self.form_layout = QFormLayout()
        
        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Lost", "Found"])
        self.form_layout.addRow("Report Type:", self.type_combo)
        self.type_combo.setStyleSheet("""
			QComboBox {                
			}
		""")

        # Category
        self.category_combo = QComboBox()
        self.form_layout.addRow("Category:", self.category_combo)

        # Item Name
        self.name_input = QLineEdit()
        self.form_layout.addRow("Item Name:", self.name_input)

        # Description
        self.desc_input = QLineEdit()
        self.form_layout.addRow("Description:", self.desc_input)

        # Reporter ID
        self.constituent_input = QLineEdit()
        self.constituent_input.setPlaceholderText("e.g. 2021-0023")
        self.form_layout.addRow("Reporter ID Number:", self.constituent_input)
        
        # Location
        self.location_input = QLineEdit()
        self.form_layout.addRow("Location:", self.location_input)
        
        # Date
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText("YYYY-MM-DD")
        self.form_layout.addRow("Date:", self.date_input)

        self.layout.addLayout(self.form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.submit_btn = QPushButton("Submit Report")
        self.submit_btn.setObjectName("btnSubmit") # Links to styles.qss
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("btnCancel")  # Links to styles.qss
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()

    def populate_categories(self, categories: List[Dict]):
        """Fills the dropdown with categories from the database."""
        self.category_combo.clear()
        for cat in categories:
            # Display the name, but store the category_id secretly in the background
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