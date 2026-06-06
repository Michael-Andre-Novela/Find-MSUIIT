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
        
        # 1. Basic Empty Validation (Check required fields)
        if not data["id_number"] or not data["name"] or not data["email"]:
            self.view.show_message("Validation Error", "Please fill in all required fields: ID Number, Full Name, and Email Address.")
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
            contact_email=data["email"], 
            contact_phone=data["phone"]
        )
            
        # 8. Handle Result Success
        if result_id:
            self.view.show_message("Success", f"Constituent '{data['name']}' has been registered successfully!")
            self.view.clear_form()