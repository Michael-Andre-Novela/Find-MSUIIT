"""Items management presenter."""

from typing import Any
from PySide6.QtWidgets import QMenu
from models import queries
# Import the new dialog window we just made
from views.items_view import EditItemDialog 

class ItemsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        self.view.search_btn.clicked.connect(self.load_items)
        self.view.table.itemSelectionChanged.connect(self.handle_selection)
        self.view.update_btn.clicked.connect(self.handle_update)
        self.view.table.customContextMenuRequested.connect(self.handle_context_menu)

    def start(self):
        categories = self.model.get_all_categories()
        self.view.populate_categories(categories)
        self.load_items()

    def load_items(self):
        search_text = self.view.search_input.text().strip()
        type_text = self.view.type_filter.currentText()
        item_type = type_text if type_text != "All Types" else None
        category_id = self.view.category_filter.currentData()

        items = self.model.search_active_items(
            search_query=search_text if search_text else None,
            category_id=category_id,
            item_type=item_type
        )
        
        self.view.populate_table(items)
        self.view.selected_label.setText("Selected Item: None")
        self.view.status_combo.setEnabled(False)
        self.view.update_btn.setEnabled(False)

    def handle_selection(self):
        item_id = self.view.get_selected_item_id()
        if item_id:
            self.view.selected_label.setText(f"Selected Item ID: {item_id}")
            self.view.status_combo.setEnabled(True)
            self.view.update_btn.setEnabled(True)
        else:
            self.view.selected_label.setText("Selected Item: None")
            self.view.status_combo.setEnabled(False)
            self.view.update_btn.setEnabled(False)

    def handle_update(self):
        item_id = self.view.get_selected_item_id()
        new_status = self.view.status_combo.currentText()
        
        if item_id and new_status:
            success = self.model.update_item_status(item_id, new_status)
            if success:
                self.view.show_message("Success", f"Item {item_id} successfully marked as {new_status}.")
                self.load_items() 
            else:
                self.view.show_message("Error", "Failed to update item status in the database.")

    def handle_context_menu(self, position):
        item_id, item_name = self.view.get_item_at_position(position)
        if not item_id: return

        menu = QMenu(self.view.table)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #cccccc; }
            QMenu::item { padding: 8px 25px; color: #333; font-weight: bold; }
            QMenu::item:selected { background-color: #f0f0f0; }
        """)
        
        # Add the two actions to the pop-up menu
        edit_action = menu.addAction(f"Edit '{item_name}'")
        menu.addSeparator() # Visual line between actions
        delete_action = menu.addAction(f"Delete '{item_name}'")
        
        # Display the menu where the mouse clicked
        action = menu.exec(self.view.table.viewport().mapToGlobal(position))

        if action == delete_action:
            self.handle_delete(item_id, item_name)
        elif action == edit_action:
            self.handle_edit(item_id)

    def handle_edit(self, item_id):
        """Pops up the edit window and processes the changes."""
        # 1. Fetch current data
        item_data = self.model.get_item_by_id(item_id)
        if not item_data:
            self.view.show_message("Error", "Could not fetch item details from the database.")
            return

        # 2. Build and launch the dialog
        categories = self.model.get_all_categories()
        dialog = EditItemDialog(self.view, categories)
        dialog.load_data(item_data)

        # 3. If they clicked 'Save'
        if dialog.exec():
            new_data = dialog.get_data()
            
            if not new_data["name"] or not new_data["location"]:
                self.view.show_message("Validation Error", "Item Name and Location cannot be empty.")
                return
                
            success = self.model.update_item_details(
                item_id=item_id,
                name=new_data["name"],
                description=new_data["description"],
                item_type=new_data["type"],
                category_id=new_data["category_id"],
                location=new_data["location"]
            )
            
            if success:
                self.view.show_message("Success", "Item details successfully updated!")
                self.load_items() # Refresh the table to show the changes
            else:
                self.view.show_message("Database Error", "Failed to save the updated item details.")

    def handle_delete(self, item_id, item_name):
        if self.view.ask_confirmation("Confirm Deletion", f"Are you sure you want to permanently delete '{item_name}'?\n\nThis action cannot be undone."):
            result = self.model.delete_item_record(item_id)
            if result == True:
                self.view.show_message("Success", f"'{item_name}' has been deleted.")
                self.load_items()
            elif result == "restricted":
                self.view.show_message("Deletion Blocked", f"Cannot delete '{item_name}'.\n\nThis item is currently tied to a claim request.")
            else:
                self.view.show_message("Error", "A database error occurred.")