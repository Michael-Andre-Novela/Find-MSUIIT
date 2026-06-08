"""Claims presenter."""

from typing import Any
from models import queries

class ClaimsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries
        
        # Connect UI Events to Functions
        self.view.submit_btn.clicked.connect(self.handle_submit)
        self.view.table.itemSelectionChanged.connect(self.handle_selection)
        self.view.approve_btn.clicked.connect(self.handle_approve)
        
        # Connect the new Reject button
        self.view.reject_btn.clicked.connect(self.handle_reject)

    def start(self):
        """Initializes the view by loading the pending claims table."""
        self.load_pending_claims()

    def load_pending_claims(self):
        claims = self.model.get_pending_claims()
        self.view.populate_table(claims)
        self.view.approve_btn.setEnabled(False)
        self.view.reject_btn.setEnabled(False)

    def handle_submit(self):
        """Processes a new claim request."""
        data = self.view.get_form_data()
        
        if not data["item_id"] or not data["id_number"]:
            self.view.show_message("Validation Error", "Please provide both an Item ID and a Claimant ID.")
            return

        constituent = self.model.get_constituent_by_school_id(data["id_number"])
        if not constituent:
            self.view.show_message("Error", f"Claimant ID '{data['id_number']}' not found in the system.")
            return
            
        success = self.model.create_claim_request(
            item_id=int(data["item_id"]), 
            constituent_id=constituent["constituent_id"], 
            claim_date=data["date"]
        )
        
        if success:
            self.view.show_message("Success", "Claim request successfully filed!")
            self.view.clear_form()
            self.load_pending_claims() # Instantly update the table below
        else:
            self.view.show_message("Database Error", "Failed to file claim. Make sure the Item ID exists.")

    def handle_selection(self):
        """Enables both Action buttons when a row is clicked."""
        if self.view.get_selected_claim():
            self.view.approve_btn.setEnabled(True)
            self.view.reject_btn.setEnabled(True)
        else:
            self.view.approve_btn.setEnabled(False)
            self.view.reject_btn.setEnabled(False)

    def handle_approve(self):
        """Approves the selected claim and officially marks the item as 'Claimed'."""
        selected = self.view.get_selected_claim()
        if not selected:
            return
            
        constituent = self.model.get_constituent_by_school_id(selected["id_number"])
        
        if constituent:
            success = self.model.resolve_claim_request(
                item_id=selected["item_id"], 
                constituent_id=constituent["constituent_id"], 
                administrative_action='Approved'
            )
            
            if success:
                self.view.show_message("Claim Approved", f"Item {selected['item_id']} has been officially claimed!")
                self.load_pending_claims() 
            else:
                self.view.show_message("Error", "Failed to process the approval.")

    def handle_reject(self):
        """Rejects and physically deletes the claim from the database."""
        selected = self.view.get_selected_claim()
        if not selected:
            return
            
        # 1. Ask for confirmation before deleting
        if self.view.ask_confirmation("Confirm Rejection", f"Are you sure you want to permanently delete the claim request for Item {selected['item_id']}?"):
            
            # 2. Proceed with database deletion
            constituent = self.model.get_constituent_by_school_id(selected["id_number"])
            if constituent:
                success = self.model.delete_claim_request(selected["item_id"], constituent["constituent_id"])
                
                if success:
                    self.view.show_message("Claim Rejected", "The claim request was successfully deleted.")
                    self.load_pending_claims()
                else:
                    self.view.show_message("Error", "Failed to delete the claim from the database.")