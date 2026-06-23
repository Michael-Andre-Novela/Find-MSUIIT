"""Dashboard view."""

from typing import List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QAbstractItemView
)


class DashboardView(QWidget):

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # ── Header ────────────────────────────────────────────────────
        header_layout = QHBoxLayout()

        self.lbl_title = QLabel("Dashboard Overview", self)
        self.lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #1A1A1A;")

        self.btn_refresh = QPushButton("Refresh", self)
        self.btn_refresh.setObjectName("refreshButton")

        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_refresh)

        self.main_layout.addLayout(header_layout)

        # ── Notification Banner ───────────────────────────────────────
        self.alert_frame = QFrame(self)
        self.alert_frame.setObjectName("alertFrame")
        self.alert_frame.setVisible(False)
        self.alert_layout = QVBoxLayout(self.alert_frame)
        self.alert_layout.setContentsMargins(15, 10, 15, 10)
        
        self.alert_title = QLabel("⚠️ System Notifications (Unclaimed Found Items stored > 30 days):", self)
        self.alert_title.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.alert_layout.addWidget(self.alert_title)
        
        self.alert_list_label = QLabel(self)
        self.alert_list_label.setStyleSheet("font-size: 12px;")
        self.alert_layout.addWidget(self.alert_list_label)

        self.main_layout.addWidget(self.alert_frame)

        # ── Stat cards row ────────────────────────────────────────────
        self.cards_row = QHBoxLayout()
        self.cards_row.setSpacing(10)

        self.card_lost      = self._create_stat_card("Active Lost Items")
        self.card_found     = self._create_stat_card("Active Found Items")
        self.card_pending   = self._create_stat_card("Pending Claims")
        self.card_claimed   = self._create_stat_card("Total Claimed")
        self.card_unclaimed = self._create_stat_card("Unclaimed Found Items")

        for card in [self.card_lost, self.card_found, self.card_pending, self.card_claimed, self.card_unclaimed]:
            self.cards_row.addWidget(card)

        self.main_layout.addLayout(self.cards_row)

        # ── Active items table ────────────────────────────────────────
        self.lbl_section = QLabel("Active Items", self)
        self.lbl_section.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.main_layout.addWidget(self.lbl_section)

        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(["Item ID", "Name", "Type", "Category", "Priority"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        self.main_layout.addWidget(self.table)

    # ── Helpers ───────────────────────────────────────────────────────

    def _create_stat_card(self, title: str) -> QFrame:
        card = QFrame(self)
        card.setObjectName("statCard")
        card.setMinimumHeight(80)

        layout = QVBoxLayout(card)

        lbl_title = QLabel(title, card)
        lbl_title.setStyleSheet("font-size: 11px; font-weight: bold;")
        lbl_value = QLabel("0", card)
        lbl_value.setStyleSheet("font-size: 28px; font-weight: 800;")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value, 0, Qt.AlignmentFlag.AlignBottom)

        card.setProperty("displayLabel", lbl_value)
        return card

    # ── Public interface ──────────────────────────────────────────────

    def update_counters(self, lost: int, found: int, pending: int, claimed: int, unclaimed: int) -> None:
        """Updates all five stat cards."""
        self.card_lost.property("displayLabel").setText(str(lost))
        self.card_found.property("displayLabel").setText(str(found))
        self.card_pending.property("displayLabel").setText(str(pending))
        self.card_claimed.property("displayLabel").setText(str(claimed))
        self.card_unclaimed.property("displayLabel").setText(str(unclaimed))

    def show_alerts(self, alerts: List[dict]) -> None:
        """Shows or hides alerts based on the count of items."""
        if not alerts:
            self.alert_frame.setVisible(False)
            return
        
        self.alert_frame.setVisible(True)
        text = ""
        for alert in alerts[:5]: # Show max 5 items in the list to avoid cluttering
            text += f"• <b>{alert['name']}</b> (ID: {alert['item_id']}) reported on {alert['date_found']} at {alert['location_found']}\n"
        
        if len(alerts) > 5:
            text += f"• ...and {len(alerts) - 5} more unclaimed items."
            
        self.alert_list_label.setText(text.strip())

    def show_items(self, items: List[dict]) -> None:
        """Populates the active items table."""
        self.table.setRowCount(0)

        if not items:
            return

        for row_idx, item in enumerate(items):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(item.get("item_id", ""))))
            self.table.setItem(row_idx, 1, QTableWidgetItem(item.get("name", "")))
            self.table.setItem(row_idx, 2, QTableWidgetItem(item.get("type", "")))
            self.table.setItem(row_idx, 3, QTableWidgetItem(item.get("category_name") or "Uncategorized"))
            self.table.setItem(row_idx, 4, QTableWidgetItem(item.get("priority_level", "")))

            # Color-code the Type cell
            type_item = self.table.item(row_idx, 2)
            if item.get("type") == "Lost":
                type_item.setForeground(Qt.GlobalColor.darkRed)
            elif item.get("type") == "Found":
                type_item.setForeground(Qt.GlobalColor.darkBlue)

            for col in range(5):
                cell = self.table.item(row_idx, col)
                if cell:
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)