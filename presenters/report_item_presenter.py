"""Report item presenter."""

from typing import Any
from models import queries
from modules.matching import find_matches_for_item
from modules.logger import get_logger

log = get_logger(__name__)
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
        """Processes a new item report with optional image attachment."""
        data = self.view.get_form_data()
        
        if not data["name"] or not data["reporter_id"] or not data["date"] or not data["location"]:
            self.view.show_message("Validation Error", "Please fill in Name, Reporter ID, Location, and Date.")
            return

        import re
        pattern = re.compile(r"^\d{4}-\d{4}$")
        if not pattern.match(data["reporter_id"]):
            self.view.show_message(
                "Validation Error", 
                "Reporter ID must follow the format YYYY-NNNN (e.g., 2024-1234)."
            )
            return
        
        constituent = self.model.get_constituent_by_school_id(data["reporter_id"])
        if not constituent:
            self.view.show_message(
                "Error", 
                f"Reporter ID '{data['reporter_id']}' not found.\n\nPlease register them in the Constituents tab first."
            )
            return
            
        c_id = constituent["constituent_id"]
        
        # ===== IMAGE HANDLING =====
        photo_filepath = data.get("photo_filepath", "").strip()
        
        if photo_filepath:
            import os
            import shutil
            
            if not os.path.exists(photo_filepath):
                self.view.show_message(
                    "File Not Found",
                    f"Image file not found: {photo_filepath}\n\nProceeding without image."
                )
                photo_filepath = None
            else:
                # Copy image to a safe assets folder
                assets_dir = "assets/item_photos"
                os.makedirs(assets_dir, exist_ok=True)
                
                # Generate unique filename based on timestamp
                import time
                ext = os.path.splitext(photo_filepath)[1]
                filename = f"item_{int(time.time())}{ext}"
                dest_path = os.path.join(assets_dir, filename)
                
                try:
                    shutil.copy(photo_filepath, dest_path)
                    photo_filepath = dest_path  # Store the copied path
                    log.info(f"Image copied to {dest_path}")
                except Exception as e:
                    log.error(f"Failed to copy image: {e}")
                    self.view.show_message(
                        "Image Error",
                        f"Failed to save image: {e}\n\nProceeding without image."
                    )
                    photo_filepath = None
        
        # ===== SUBMIT TO DATABASE =====
        if data["type"] == "Lost":
            success, payload = self.model.report_lost_item(
                name=data["name"], 
                description=data["description"], 
                category_id=data["category_id"], 
                priority_level=data["priority"], 
                constituent_id=c_id, 
                date_lost=data["date"], 
                location_lost=data["location"],
                photo_filepath=photo_filepath
            )
        else:
            success, payload = self.model.report_found_item(
                name=data["name"], 
                description=data["description"], 
                category_id=data["category_id"], 
                priority_level=data["priority"], 
                constituent_id=c_id, 
                date_found=data["date"], 
                location_found=data["location"],
                photo_filepath=photo_filepath
            )

        if success:
            self.view.show_message("Success", f"Item successfully reported!\nSystem Item ID: {payload}")
            self.view.clear_form()
        else:
            self.view.show_message("Error", payload or "Failed to report item to the database.")

    