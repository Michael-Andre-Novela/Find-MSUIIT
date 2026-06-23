"""Claims view."""

from typing import Optional, List, Dict
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QTableWidget, 
                               QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox,
                               QDateEdit)
from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator

class ClaimsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        # Title
        title = QLabel("Claims Management")
        title.setObjectName("viewTitle")                                                
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # ==========================================
        # TOP SECTION: FILE A NEW CLAIM
        # ==========================================
        self.form_layout = QVBoxLayout()
        self.form_layout.setContentsMargins(20, 15, 20, 15)

        def create_field(label_text, widget):
            v_box = QVBoxLayout()
            v_box.setSpacing(2) 
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; margin-top: 5px;")
            v_box.addWidget(lbl)
            v_box.addWidget(widget)
            return v_box

        # Fields
        self.item_id_input = QLineEdit()
        self.item_id_input.setPlaceholderText("e.g. 5")
        self.item_id_input.setMaximumWidth(140) 
        item_regex = QRegularExpression("^[0-9]+$")
        self.item_id_input.setValidator(QRegularExpressionValidator(item_regex))

        self.constituent_input = QLineEdit()
        self.constituent_input.setPlaceholderText("e.g. 2021-0023")
        self.constituent_input.setMaxLength(9) 
        self.constituent_input.setMaximumWidth(120) 
        id_regex = QRegularExpression("^[0-9-]+$")
        self.constituent_input.setValidator(QRegularExpressionValidator(id_regex))

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumWidth(150)
        self.date_input.setMaximumWidth(250)

        # Compact Row Layout
        row1 = QHBoxLayout()
        row1.setSpacing(15)
        row1.addLayout(create_field("Target Item ID", self.item_id_input))
        row1.addLayout(create_field("Claimant ID Number", self.constituent_input))
        row1.addLayout(create_field("Claim Date", self.date_input))
        
        self.submit_btn = QPushButton("File Claim Request")
        self.submit_btn.setObjectName("btnSubmit")
        self.submit_btn.setMinimumHeight(32)
        
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(2)
        dummy_lbl = QLabel("") 
        dummy_lbl.setStyleSheet("margin-top: 5px;")
        btn_layout.addWidget(dummy_lbl)
        btn_layout.addWidget(self.submit_btn)
        
        row1.addLayout(btn_layout)
        row1.addStretch() 

        self.form_layout.addLayout(row1)
        self.layout.addLayout(self.form_layout)

        # Divider line
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background-color: #cccccc; margin: 0px 20px;")
        self.layout.addWidget(divider)

        # ==========================================
        # BOTTOM SECTION: PENDING CLAIMS TABLE
        # ==========================================
        table_layout = QVBoxLayout()
        table_layout.setContentsMargins(20, 10, 20, 0)
        
        table_label = QLabel("Pending Claims Requiring Approval:")
        table_label.setObjectName("sectionLabel")
        table_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        table_layout.addWidget(table_label)

        self.table = QTableWidget(0, 5) 
        self.table.setHorizontalHeaderLabels(["Claim Date", "Item ID", "Item Name", "Claimant Name", "Claimant ID"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) 
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  
        self.table.setAlternatingRowColors(True)
        
        
        table_layout.addWidget(self.table)
        
        # Action Buttons Row
        action_layout = QHBoxLayout()
        
        # POLISHED: The Reject Button
        self.reject_btn = QPushButton("Reject & Delete Claim")
        self.reject_btn.setEnabled(False)
        self.reject_btn.setObjectName("btnReject")

        self.approve_btn = QPushButton("Approve Selected Claim")
        self.approve_btn.setObjectName("btnSubmit")
        self.approve_btn.setEnabled(False) 
        
        action_layout.addStretch()
        action_layout.addWidget(self.reject_btn) # Placed right next to the Approve button
        action_layout.addWidget(self.approve_btn)
        table_layout.addLayout(action_layout)

        self.layout.addLayout(table_layout)

    # --- HELPER METHODS ---
    def get_form_data(self):
        return {
            "item_id": self.item_id_input.text().strip(),
            "id_number": self.constituent_input.text().strip(),
            "date": self.date_input.date().toString("yyyy-MM-dd") 
        }

    def clear_form(self):
        self.item_id_input.clear()
        self.constituent_input.clear()
        self.date_input.setDate(QDate.currentDate()) 

    def populate_table(self, claims: List[Dict]):
        self.table.setRowCount(0) 
        for row_idx, claim in enumerate(claims):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(claim["claim_date"]))
            self.table.setItem(row_idx, 1, QTableWidgetItem(str(claim["item_id"])))
            self.table.setItem(row_idx, 2, QTableWidgetItem(claim["item_name"]))
            self.table.setItem(row_idx, 3, QTableWidgetItem(claim["claimant_name"]))
            self.table.setItem(row_idx, 4, QTableWidgetItem(claim["id_number"]))

    def get_selected_claim(self):
        selected_rows = self.table.selectedItems()
        if selected_rows:
            return {
                "item_id": int(self.table.item(selected_rows[0].row(), 1).text()),
                "id_number": self.table.item(selected_rows[0].row(), 4).text()
            }
        return None

    def show_message(self, title, message):
        QMessageBox.information(self, title, message)

    def ask_confirmation(self, title, message):
        """Pops up a Yes/No dialog to prevent accidental deletions."""
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes