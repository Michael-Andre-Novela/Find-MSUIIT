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

        # Connect the refresh button
        self.view.btn_refresh.clicked.connect(self.refresh)

    def start(self) -> None:
        """Triggered automatically by main_window when the dashboard tab comes into focus."""
        self.load_dashboard()

    def refresh(self) -> None:
        """Forces a re-query to capture newly updated lost/found metric updates."""
        self.load_dashboard()

    def load_dashboard(self) -> None:
        """Fetches data from the model, processes counters, and updates the view."""
        # 1. Fetch the four stat metrics from the dedicated query
        stats = self._fetch_statistics()

        # 2. Push all four counters to the view's stat cards
        self.view.update_counters(
            lost=stats["active_lost"],
            found=stats["active_found"],
            pending=stats["pending_claims"],
            claimed=stats["total_claimed"],
        )

        # 3. Fetch and display the active items table
        items = self._fetch_active_items()
        self.view.show_items(items)

    def _fetch_statistics(self) -> Dict[str, int]:
        """Fetches the four dashboard stat counters from the database."""
        if self.model and hasattr(self.model, "get_dashboard_statistics"):
            try:
                return self.model.get_dashboard_statistics()
            except Exception as e:
                logger.error(f"Failed to fetch dashboard statistics: {e}")

        # Fallback zeros so the UI never crashes
        return {
            "active_lost": 0,
            "active_found": 0,
            "pending_claims": 0,
            "total_claimed": 0,
        }

    def _fetch_active_items(self) -> List[Dict[str, Any]]:
        """Internal helper to safely fetch active item records for the table."""
        if self.model and hasattr(self.model, "get_active_dashboard_items"):
            try:
                return self.model.get_active_dashboard_items()
            except Exception as e:
                logger.error(f"Database query layer failed: {e}")
                return []

        return []