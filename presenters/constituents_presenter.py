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
        
        # 1. Basic Empty Validation (Check required fields)
        if not data["id_number"] or not data["name"] or not data["email"]:
            self.view.show_message("Validation Error", "ID Number, Name, and Email are required.")
            return

        import re

        # 2. Strict School ID Format Check (e.g., 2024-1234)
        id_pattern = re.compile(r"^\d{4}-\d{4}$")
        if not id_pattern.match(data["id_number"]):
            self.view.show_message("Validation Error", "ID Number must follow the format YYYY-NNNN (e.g., 2026-0001).")
            return
            
        # 3. Strict Name Format Check (Only letters, spaces, dots, and hyphens)
        name_pattern = re.compile(r"^[A-Za-z\s\.\-]+$")
        if not name_pattern.match(data["name"]):
            self.view.show_message("Validation Error", "Full Name must only contain letters and spaces (e.g., Michael Khan).")
            return

        # 4. Strict Email Format Check (Standard email validations matching placeholders)
        email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_pattern.match(data["email"]):
            self.view.show_message("Validation Error", "Please enter a valid Email Address ending in @msuiit.edu.ph (e.g., sammy@msuiit.edu.ph).")
            return
            
        # 5. Strict Optional Phone Format Check (If provided, must be exactly 11 digits starting with 09)
        if data["phone"]:  # Only check if the text box isn't empty
            phone_pattern = re.compile(r"^09\d{9}$")
            if not phone_pattern.match(data["phone"]):
                self.view.show_message("Validation Error", "Contact Phone must be an 11-digit mobile number starting with 09 (e.g., 09171234567).")
                return

        # 6. Check for Duplicate ID in Database
        existing_person = self.model.get_constituent_by_school_id(data["id_number"])
        if existing_person:
            self.view.show_message(
                "Duplicate Error", 
                f"ID '{data['id_number']}' is already registered to {existing_person['name']}."
            )
            return
            
        # 7. Submit to Database
        result_id = self.model.add_constituent(
            id_number=data["id_number"], 
            name=data["name"],
            email=data["email"],
            phone=data["phone"]
        )
        
        # 8. Handle Result Success
        if result_id:
            self.view.show_message("Success", f"Constituent '{data['name']}' has been registered successfully!")
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