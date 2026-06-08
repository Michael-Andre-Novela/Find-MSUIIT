"""Claims presenter: bridges `views.claims_view.ClaimsView` and `models.queries`.

Loads pending claims into the view, and handles Approve / Reject actions.
"""

from typing import Any

from models import queries
from modules.logger import get_logger

log = get_logger(__name__)


class ClaimsPresenter:
    def __init__(self, view: Any, model=None):
        self.view = view
        self.model = model or queries

        # Connect view signals to presenter handlers
        self.view.btn_refresh.clicked.connect(self.load_claims)
        self.view.btn_approve.clicked.connect(self.handle_approve)
        self.view.btn_reject.clicked.connect(self.handle_reject)

    def start(self):
        """Called on initial load to populate the claims table."""
        self.load_claims()

    def load_claims(self):
        """Fetches all pending claims from the DB and sends them to the view."""
        try:
            claims = self.model.get_pending_claims()
            self.view.populate_claims(claims)
            log.info(f"Loaded {len(claims)} pending claim(s).")
        except Exception as e:
            log.error(f"Failed to load claims: {e}", exc_info=True)
            self.view.show_message("Error", "Could not load claims from the database.")

    def _get_selected(self):
        """Returns (item_id, constituent_id_number) from the view selection, or (None, None)."""
        return self.view.get_selected_claim()

    def handle_approve(self):
        """Approves the selected pending claim."""
        item_id, id_number = self._get_selected()
        if item_id is None:
            self.view.show_message("No Selection", "Please select a claim to approve.")
            return

        # Look up the internal constituent_id from the school ID number
        constituent = self.model.get_constituent_by_school_id(id_number)
        if not constituent:
            self.view.show_message("Error", f"Constituent '{id_number}' not found in the database.")
            return

        success, msg = self.model.resolve_claim_request(
            item_id=item_id,
            constituent_id=constituent["constituent_id"],
            administrative_action="Approved"
        )

        if success:
            log.info(f"Claim for item_id={item_id} approved.")
            self.view.show_message("Success", f"Claim for Item ID {item_id} has been approved.\nItem status set to 'Claimed'.")
            self.load_claims()
        else:
            self.view.show_message("Error", msg or "Failed to approve the claim.")

    def handle_reject(self):
        """Rejects the selected pending claim."""
        item_id, id_number = self._get_selected()
        if item_id is None:
            self.view.show_message("No Selection", "Please select a claim to reject.")
            return

        constituent = self.model.get_constituent_by_school_id(id_number)
        if not constituent:
            self.view.show_message("Error", f"Constituent '{id_number}' not found in the database.")
            return

        success, msg = self.model.resolve_claim_request(
            item_id=item_id,
            constituent_id=constituent["constituent_id"],
            administrative_action="Rejected"
        )

        if success:
            log.info(f"Claim for item_id={item_id} rejected.")
            self.view.show_message("Success", f"Claim for Item ID {item_id} has been rejected.\nItem remains 'Active'.")
            self.load_claims()
        else:
            self.view.show_message("Error", msg or "Failed to reject the claim.")
