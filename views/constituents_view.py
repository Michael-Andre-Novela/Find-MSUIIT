"""Constituents management view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

class ConstituentsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        # Title
        title = QLabel("Constituents Management")
        title.setStyleSheet("""
            QLabel {
                font-size: 25px; font-weight: bold; 
                background-color: #b81417; color: white; padding: 15px; 
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # ==========================================
        # TOP SECTION: REGISTRATION / EDIT FORM
        # ==========================================
        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(20, 15, 20, 15)

        def create_field(label_text, widget):
            v_box = QVBoxLayout()
            v_box.setSpacing(2) 
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; color: #333; margin-top: 5px;") 
            v_box.addWidget(lbl)
            v_box.addWidget(widget)
            return v_box

        # Hidden field to track if we are editing an existing constituent
        self.hidden_constituent_id = None 

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("e.g. 2021-0023")
        self.id_input.setMaxLength(9) 
        self.id_input.setMaximumWidth(140) 
        self.id_input.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9-]+$")))

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("e.g. 09171234567")
        self.phone_input.setMaxLength(11) 
        self.phone_input.setMaximumWidth(160)
        self.phone_input.setValidator(QRegularExpressionValidator(QRegularExpression("^[0-9]+$")))

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Juan dela Cruz")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("e.g. juan@g.msuiit.edu.ph")

        row1 = QHBoxLayout()
        row1.setSpacing(15)
        row1.addLayout(create_field("ID Number", self.id_input))
        row1.addLayout(create_field("Contact Phone", self.phone_input))
        row1.addStretch() 
        self.form_layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(15)
        row2.addLayout(create_field("Full Name", self.name_input))
        row2.addLayout(create_field("Email Address", self.email_input))
        self.form_layout.addLayout(row2)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 15, 0, 0)
        
        self.submit_btn = QPushButton("Register New Constituent")
        self.submit_btn.setObjectName("btnSubmit") 
        self.submit_btn.setMinimumHeight(35)
        
        self.update_btn = QPushButton("Save Updated Information")
        self.update_btn.setObjectName("btnSubmit")
        self.update_btn.setMinimumHeight(35)
        self.update_btn.setStyleSheet("background-color: #d97706;") 
        self.update_btn.setVisible(False)

        # POLISHED: New Delete Button
        self.delete_btn = QPushButton("Delete Constituent")
        self.delete_btn.setMinimumHeight(35)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #4b5563; /* Sleek Gray */
                color: white; font-weight: bold; border-radius: 4px; padding: 6px 16px;
            }
            QPushButton:hover { background-color: #374151; }
        """)
        self.delete_btn.setVisible(False)

        self.clear_btn = QPushButton("Clear Form / Cancel Edit")
        self.clear_btn.setObjectName("btnCancel")  
        self.clear_btn.setMinimumHeight(35)
        
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn) # Inserted next to the update button
        btn_layout.addWidget(self.clear_btn)
        btn_layout.addStretch() 
        self.form_layout.addLayout(btn_layout)
        self.layout.addLayout(self.form_layout)

        # Divider line
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #cccccc; margin: 0px 20px;")
        self.layout.addWidget(divider)

        # ==========================================
        # BOTTOM SECTION: CONSTITUENTS DIRECTORY
        # ==========================================
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 10, 20, 0)

        # Search Bar
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Name or ID Number...")
        self.search_input.setStyleSheet("padding: 6px;")
        self.search_btn = QPushButton("Search")
        self.search_btn.setObjectName("btnSubmit")
        search_row.addWidget(self.search_input)
        search_row.addWidget(self.search_btn)
        table_layout.addLayout(search_row)

        # Data Table
        self.table = QTableWidget(0, 5) 
        self.table.setHorizontalHeaderLabels(["Internal ID", "ID Number", "Name", "Email", "Phone"])
        self.table.setColumnHidden(0, True) 
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) 
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #cccccc; }
            QHeaderView::section { background-color: #f0f0f0; padding: 4px; font-weight: bold; }
        """)
        
        instruction = QLabel("Click any row below to edit or delete constituent information:")
        instruction.setStyleSheet("color: #555; font-style: italic;")
        table_layout.addWidget(instruction)
        table_layout.addWidget(self.table)

        self.layout.addLayout(table_layout)

    # --- METHODS ---
    def get_form_data(self):
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
        self.id_input.setEnabled(True) 
        self.hidden_constituent_id = None
        self.submit_btn.setVisible(True)
        self.update_btn.setVisible(False)
        self.delete_btn.setVisible(False) # Hide delete button on clear
        self.table.clearSelection()

    def populate_table(self, constituents: List[Dict]):
        self.table.setRowCount(0) 
        for row_idx, person in enumerate(constituents):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(person["constituent_id"])))
            self.table.setItem(row_idx, 1, QTableWidgetItem(person["id_number"]))
            self.table.setItem(row_idx, 2, QTableWidgetItem(person["name"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(person["contact_email"]))
            self.table.setItem(row_idx, 4, QTableWidgetItem(person["contact_phone"] or ""))

    def populate_form_for_edit(self, row_index):
        """Grabs data from the clicked row and puts it in the top form."""
        self.hidden_constituent_id = int(self.table.item(row_index, 0).text())
        self.id_input.setText(self.table.item(row_index, 1).text())
        self.name_input.setText(self.table.item(row_index, 2).text())
        self.email_input.setText(self.table.item(row_index, 3).text())
        self.phone_input.setText(self.table.item(row_index, 4).text())
        
        self.id_input.setEnabled(False) 
        self.submit_btn.setVisible(False)
        self.update_btn.setVisible(True)
        self.delete_btn.setVisible(True) # Show delete button

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def ask_confirmation(self, title, message):
        """Pops up a Yes/No dialog to prevent accidental deletions."""
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes