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
        title.setObjectName("viewTitle")
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # Content layout
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 15, 20, 15)
        content_layout.setSpacing(15)

        # Section 1: Backup & Restore Manager
        backup_group = QFrame(self)
        backup_group.setObjectName("cardGroup")
        backup_group_layout = QVBoxLayout(backup_group)
        backup_group_layout.setContentsMargins(15, 15, 15, 15)
        backup_group_layout.setSpacing(10)

        lbl_backup_title = QLabel("📦 Database Backup & Restore Manager", backup_group)
        lbl_backup_title.setObjectName("sectionLabel")
        lbl_backup_title.setStyleSheet("font-size: 16px;")
        backup_group_layout.addWidget(lbl_backup_title)

        lbl_backup_desc = QLabel(
            "Create full backups of the current system database or select an "
            "existing backup file to restore the database to a previous state.",
            backup_group
        )
        lbl_backup_desc.setStyleSheet("font-size: 12px;")
        backup_group_layout.addWidget(lbl_backup_desc)

        # List widget for backups
        self.backup_list = QListWidget(backup_group)
      
        self.backup_list.setMinimumHeight(150)
        backup_group_layout.addWidget(self.backup_list)

        # Button Row for Backups
        btn_backup_row = QHBoxLayout()
        
        self.btn_create_backup = QPushButton("Create New Backup", backup_group)
        self.btn_create_backup.setObjectName("btnSubmit")
        self.btn_create_backup.setObjectName("btnCreate")

        self.btn_restore_backup = QPushButton("Restore Selected Backup", backup_group)
        self.btn_restore_backup.setEnabled(False)
        self.btn_restore_backup.setObjectName("btnRestore")
        btn_backup_row.addWidget(self.btn_create_backup)
        btn_backup_row.addWidget(self.btn_restore_backup)
        btn_backup_row.addStretch()

        backup_group_layout.addLayout(btn_backup_row)
        content_layout.addWidget(backup_group)

        # Section 2: Database Optimization Utility
        opt_group = QFrame(self)
        opt_group.setObjectName("cardGroup")
        opt_group_layout = QVBoxLayout(opt_group)
        opt_group_layout.setContentsMargins(15, 15, 15, 15)
        opt_group_layout.setSpacing(10)

        lbl_opt_title = QLabel("🛠️ Database Maintenance", opt_group)
        lbl_opt_title.setObjectName("sectionLabel")
        lbl_opt_title.setStyleSheet("font-size: 16px;")
        opt_group_layout.addWidget(lbl_opt_title)

        lbl_opt_desc = QLabel(
            "Running optimization re-indexes all SQLite tables and vacuums unused storage space "
            "to improve overall system load performance.",
            opt_group
        )
        lbl_opt_desc.setStyleSheet("font-size: 12px;")
        opt_group_layout.addWidget(lbl_opt_desc)

        btn_opt_row = QHBoxLayout()
        self.btn_optimize = QPushButton("Optimize Database (VACUUM)", opt_group)
        self.btn_optimize.setObjectName("btnSecondary")
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
