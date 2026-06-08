"""Constituents presenter."""

from typing import Any
from models import queries

class ConstituentsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect UI Events to Functions
        self.view.submit_btn.clicked.connect(self.handle_submit)
        self.view.update_btn.clicked.connect(self.handle_update)
        self.view.delete_btn.clicked.connect(self.handle_delete) # Wire the Delete button
        self.view.clear_btn.clicked.connect(self.view.clear_form)
        self.view.search_btn.clicked.connect(self.load_directory)
        
        # Trigger edit mode when a row in the table is clicked
        self.view.table.cellClicked.connect(self.view.populate_form_for_edit)

    def start(self):
        """Initializes the view by loading the existing constituents."""
        self.load_directory()

    def load_directory(self):
        """Fetches constituents based on the search bar."""
        search_term = self.view.search_input.text().strip()
        data = self.model.search_constituents(search_term)
        self.view.populate_table(data)

    def handle_submit(self):
        """Registers a completely new constituent."""
        data = self.view.get_form_data()
        
        if not data["id_number"] or not data["name"] or not data["email"]:
            self.view.show_message("Validation Error", "ID Number, Name, and Email are required.")
            return

        existing = self.model.get_constituent_by_school_id(data["id_number"])
        if existing:
            self.view.show_message("Duplicate Error", f"ID '{data['id_number']}' is already registered.")
            return
            
        result = self.model.add_constituent(
            id_number=data["id_number"], name=data["name"], 
            contact_email=data["email"], contact_phone=data["phone"]
        )
            
        if result:
            self.view.show_message("Success", "Constituent registered successfully!")
            self.view.clear_form()
            self.load_directory() # Instantly update the table
        else:
            self.view.show_message("Error", "Failed to register constituent.")

    def handle_update(self):
        """Saves changes to an existing constituent."""
        if not self.view.hidden_constituent_id:
            return
            
        data = self.view.get_form_data()
        
        if not data["name"] or not data["email"]:
            self.view.show_message("Validation Error", "Name and Email cannot be empty.")
            return
            
        success = self.model.update_constituent_info(
            constituent_id=self.view.hidden_constituent_id,
            name=data["name"],
            email=data["email"],
            phone=data["phone"]
        )
        
        if success:
            self.view.show_message("Success", "Constituent information updated successfully!")
            self.view.clear_form()
            self.load_directory() # Instantly update the table
        else:
            self.view.show_message("Error", "Failed to update database.")

    def handle_delete(self):
        """Attempts to delete the selected constituent from the database."""
        if not self.view.hidden_constituent_id:
            return
            
        name = self.view.name_input.text()
        
        # 1. Ask for confirmation before deleting
        if self.view.ask_confirmation("Confirm Deletion", f"Are you sure you want to permanently delete {name} from the system?"):
            
            # 2. Proceed with database deletion
            result = self.model.remove_constituent_record(self.view.hidden_constituent_id)
            
            if result == True:
                self.view.show_message("Success", f"{name} has been removed from the database.")
                self.view.clear_form()
                self.load_directory()
                
            elif result == "restricted":
                # Handles the SQLite ON DELETE RESTRICT constraint
                self.view.show_message(
                    "Deletion Blocked", 
                    f"Cannot delete {name}.\n\nThis constituent is currently tied to a Lost Item, Found Item, or Pending Claim. "
                    "You must resolve or remove their items before their profile can be deleted."
                )
                
            else:
                self.view.show_message("Error", "Failed to delete the constituent due to a database error.")