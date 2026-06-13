"""Maintenance view for database backup, restore, and optimization."""

from typing import Optional, List
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QMessageBox, QFrame,
    QSpacerItem, QSizePolicy
)

class MaintenanceView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 10)

        # Title Header
        title = QLabel("System Maintenance & Utilities")
        title.setStyleSheet("QLabel { font-size: 25px; font-weight: bold; background-color: #111827; color: white; padding: 15px; }")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)

        # Section 1: Backup & Restore Manager
        backup_group = QFrame(self)
        backup_group.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            QLabel { border: none; font-weight: bold; }
        """)
        backup_group_layout = QVBoxLayout(backup_group)
        backup_group_layout.setContentsMargins(15, 15, 15, 15)
        backup_group_layout.setSpacing(10)

        lbl_backup_title = QLabel("📦 Database Backup & Restore Manager", backup_group)
        lbl_backup_title.setStyleSheet("font-size: 16px; color: #b81417;")
        backup_group_layout.addWidget(lbl_backup_title)

        lbl_backup_desc = QLabel(
            "Create full backups of the current system database or select an "
            "existing backup file to restore the database to a previous state.",
            backup_group
        )
        lbl_backup_desc.setStyleSheet("font-weight: normal; color: #555555; font-size: 12px;")
        backup_group_layout.addWidget(lbl_backup_desc)

        # List widget for backups
        self.backup_list = QListWidget(backup_group)
        self.backup_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-family: monospace;
                font-size: 13px;
                color: black;
            }
            QListWidget::item {
                padding: 6px;
            }
            QListWidget::item:selected {
                background-color: #FEE2E2;
                color: #7A1C1C;
                font-weight: bold;
            }
        """)
        self.backup_list.setMinimumHeight(150)
        backup_group_layout.addWidget(self.backup_list)

        # Button Row for Backups
        btn_backup_row = QHBoxLayout()
        
        self.btn_create_backup = QPushButton("Create New Backup", backup_group)
        self.btn_create_backup.setObjectName("btnSubmit")
        self.btn_create_backup.setStyleSheet("""
            QPushButton { background-color: #10b981; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #059669; }
        """)

        self.btn_restore_backup = QPushButton("Restore Selected Backup", backup_group)
        self.btn_restore_backup.setEnabled(False)
        self.btn_restore_backup.setStyleSheet("""
            QPushButton { background-color: #d97706; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover:!disabled { background-color: #b45309; }
            QPushButton:disabled { background-color: #d1d5db; color: #9ca3af; }
        """)

        btn_backup_row.addWidget(self.btn_create_backup)
        btn_backup_row.addWidget(self.btn_restore_backup)
        btn_backup_row.addStretch()

        backup_group_layout.addLayout(btn_backup_row)
        content_layout.addWidget(backup_group)

        # Section 2: Database Optimization Utility
        opt_group = QFrame(self)
        opt_group.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 8px;
            }
            QLabel { border: none; font-weight: bold; }
        """)
        opt_group_layout = QVBoxLayout(opt_group)
        opt_group_layout.setContentsMargins(15, 15, 15, 15)
        opt_group_layout.setSpacing(10)

        lbl_opt_title = QLabel("🛠️ Database Maintenance", opt_group)
        lbl_opt_title.setStyleSheet("font-size: 16px; color: #4B5563;")
        opt_group_layout.addWidget(lbl_opt_title)

        lbl_opt_desc = QLabel(
            "Running optimization re-indexes all SQLite tables and vacuums unused storage space "
            "to improve overall system load performance.",
            opt_group
        )
        lbl_opt_desc.setStyleSheet("font-weight: normal; color: #555555; font-size: 12px;")
        opt_group_layout.addWidget(lbl_opt_desc)

        btn_opt_row = QHBoxLayout()
        self.btn_optimize = QPushButton("Optimize Database (VACUUM)", opt_group)
        self.btn_optimize.setStyleSheet("""
            QPushButton { background-color: #4b5563; color: white; font-weight: bold; padding: 8px 16px; border-radius: 4px; }
            QPushButton:hover { background-color: #374151; }
        """)
        btn_opt_row.addWidget(self.btn_optimize)
        btn_opt_row.addStretch()

        opt_group_layout.addLayout(btn_opt_row)
        content_layout.addWidget(opt_group)

        content_layout.addStretch()
        self.layout.addLayout(content_layout)

        # Signal connection for list selection change
        self.backup_list.itemSelectionChanged.connect(self.on_selection_changed)

    def populate_backups(self, backups: List[str]) -> None:
        self.backup_list.clear()
        self.backup_list.addItems(backups)
        self.btn_restore_backup.setEnabled(False)

    def on_selection_changed(self) -> None:
        selected = self.backup_list.selectedItems()
        self.btn_restore_backup.setEnabled(len(selected) > 0)

    def get_selected_backup(self) -> Optional[str]:
        selected = self.backup_list.selectedItems()
        return selected[0].text() if selected else None

    def show_message(self, title: str, message: str) -> None:
        QMessageBox.information(self, title, message)

    def ask_confirmation(self, title: str, message: str) -> bool:
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes
