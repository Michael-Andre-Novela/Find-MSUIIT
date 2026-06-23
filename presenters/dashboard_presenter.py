"""Dashboard presenter."""

from typing import Any, List, Dict
import logging

logger = logging.getLogger(__name__), List, Dict
try:
    from models import queries
from modules.logger import get_logger

log = get_logger(__name__)
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
        # 1. Fetch the stat metrics from the dedicated query
        stats = self._fetch_statistics()

        # 2. Push all five counters to the view's stat cards (including unclaimed)
        self.view.update_counters(
            lost=stats["active_lost"],
            found=stats["active_found"],
            pending=stats["pending_claims"],
            claimed=stats["total_claimed"],
            unclaimed=stats["unclaimed"],
        )

        # 3. Fetch and display the unclaimed alerts banner
        alerts = self._fetch_alerts()
        self.view.show_alerts(alerts)

        # 4. Fetch and display the active items table
        items = self._fetch_active_items()
        self.view.show_items(items)

    def _fetch_statistics(self) -> Dict[str, int]:
        """Fetches the dashboard stat counters from the database."""
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
            "unclaimed": 0,
        }

    def _fetch_alerts(self) -> List[Dict[str, Any]]:
        """Fetches unclaimed found items older than 30 days for the alert banner."""
        if self.model and hasattr(self.model, "get_unclaimed_found_items_alerts"):
            try:
                return self.model.get_unclaimed_found_items_alerts(days=30)
            except Exception as e:
                logger.error(f"Failed to fetch unclaimed alerts: {e}")
        return []

    def _fetch_active_items(self) -> List[Dict[str, Any]]:
        """Internal helper to safely fetch active item records for the table."""
        if self.model and hasattr(self.model, "get_active_dashboard_items"):
            try:
                return self.model.get_active_dashboard_items()
            except Exception as e:
                logger.error(f"Database query layer failed: {e}")
                return []

        return []