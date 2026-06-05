"""Report item view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QComboBox, QPushButton, QHBoxLayout, QMessageBox,
                               QDateEdit)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

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

        # Main Form Layout
        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(20, 15, 20, 0)
        self.form_layout.setSpacing(10)

        # --- HELPER FUNCTION ---
        def create_field(label_text, widget):
            v_box = QVBoxLayout()
            v_box.setSpacing(2) 
            
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; color: #333; margin-top: 5px;") 
            
            v_box.addWidget(lbl)
            v_box.addWidget(widget)
            return v_box
        # -----------------------

        # Initialize Widgets
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Lost", "Found"])
        
        self.category_combo = QComboBox()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Black Leather Wallet")
        
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Provide detailed features...")
        
        # ID Input 
        self.constituent_input = QLineEdit()
        self.constituent_input.setPlaceholderText("e.g. 2021-0023")
        self.constituent_input.setMaxLength(9) 
        
        regex = QRegularExpression("^[0-9-]+$")
        validator = QRegularExpressionValidator(regex)
        self.constituent_input.setValidator(validator)
        
        # Date Input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        
        self.date_input.setStyleSheet("""
            QDateEdit {
                padding: 6px;
                background-color: #FFFDE7; /* Subtle Yellow Tint */
                color: black;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QDateEdit::drop-down {
                border-left: 1px solid #cccccc;
                width: 25px;
            }
        """)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("e.g. Main Library, 2nd Floor")

        # ==========================================
        # BUILD THE COMPACT UI LAYOUT
        # ==========================================
        
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        row1.addLayout(create_field("Report Type", self.type_combo))
        row1.addLayout(create_field("Category", self.category_combo))
        self.form_layout.addLayout(row1)

        self.form_layout.addLayout(create_field("Item Name", self.name_input))
        self.form_layout.addLayout(create_field("Description", self.desc_input))

        # ROW 4: ID Number and Date with STRETCH FACTORS
        row4 = QHBoxLayout()
        row4.setSpacing(15)
        
        # The '1' means this takes up 1 part of the available space
        row4.addLayout(create_field("Reporter ID Number", self.constituent_input), 1)
        
        # The '2' means this takes up 2 parts of the available space (making it twice as wide)
        row4.addLayout(create_field("Date", self.date_input), 2)
        
        self.form_layout.addLayout(row4)

        self.form_layout.addLayout(create_field("Location", self.location_input))

        self.layout.addLayout(self.form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 20, 20, 0) 
        
        self.submit_btn = QPushButton("Submit Report")
        self.submit_btn.setObjectName("btnSubmit") 
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("btnCancel")  
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()

    def populate_categories(self, categories: List[Dict]):
        self.category_combo.clear()
        for cat in categories:
            self.category_combo.addItem(cat["category_name"], cat["category_id"])
        
    def get_form_data(self):
        return {
            "type": self.type_combo.currentText(),
            "category_id": self.category_combo.currentData(),
            "name": self.name_input.text().strip(),
            "description": self.desc_input.text().strip(),
            "reporter_id": self.constituent_input.text().strip(),
            "location": self.location_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd") 
        }
        
    def clear_form(self):
        self.name_input.clear()
        self.desc_input.clear()
        self.constituent_input.clear()
        self.location_input.clear()
        self.date_input.setDate(QDate.currentDate()) 
        
    def show_message(self, title, message):
        QMessageBox.information(self, title, message)