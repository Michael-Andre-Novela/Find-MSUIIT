"""Constituents view."""

from typing import Optional
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QHBoxLayout, QMessageBox)
from PySide6.QtCore import Qt

class ConstituentsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10) # 0 margins for edge-to-edge header

        # Title
        title = QLabel("Register New Constituent")
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

        # Switched to QVBoxLayout for stacked labels and inputs
        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(20, 20, 20, 0) # Padding for the form
        self.form_layout.setSpacing(5) # Space between the fields

        # --- HELPER FUNCTION FOR CLEAN CODE ---
        def add_field(label_text, widget):
            """Creates a bold label and adds it directly above the input widget."""
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; color: #333; margin-top: 10px;") 
            self.form_layout.addWidget(lbl)
            self.form_layout.addWidget(widget)
        # --------------------------------------

        # Input Fields
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. 2021-0023")
        add_field("ID Number", self.id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Juan dela Cruz")
        add_field("Full Name", self.name_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. juan@g.msuiit.edu.ph")
        add_field("Email Address", self.email_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g. 09171234567 (Optional)")
        add_field("Contact Phone", self.phone_input)

        self.layout.addLayout(self.form_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(20, 20, 20, 0) # Added margin above buttons
        
        self.submit_btn = QPushButton("Register Constituent")
        self.submit_btn.setObjectName("btnSubmit") 
        
        self.clear_btn = QPushButton("Clear Form")
        self.clear_btn.setObjectName("btnCancel")  
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.clear_btn)
        
        self.layout.addLayout(btn_layout)
        self.layout.addStretch()

    def get_form_data(self):
        """Scrapes all text boxes and returns a dictionary."""
        return {
            "id_number": self.id_input.text().strip(),
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip()
        }
        
    def clear_form(self):
        self.id_input.clear()
        self.name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        
    def show_message(self, title, message):
        """Helper to show popup alerts."""
        QMessageBox.information(self, title, message)