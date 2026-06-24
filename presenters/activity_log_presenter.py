"""Activity Log and Archives Presenter."""

from typing import Any, List, Dict
import logging
import csv
from PySide6.QtWidgets import QFileDialog, QMessageBox, QMenu

logger = logging.getLogger(__name__)

try:
    from models import queries
except ImportError:
    try:
        from database import queries
    except ImportError:
        queries = None

class ActivityLogPresenter:
    def __init__(self, view: Any, model: Any = None):
        self.view = view
        self.model = model or queries

        # --- Tab 1: Log Signals ---
        self.view.btn_refresh_logs.clicked.connect(self.load_logs)
        self.view.combo_filter.currentTextChanged.connect(self.load_logs)
        self.view.btn_export.clicked.connect(self.export_to_csv)
        self.current_filtered_logs = []

        # --- Tab 2: Archives Signals ---
        self.view.search_btn.clicked.connect(self.load_archived_items)
        self.view.table.itemSelectionChanged.connect(self.handle_archive_selection)
        self.view.restore_btn.clicked.connect(self.handle_restore)
        self.view.table.customContextMenuRequested.connect(self.handle_context_menu)

        # Refresh data automatically when the admin switches between the tabs
        self.view.tabs.currentChanged.connect(self.handle_tab_change)

    def start(self) -> None:
        """Triggered automatically by main_window when this panel comes into focus."""
        # Load categories for archives drop-down
        categories = self.model.get_all_categories()
        self.view.populate_categories(categories)

        # Pre-load both datasets so they are ready instantly
        self.load_logs()
        self.load_archived_items()

    def handle_tab_change(self, index):
        if index == 0:
            self.load_logs()
        elif index == 1:
            self.load_archived_items()

    # ==========================================
    # TAB 1: LOGS LOGIC
    # ==========================================
    def load_logs(self) -> None:
        current_filter = self.view.combo_filter.currentText()
        raw_logs = self._get_raw_logs()

        formatted_list = []
        self.current_filtered_logs = []

        for log in raw_logs:
            if not log:
                continue

            details = log.get("details") or log.get("message") or ""
            action_type = str(log.get("actions") or log.get("type") or "").lower()
            timestamp = log.get("action_date") or log.get("timestamp") or "0000-00-00 00:00"

            # --- FIXED: Robust filter matching that covers all action types ---
            if current_filter == "Items Registration":
                # Catches: "Created", "Status -> Active", "Status -> Claimed",
                #          "Status -> Archived", "Registered"
                if not any(x in action_type for x in ["created", "registered", "status"]):
                    continue

            elif current_filter == "Claims Processed":
                # Catches: "Claim Requested", "Claim Approved",
                #          "Claim Rejected", "Claim {anything}"
                if "claim" not in action_type:
                    continue

            elif current_filter == "System Alerts":
                # Catches: "System Alert", "Constituent" logs,
                #          backup / optimizer logs
                if not any(x in action_type for x in ["system", "alert", "constituent"]):
                    continue

            # "All Activity" — no filter applied, falls through

            # Include the action type label in the log line for clarity
            formatted_row = f"[{timestamp}] [{action_type.upper()}] {details}"
            formatted_list.append(formatted_row)

            self.current_filtered_logs.append({
                "Timestamp": timestamp,
                "Action Type": action_type.title(),
                "Details": details
            })

        if not formatted_list:
            self.view.show_logs([f"No logs found for filter: '{current_filter}'."])
        else:
            self.view.show_logs(formatted_list)

    def export_to_csv(self):
        if not self.current_filtered_logs:
            QMessageBox.warning(
                self.view,
                "Export Failed",
                "There are no logs to export. Try refreshing or changing the filter first."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self.view,
            "Export Activity Logs",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(
                        file,
                        fieldnames=["Timestamp", "Action Type", "Details"]
                    )
                    writer.writeheader()
                    writer.writerows(self.current_filtered_logs)

                QMessageBox.information(
                    self.view,
                    "Export Successful",
                    f"Logs successfully exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.view,
                    "Export Error",
                    f"Failed to save file:\n{str(e)}"
                )

    def _get_raw_logs(self) -> List[Dict[str, str]]:
        if self.model and hasattr(self.model, "get_all_activity_logs"):
            try:
                db_logs = self.model.get_all_activity_logs()
                return [dict(row) for row in db_logs] if db_logs else []
            except Exception as e:
                logger.error(f"Failed to query database logs: {e}")
        return []

    # ==========================================
    # TAB 2: ARCHIVES LOGIC
    # ==========================================
    def load_archived_items(self):
        search_text = self.view.search_input.text().strip()
        type_text = self.view.type_filter.currentText()
        item_type = type_text if type_text != "All Types" else None
        category_id = self.view.category_filter.currentData()

        items = self.model.search_archived_items(
            search_query=search_text if search_text else None,
            category_id=category_id,
            item_type=item_type
        )

        self.view.populate_table(items)
        self.view.selected_label.setText("Selected Item: None")
        self.view.restore_btn.setEnabled(False)

    def handle_archive_selection(self):
        item_id = self.view.get_selected_item_id()
        if item_id:
            self.view.selected_label.setText(f"Selected Item ID: {item_id}")
            self.view.restore_btn.setEnabled(True)
        else:
            self.view.selected_label.setText("Selected Item: None")
            self.view.restore_btn.setEnabled(False)

    def handle_restore(self):
        item_id = self.view.get_selected_item_id()
        if not item_id:
            return

        if self.view.ask_confirmation(
            "Confirm Restore",
            f"Are you sure you want to restore Item {item_id} to the Active ledger?"
        ):
            success = self.model.update_item_status(item_id, 'Active')

            if success:
                self.view.show_message(
                    "Success",
                    f"Item {item_id} has been restored to 'Active' status."
                )
                self.load_archived_items()
            else:
                self.view.show_message(
                    "Error",
                    "Failed to update item status in the database."
                )

    def handle_context_menu(self, position):
        """Draws a right-click menu over the selected archived row."""
        item_id, item_name = self.view.get_item_at_position(position)
        if not item_id:
            return

        menu = QMenu(self.view.table)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #cccccc; }
            QMenu::item { padding: 8px 25px; color: #b81417; font-weight: bold; }
            QMenu::item:selected { background-color: #f0f0f0; }
        """)

        delete_action = menu.addAction(f"Permanently Purge '{item_name}'")
        action = menu.exec(self.view.table.viewport().mapToGlobal(position))

        if action == delete_action:
            self.handle_purge(item_id, item_name)

    def handle_purge(self, item_id, item_name):
        """Permanently deletes the item after confirmation."""
        message = (
            f"Are you sure you want to PERMANENTLY delete '{item_name}'?\n\n"
            "WARNING: This will completely erase the item, its claim history, "
            "and its activity logs from the database. This cannot be undone."
        )

        if self.view.ask_confirmation("Confirm Permanent Purge", message):
            success = self.model.purge_archived_item(item_id)

            if success:
                self.view.show_message(
                    "Success",
                    f"'{item_name}' and all associated history have been wiped from the database."
                )
                self.load_archived_items()
            else:
                self.view.show_message(
                    "Database Error",
                    "Failed to permanently purge the item."
                )