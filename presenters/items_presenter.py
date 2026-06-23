"""Items management presenter."""

from typing import Any
from PySide6.QtWidgets import QMenu
from models import queries
from views.items_view import EditItemDialog, AddCategoryDialog 
from views.matches_dialog import MatchesDialog
from modules.matching import find_matches_for_item

class ItemsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        self.view.search_btn.clicked.connect(self.load_items)
        self.view.table.customContextMenuRequested.connect(self.handle_context_menu)
        self.view.add_category_btn.clicked.connect(self.handle_add_category)

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

    def handle_context_menu(self, position):
        item_id, item_name = self.view.get_item_at_position(position)
        if not item_id: return

        menu = QMenu(self.view.table)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #cccccc; }
            QMenu::item { padding: 8px 25px; color: #333; font-weight: bold; }
            QMenu::item:selected { background-color: #f0f0f0; }
        """)
        
        match_action = menu.addAction(f"Find Matches for '{item_name}'")
        menu.addSeparator()
        edit_action = menu.addAction(f"Edit '{item_name}'")
        archive_action = menu.addAction(f"Archive '{item_name}'") # Added to context menu
        menu.addSeparator() 
        delete_action = menu.addAction(f"Delete '{item_name}'")
        
        action = menu.exec(self.view.table.viewport().mapToGlobal(position))

        if action == delete_action:
            self.handle_delete(item_id, item_name)
        elif action == edit_action:
            self.handle_edit(item_id)
        elif action == archive_action:
            self.handle_archive(item_id, item_name) # Triggers the new archive method
        elif action == match_action:
            self.handle_find_matches(item_id)

    def handle_find_matches(self, item_id):
        item_details = self.model.get_item_details(item_id, None)
        if not item_details:
            self.view.show_message("Error", "Could not retrieve item details.")
            return

        opposite_type = "Found" if item_details["type"] == "Lost" else "Lost"
        candidates = self.model.search_active_items(item_type=opposite_type)
        matches = find_matches_for_item(item_details, candidates)

        dialog = MatchesDialog(self.view, item_details)
        dialog.populate_matches(matches)

        if dialog.exec():
            selected = dialog.get_selected_match()
            if selected:
                # Resolve claimant and found item ID for claim routing
                if item_details["type"] == "Lost":
                    claimant_id = item_details.get("constituent_id_number")
                    found_item_id = selected["item_id"]
                else:
                    match_details = self.model.get_item_details(selected["item_id"], "Lost")
                    claimant_id = match_details.get("constituent_id_number") if match_details else ""
                    found_item_id = item_details["item_id"]

                # Get MainWindow and route to Claims view
                main_window = self.view.window()
                try:
                    claims_view = main_window.get_view("claims")
                    claims_view.item_id_input.setText(str(found_item_id))
                    claims_view.constituent_input.setText(str(claimant_id))
                    main_window.show_view("claims")
                except Exception as e:
                    self.view.show_message("Routing Error", f"Failed to open claims view: {e}")

    def handle_archive(self, item_id, item_name):
        """Archives the selected item after confirmation."""
        if self.view.ask_confirmation("Confirm Archive", f"Are you sure you want to archive '{item_name}'?\n\nIt will be moved to the Historical Archives."):
            
            # Unpack the tuple correctly to avoid silent errors
            success, msg = self.model.update_item_status(item_id, "Archived")
            
            if success:
                self.view.show_message("Success", f"'{item_name}' has been successfully archived.")
                self.load_items() 
            else:
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
                location=new_data["location"]
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
                
            result = self.model.add_category(data["name"], data["description"])
            
            if result == True:
                self.view.show_message("Success", f"Category '{data['name']}' was successfully added to the system!")
                categories = self.model.get_all_categories()
                self.view.populate_categories(categories)
            elif result == "duplicate":
                self.view.show_message("Error", f"The category '{data['name']}' already exists.")
            else:
                self.view.show_message("Database Error", "Failed to save the new category.")
