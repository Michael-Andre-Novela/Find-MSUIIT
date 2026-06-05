"""Items management presenter."""

from typing import Any
from models import queries

class ItemsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect UI Events to Functions
        self.view.search_btn.clicked.connect(self.load_items)
        self.view.table.itemSelectionChanged.connect(self.handle_selection)
        self.view.update_btn.clicked.connect(self.handle_update)

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
                self.view.show_message("Error", "Failed to update item status in the database.")