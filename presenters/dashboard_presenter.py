"""Dashboard presenter: bridges `views.dashboard_view.DashboardView` and `models.queries`.

It exposes a simple `start()` method that loads dashboard data and updates the view.
"""

from typing import Any, List, Dict
import logging

logger = logging.getLogger(__name__)

try:
    from models import queries
except ImportError:
    logger.warning("models.queries module not found. Using placeholder data engine.")
    queries = None


class DashboardPresenter:
    def __init__(self, view: Any, model: Any = None):
        """Initializes the presenter with hooks to the UI view and database model layer."""
        self.view = view
        self.model = model or queries

    def start(self) -> None:
        """Triggered automatically by main_window when the dashboard tab comes into focus."""
        self.load_dashboard()

    def refresh(self) -> None:
        """Forces a re-query to capture newly updated lost/found metric updates."""
        self.load_dashboard()

    def load_dashboard(self) -> None:
        """Fetches data from the model, processes counters, and updates the view."""
        # 1. Fetch data from Michael's queries layer with safety fallbacks
        items = self._fetch_active_items()
            
        # 2. Count metrics dynamically based on 'status' dictionary keys
        lost_count = 0
        found_count = 0
        
        for item in items:
            status = item.get("status", "").lower()
            if status == "lost":
                lost_count += 1
            elif status == "found":
                found_count += 1

        # 3. Hand over data to the view's public interface methods
        # Push the raw integers to your newly styled metric cards
        self.view.update_counter(lost_count, found_count)
        
        # Push the full array to your QTextEdit item display box
        self.view.show_items(items)

    def _fetch_active_items(self) -> List[Dict[str, Any]]:
        """Internal helper to safely fetch database records or supply mock items."""
        if self.model and hasattr(self.model, "get_active_dashboard_items"):
            try:
                return self.model.get_active_dashboard_items()
            except Exception as e:
                logger.error(f"Database query layer failed: {e}")
                return []
                
        # Robust mock dataset matching our application test data requirements
        return [
            {"name": "Keys with Maroon Lanyard", "status": "lost"},
            {"name": "Samsung Galaxy S22", "status": "found"},
            {"name": "Brown Leather Wallet", "status": "lost"},
            {"name": "Dell XPS Laptop", "status": "found"},
            {"name": "MSU-IIT Umbrella", "status": "lost"},
        ]