"""Constituents presenter."""

from typing import Any
from models import queries
import re

class ConstituentsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect UI Events to Functions
        self.view.submit_btn.clicked.connect(self.handle_submit)
        self.view.update_btn.clicked.connect(self.handle_update)
        self.view.delete_btn.clicked.connect(self.handle_delete)
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

    def _validate_form(self, data, require_id=True):
        """
        Shared validator for both submit and update.
        Returns an error message string if invalid, or None if valid.
        """
        if require_id and not data["id_number"]:
            return "ID Number is required."

        if not data["name"] or not data["email"]:
            return "Name and Email are required."

        # School ID format: YYYY-NNNN
        if require_id:
            id_pattern = re.compile(r"^\d{4}-\d{4}$")
            if not id_pattern.match(data["id_number"]):
                return "ID Number must follow the format YYYY-NNNN (e.g., 2026-0001)."

        # Name: letters, spaces, dots, hyphens only
        name_pattern = re.compile(r"^[A-Za-z\s\.\-]+$")
        if not name_pattern.match(data["name"]):
            return "Full Name must only contain letters, spaces, dots, or hyphens."

        # Email: standard format
        email_pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        if not email_pattern.match(data["email"]):
            return "Please enter a valid Email Address (e.g., juan@g.msuiit.edu.ph)."

        # Phone: optional, but if provided must be 11 digits starting with 09
        if data["phone"]:
            phone_pattern = re.compile(r"^09\d{9}$")
            if not phone_pattern.match(data["phone"]):
                return "Contact Phone must be 11 digits starting with 09 (e.g., 09171234567)."

        return None

    def handle_submit(self):
        """Registers a completely new constituent."""
        data = self.view.get_form_data()

        error = self._validate_form(data, require_id=True)
        if error:
            self.view.show_message("Validation Error", error)
            return

        import re

        # 2. Strict School ID Format Check (e.g., 2024-1234)
        id_pattern = re.compile(r"^\d{4}-\d{4}$")
        if not id_pattern.match(data["id_number"]):
            self.view.show_message("Validation Error", "ID Number must follow the format YYYY-NNNN (e.g., 2026-0001).")
            return
            
        result = self.model.add_constituent(
            id_number=data["id_number"], name=data["name"], 
            contact_email=data["email"], contact_phone=data["phone"]
        )
            
        if result:
            self.view.show_message("Success", "Constituent registered successfully!")
            self.view.clear_form()
            self.load_directory()
        else:
            self.view.show_message("Error", "Failed to register constituent.")

    def handle_update(self):
        """Saves changes to an existing constituent."""
        if not self.view.hidden_constituent_id:
            return
            
        data = self.view.get_form_data()

        # ID not required for update since it's already stored
        error = self._validate_form(data, require_id=False)
        if error:
            self.view.show_message("Validation Error", error)
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
            self.load_directory()
        else:
            self.view.show_message("Error", "Failed to update database.")

    def handle_delete(self):
        """Attempts to delete the selected constituent from the database."""
        if not self.view.hidden_constituent_id:
            return
            
        name = self.view.name_input.text()
        
        if self.view.ask_confirmation("Confirm Deletion", f"Are you sure you want to permanently delete {name} from the system?"):
            result = self.model.remove_constituent_record(self.view.hidden_constituent_id)
            
            if result == True:
                self.view.show_message("Success", f"{name} has been removed from the database.")
                self.view.clear_form()
                self.load_directory()
                
            elif result == "restricted":
                self.view.show_message(
                    "Deletion Blocked", 
                    f"Cannot delete {name}.\n\nThis constituent is currently tied to a Lost Item, Found Item, or Pending Claim. "
                    "You must resolve or remove their items before their profile can be deleted."
                )
                
            else:
                self.view.show_message("Error", "Failed to delete the constituent due to a database error.")