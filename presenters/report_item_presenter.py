"""Report item presenter."""

from typing import Any
from models import queries
from modules.matching import find_matches_for_item

class ReportItemPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect button clicks to functions
        self.view.submit_btn.clicked.connect(self.handle_submit)
        self.view.clear_btn.clicked.connect(self.view.clear_form)

    def start(self):
        """Called to initialize the view with data (like categories)."""
        categories = self.model.get_all_categories()
        self.view.populate_categories(categories)

    def handle_submit(self):
        data = self.view.get_form_data()
        
        # 1. Basic Validation
        if not data["name"] or not data["reporter_id"] or not data["date"] or not data["location"]:
            self.view.show_message("Validation Error", "Please fill in Name, Reporter ID, Location, and Date.")
            return

        # 2. Strict Reporter ID Regular Expression Check
        import re
        pattern = re.compile(r"^\d{4}-\d{4}$")
        if not pattern.match(data["reporter_id"]):
            self.view.show_message(
                "Validation Error", 
                "Reporter ID must follow the format YYYY-NNNN (e.g., 2024-1234)."
            )
            return
        # 3. Verify Constituent exists in the database
        constituent = self.model.get_constituent_by_school_id(data["reporter_id"])
        if not constituent:
            self.view.show_message(
                "Error", 
                f"Reporter ID '{data['reporter_id']}' not found.\n\nPlease register them in the Constituents tab first."
            )
            return
            
        c_id = constituent["constituent_id"]

        # 4. Duplicate Detection (Warning before saving)
        categories = self.model.get_all_categories()
        category_name = next((c["category_name"] for c in categories if c["category_id"] == data["category_id"]), "")
        
        target_item = {
            "name": data["name"],
            "description": data["description"],
            "category_name": category_name
        }

        # Check for similar active items of the same type (duplicate threshold 0.65)
        same_type_items = self.model.search_active_items(item_type=data["type"])
        duplicates = find_matches_for_item(target_item, same_type_items, threshold=0.65)

        if duplicates:
            duplicate_list = "\n".join([f"- {item['name']} (ID: {item['item_id']}, Category: {item['category_name']})" for item in duplicates[:3]])
            if len(duplicates) > 3:
                duplicate_list += "\n...and others."
            
            confirm = self.view.ask_confirmation(
                "Potential Duplicate Detected",
                f"The system detected the following similar active '{data['type']}' items:\n\n"
                f"{duplicate_list}\n\n"
                f"Do you still wish to submit this report?"
            )
            if not confirm:
                return # Abort submission
        
        # 5. Submit to Database
        photo_path = data["photo_filepath"] if data["photo_filepath"] else None
        if data["type"] == "Lost":
            success, payload = self.model.report_lost_item(
                name=data["name"], description=data["description"], 
                category_id=data["category_id"], priority_level=data["priority"], 
                constituent_id=c_id, date_lost=data["date"], location_lost=data["location"],
                photo_filepath=photo_path
            )
        else:
            success, payload = self.model.report_found_item(
                name=data["name"], description=data["description"], 
                category_id=data["category_id"], priority_level=data["priority"], 
                constituent_id=c_id, date_found=data["date"], location_found=data["location"],
                photo_filepath=photo_path
            )

        # 6. Handle Result
        if success:
            self.view.show_message("Success", f"Item successfully reported!\nSystem Item ID: {payload}")
            self.view.clear_form()
        else:
            self.view.show_message("Error", payload or "Failed to report item to the database.")