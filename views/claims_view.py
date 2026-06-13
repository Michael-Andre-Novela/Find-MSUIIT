"""Claims view: displays pending claims and exposes Approve / Reject controls."""

from typing import Optional, List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QAbstractItemView,
)


# Column order must match populate_claims()
_COLUMNS = ["Item ID", "Item Name", "Claimant Name", "ID Number", "Claim Date"]


class ClaimsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # ── Header ────────────────────────────────────────────────────
        header_layout = QHBoxLayout()

        self.lbl_title = QLabel("Manage Claims", self)
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A1A1A;")

        self.btn_refresh = QPushButton("Refresh", self)
        self.btn_refresh.setObjectName("refreshButton")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)

        self.main_layout.addLayout(header_layout)

        # ── Pending claims table ───────────────────────────────────────
        self.table = QTableWidget(self)
        self.table.setColumnCount(len(_COLUMNS))
        self.table.setHorizontalHeaderLabels(_COLUMNS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)

        self.main_layout.addWidget(self.table)

        # ── Action buttons ─────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_approve = QPushButton("✔  Approve Claim", self)
        self.btn_approve.setObjectName("btnSubmit")

        self.btn_reject = QPushButton("✘  Reject Claim", self)
        self.btn_reject.setObjectName("btnCancel")

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_approve)
        btn_layout.addWidget(self.btn_reject)

        self.main_layout.addLayout(btn_layout)

    # =========================================================================
    # PUBLIC INTERFACE METHODS
    # =========================================================================

    def populate_claims(self, claims: List[Dict]) -> None:
        """Fills the table with pending claim rows from the presenter."""
        self.table.setRowCount(0)

        for row_data in claims:
            row = self.table.rowCount()
            self.table.insertRow(row)

            values = [
                str(row_data.get("item_id", "")),
                row_data.get("item_name", ""),
                row_data.get("claimant_name", ""),
                row_data.get("id_number", ""),
                row_data.get("claim_date", ""),
            ]

            for col, value in enumerate(values):
                cell = QTableWidgetItem(value)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, cell)

    def get_selected_claim(self) -> tuple:
        """Returns (item_id, id_number) of the selected row, or (None, None)."""
        selected = self.table.selectedItems()
        if not selected:
            return None, None

        current_row = self.table.currentRow()
        try:
            item_id = int(self.table.item(current_row, 0).text())
            id_number = self.table.item(current_row, 3).text()
            return item_id, id_number
        except (ValueError, AttributeError):
            return None, None

    def show_message(self, title: str, message: str) -> None:
        """Shows a popup alert dialog."""
        QMessageBox.information(self, title, message)

