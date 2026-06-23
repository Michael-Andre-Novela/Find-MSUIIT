"""Maintenance presenter controlling database backups, restores, and optimization."""

import os
import shutil
from datetime import datetime
from typing import Any
from models.connection import DB_DIR, DB_PATH
from models import queries
from modules.logger import get_logger

log = get_logger(__name__)

class MaintenancePresenter:
    def __init__(self, view: Any, model: Any = None):
        self.view = view
        self.model = model or queries
        self.backup_dir = os.path.join(DB_DIR, "backups")

        # Connect UI signals to presenter slots
        self.view.btn_create_backup.clicked.connect(self.handle_create_backup)
        self.view.btn_restore_backup.clicked.connect(self.handle_restore_backup)
        self.view.btn_optimize.clicked.connect(self.handle_optimize)

    def start(self) -> None:
        self.load_backups()

    def load_backups(self) -> None:
        """Scan backup directory and populate QListWidget with existing backups."""
        if not os.path.exists(self.backup_dir):
            try:
                os.makedirs(self.backup_dir, exist_ok=True)
            except Exception as e:
                log.error(f"Failed to create backups directory: {e}")
                self.view.populate_backups([])
                return

        try:
            files = [
                f for f in os.listdir(self.backup_dir)
                if f.endswith(".bak") or f.endswith(".db")
            ]
            # Sort backups descending (newest first)
            files.sort(reverse=True)
            self.view.populate_backups(files)
        except Exception as e:
            log.error(f"Failed to scan backups directory: {e}")
            self.view.populate_backups([])

    def handle_create_backup(self) -> None:
        """Create a new timestamped backup of the current database file."""
        if not os.path.exists(DB_PATH):
            self.view.show_message("Error", "Core database file not found. Cannot perform backup.")
            return

        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup_filename = f"find_iit.db.{timestamp}.bak"
            dest_path = os.path.join(self.backup_dir, backup_filename)

            shutil.copy2(DB_PATH, dest_path)
            
            # Log backup creation in database activity logs
            self.model.add_activity_log(
                item_id=0,
                details=f"Database backup created: {backup_filename}",
                actions="System Alert"
            )
            
            self.view.show_message("Backup Created", f"Successfully backed up database to:\n{backup_filename}")
            self.load_backups()
        except Exception as e:
            log.error(f"Failed to create backup: {e}")
            self.view.show_message("Error", f"Failed to create database backup:\n{e}")

    def handle_restore_backup(self) -> None:
        """Restore database from a selected backup file after confirmation."""
        selected_file = self.view.get_selected_backup()
        if not selected_file:
            self.view.show_message("No Selection", "Please select a backup file to restore.")
            return

        confirm = self.view.ask_confirmation(
            "Confirm Restore",
            f"Are you sure you want to restore the database to state:\n'{selected_file}'?\n\n"
            "This will overwrite the current database. All active changes since this backup was made will be lost."
        )
        if not confirm:
            return

        src_path = os.path.join(self.backup_dir, selected_file)
        if not os.path.exists(src_path):
            self.view.show_message("Error", "Selected backup file no longer exists on disk.")
            self.load_backups()
            return

        try:
            # Overwrite the active database file with the backup copy
            shutil.copy2(src_path, DB_PATH)
            
            # Add activity log to the restored database
            self.model.add_activity_log(
                item_id=0,
                details=f"Database restored from backup: {selected_file}",
                actions="System Alert"
            )
            
            self.view.show_message("Database Restored", "System database successfully restored! Please navigate to other tabs to reload data.")
            self.load_backups()
        except Exception as e:
            log.error(f"Failed to restore database: {e}")
            self.view.show_message("Error", f"Failed to restore database from backup:\n{e}")

    def handle_optimize(self) -> None:
        """Runs optimization (VACUUM) on the active SQLite database."""
        self.view.btn_optimize.setEnabled(False)
        try:
            success = self.model.optimize_database()
            if success:
                self.view.show_message("Optimization Complete", "Database optimized successfully (VACUUM ran successfully).")
            else:
                self.view.show_message("Optimization Failed", "Could not complete database optimization.")
        except Exception as e:
            log.error(f"Database optimization error: {e}")
            self.view.show_message("Error", f"An error occurred during database optimization:\n{e}")
        finally:
            self.view.btn_optimize.setEnabled(True)
