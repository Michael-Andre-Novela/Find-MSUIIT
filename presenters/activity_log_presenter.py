from typing import Any, List, Dict
import logging

logger = logging.getLogger(__name__)

try:
    from models import queries
except ImportError:
    # Handle absolute/relative path import flexibility depending on main run environment
    try:
        from database import queries
    except ImportError:
        queries = None

class ActivityLogPresenter:
    def __init__(self, view: Any, model: Any = None):
        self.view = view
        self.model = model or queries  # Use the queries module as a default model if not provided
        
        # Connect signals from the UI View to methods in this Presenter
        self.view.btn_refresh.clicked.connect(self.load_logs)
        self.view.combo_filter.currentTextChanged.connect(self.load_logs)   

    def start(self) -> None:
        """Triggered automatically by main_window when this panel comes into focus."""
        self.load_logs()

    def load_logs(self) -> None:
        """Fetches, filters, formats, and displays the log list."""
        # 1. Grab current filter text from the view's combo box
        current_filter = self.view.combo_filter.currentText()
        
        # 2. Get data from model layer (or our fallback helper)
        raw_logs = self._get_raw_logs()
        
        # 3. Filter and process the data based on selection
        formatted_list = []
        for log in raw_logs:
            if not log:
                continue

            details = log.get("details") or log.get("message") or ""
            action_type = str(log.get("actions") or log.get("type") or "").lower()
            timestamp = log.get("action_date") or log.get("timestamp") or "0000-00-00 00:00"
            
            # Match the combo box filters to the action text attributes
            if current_filter == "Items Registration":
                if "created" not in  action_type:
                    continue
            elif current_filter == "Claims Processed":
                if "claim" not in action_type:
                    continue
            elif current_filter == "System Alerts":
                if "status" not in action_type:
                    continue
            #If current_filter is "All Activity", it cleanly falls through and passes everyone!
                
            formatted_row = f"[{timestamp}] {details}"
            formatted_list.append(formatted_row)
            
        # 4. Flush and load the text strings directly to the view layout box!
        self.view.show_logs(formatted_list)

    def _get_raw_logs(self) -> List[Dict[str, str]]:
        """Safely fetch real records, using mock events if the database isn't hooked up yet."""
        if self.model and hasattr(self.model, "get_all_activity_logs"):
            try:
                db_logs = self.model.get_all_activity_logs()
                if db_logs:
                    # Convert SQLite Row objects explicitly into standard dictionaries
                    return [dict(row) for row in db_logs]
            except Exception as e:
                logger.error(f"Failed to query database logs: {e}")

                
        # Mock database rows perfectly matching the design we chose
        return [
            {"timestamp": "2026-06-02 10:12:05", "type": "item", "message": "Item Registered: Keys with Maroon Lanyard [ID: 1023]", "user": "Admin"},
            {"timestamp": "2026-06-02 10:15:22", "type": "item", "message": "Item Registered: Black Leather Wallet [ID: 1024]", "user": "Admin"},
            {"timestamp": "2026-06-02 10:30:11", "type": "claim", "message": "New Claim Submitted: Samsung Galaxy S22 [Claim ID: 45]", "user": "S. Khan"},
            {"timestamp": "2026-06-02 11:01:05", "type": "system", "message": "Account Logged In: michael_admin", "user": "System"},
            {"timestamp": "2026-06-02 11:15:30", "type": "claim", "message": "Claim Processed: Approved Brown Leather Wallet [Claim ID: 44]", "user": "sammy_claims"},
            {"timestamp": "2026-06-02 11:45:01", "type": "system", "message": "Connection established successfully to find_iit.db", "user": "System"},
        ]