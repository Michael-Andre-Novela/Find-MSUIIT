"""Items management presenter."""

from typing import Any
from models import queries

class ItemsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect UI Events to Functions
        self.view.search_btn.clicked.connect(self.load_items)
<<<<<<< Updated upstream
        self.view.table.itemSelectionChanged.connect(self.handle_selection)
        self.view.update_btn.clicked.connect(self.handle_update)
=======
        self.view.table.customContextMenuRequested.connect(self.handle_context_menu)
        self.view.add_category_btn.clicked.connect(self.handle_add_category)
        self.view.delete_category_btn.clicked.connect(self.handle_delete_category)
        
        # Connect doubleClick signal to view detailed item dialog
        self.view.table.doubleClicked.connect(self.handle_double_click)
>>>>>>> Stashed changes

    def start(self):
        """Initializes the view with category data and loads all active items."""
        categories = self.model.get_all_categories()
        self.view.populate_categories(categories)
        self.load_items()

    def load_items(self):
        """Fetches items from the database based on the active filters."""
        search_text = self.view.search_input.text().strip()
        
        # Handle the dropdowns (convert "All" to None for the database query)
        type_text = self.view.type_filter.currentText()
        item_type = type_text if type_text != "All Types" else None
        
        category_id = self.view.category_filter.currentData()

        # Fetch data using your existing query
        items = self.model.search_active_items(
            search_query=search_text if search_text else None,
            category_id=category_id,
            item_type=item_type
        )
        
        # Push data to the UI table
        self.view.populate_table(items)
        
        # Reset the action bar at the bottom
        self.view.selected_label.setText("Selected Item: None")
        self.view.status_combo.setEnabled(False)
        self.view.update_btn.setEnabled(False)

    def handle_selection(self):
        """Triggers when a user clicks a row. Enables the Update controls."""
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
        """Updates the status of the selected item in the database."""
        item_id = self.view.get_selected_item_id()
        new_status = self.view.status_combo.currentText()
        
        if item_id and new_status:
            success = self.model.update_item_status(item_id, new_status)
            if success:
                self.view.show_message("Success", f"Item {item_id} successfully marked as {new_status}.")
                # Refresh the table immediately. 
                # Since the item is no longer 'Active', it will disappear from the list!
                self.load_items() 
            else:
<<<<<<< Updated upstream
                self.view.show_message("Error", "Failed to update item status in the database.")
=======
                self.view.show_message("Error", f"Failed to archive item:\n{msg}")

    def handle_edit(self, item_id):
        item_data = self.model.get_item_by_id(item_id)
        if not item_data:
            self.view.show_message("Error", "Could not fetch item details from the database.")
            return

        categories = self.model.get_all_categories()
        dialog = EditItemDialog(self.view, categories)
        dialog.load_data(item_data)

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
                location=new_data["location"],
                photo_filepath=new_data.get("photo_filepath")
            )
            
            if success:
                self.view.show_message("Success", "Item details successfully updated!")
                self.load_items()
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

    def handle_add_category(self):
        dialog = AddCategoryDialog(self.view)
        
        if dialog.exec():
            data = dialog.get_data()
            
            if not data["name"]:
                self.view.show_message("Validation Error", "Category Name cannot be empty.")
                return
                
            result = self.model.add_category(data["name"])
            
            if result == True:
                self.view.show_message("Success", f"Category '{data['name']}' was successfully added to the system!")
                categories = self.model.get_all_categories()
                self.view.populate_categories(categories)
            elif result == "duplicate":
                self.view.show_message("Error", f"The category '{data['name']}' already exists.")
            else:
                self.view.show_message("Database Error", "Failed to save the new category.")

    def handle_delete_category(self):
        """Attempts to delete the currently selected category in the dropdown filter."""
        category_id = self.view.category_filter.currentData()
        category_name = self.view.category_filter.currentText()

        # If they left it on "All Categories", they haven't selected a specific one to delete
        if not category_id:
            self.view.show_message("Selection Error", "Please select a specific category from the dropdown to delete. ('All Categories' cannot be deleted).")
            return

        if self.view.ask_confirmation("Confirm Category Deletion", f"Are you sure you want to completely delete the '{category_name}' category?\n\nThis will only work if no items are currently using it."):
            
            result = self.model.delete_category(category_id)
            
            if result == True:
                self.view.show_message("Success", f"Category '{category_name}' has been deleted.")
                # Refresh the dropdown menus so the category disappears
                categories = self.model.get_all_categories()
                self.view.populate_categories(categories)
                self.load_items()
                
            elif result == "restricted":
                self.view.show_message("Deletion Blocked", f"Cannot delete '{category_name}'.\n\nThere are still items tied to this category. You must move or delete those items first.")
            elif result == "system_protected":
                self.view.show_message("Deletion Blocked", "The default 'System Unassigned' category is protected and cannot be deleted.")
            else:
                self.view.show_message("Database Error", "Failed to delete the category.")
>>>>>>> Stashed changes
