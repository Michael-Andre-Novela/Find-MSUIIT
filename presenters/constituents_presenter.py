"""Constituents presenter."""

from typing import Any
from models import queries

class ConstituentsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect button clicks to functions
        self.view.submit_btn.clicked.connect(self.handle_submit)
        self.view.clear_btn.clicked.connect(self.view.clear_form)

    def start(self):
        # We don't have dropdowns to populate here, but we keep 
        # start() for MVP architectural consistency.
        pass 

    def handle_submit(self):
        data = self.view.get_form_data()
        
        # 1. Basic Validation (Phone is optional, so we don't check it here)
        if not data["id_number"] or not data["name"] or not data["email"]:
            self.view.show_message("Validation Error", "Please fill in the ID Number, Full Name, and Email Address.")
            return

        # 2. Check for Duplicate ID
        # We ask the database if this school ID already exists.
        existing_person = self.model.get_constituent_by_school_id(data["id_number"])
        if existing_person:
            self.view.show_message(
                "Duplicate Error", 
                f"ID '{data['id_number']}' is already registered to {existing_person['name']}."
            )
            return
            
        # 3. Submit to Database
        result_id = self.model.add_constituent(
            id_number=data["id_number"], 
            name=data["name"], 
            contact_email=data["email"], 
            contact_phone=data["phone"]
        )
            
        # 4. Handle Result
        if result_id:
            self.view.show_message("Success", f"Constituent '{data['name']}' has been registered successfully!")
            self.view.clear_form()
        else:
            self.view.show_message("Database Error", "Failed to register constituent. Check database connection.")