"""Auto-Matching results popup dialog."""

from typing import List, Dict, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QDialogButtonBox, QAbstractItemView
)

class MatchesDialog(QDialog):
    def __init__(self, parent: Optional[QDialog] = None, target_item: Optional[dict] = None):
        super().__init__(parent)
        self.setWindowTitle("Auto-Matching Candidates")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        

        self.target_item = target_item
        self.selected_match: Optional[dict] = None

        layout = QVBoxLayout(self)

        # Header Info
        header_text = f"Auto-matching candidates for: <b>{target_item.get('name', 'Item')}</b>"
        if target_item.get("category_name"):
            header_text += f" (<i>{target_item['category_name']}</i>)"
        
        self.lbl_info = QLabel(header_text, self)
        self.lbl_info.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.lbl_info)

        # Candidates Table
        self.table = QTableWidget(0, 4, self)
        self.table.setHorizontalHeaderLabels(["Item ID", "Name", "Category", "Match Score"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.table)

        # Actions Layout
        self.action_layout = QHBoxLayout()
        
        self.lbl_status = QLabel("Select a candidate match to proceed with a claim request.", self)
        self.lbl_status.setStyleSheet("color: #555555; font-style: italic;")
        self.action_layout.addWidget(self.lbl_status)
        self.action_layout.addStretch()

        self.btn_claim = QPushButton("File Claim for Selected", self)
        self.btn_claim.setObjectName("btnSubmit")
        self.btn_claim.setEnabled(False)
        self.btn_claim.clicked.connect(self.accept)
        self.action_layout.addWidget(self.btn_claim)

        self.btn_close = QPushButton("Close", self)
        self.btn_close.setObjectName("btnCancel")
        self.btn_close.clicked.connect(self.reject)
        self.action_layout.addWidget(self.btn_close)

        layout.addLayout(self.action_layout)

        # Connect Table selection change to update claim button
        self.table.itemSelectionChanged.connect(self.on_selection_changed)

        self.candidates: List[dict] = []

    def populate_matches(self, matches: List[dict]) -> None:
        """Populate the table with candidate matches."""
        self.candidates = matches
        self.table.setRowCount(0)
        
        if not matches:
            self.lbl_status.setText("No matching candidates met the score threshold.")
            return

        for row_idx, match in enumerate(matches):
            self.table.insertRow(row_idx)
            
            id_item = QTableWidgetItem(str(match.get("item_id", "")))
            name_item = QTableWidgetItem(match.get("name", ""))
            cat_item = QTableWidgetItem(match.get("category_name") or "None")
            
            score_val = match.get("match_score", 0.0)
            score_percent = f"{int(score_val * 100)}%"
            score_item = QTableWidgetItem(score_percent)
            score_item.setFont(score_item.font())
            score_item.font().setBold(True)

            self.table.setItem(row_idx, 0, id_item)
            self.table.setItem(row_idx, 1, name_item)
            self.table.setItem(row_idx, 2, cat_item)
            self.table.setItem(row_idx, 3, score_item)

            for col in range(4):
                cell = self.table.item(row_idx, col)
                if cell:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def on_selection_changed(self) -> None:
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            self.btn_claim.setEnabled(True)
            row_idx = selected_rows[0].row()
            self.selected_match = self.candidates[row_idx]
        else:
            self.btn_claim.setEnabled(False)
            self.selected_match = None

    def get_selected_match(self) -> Optional[dict]:
        return self.selected_match
