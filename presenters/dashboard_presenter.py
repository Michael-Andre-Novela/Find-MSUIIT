"""Dashboard presenter."""

from typing import Any, List, Dict
from models import queries
from modules.logger import get_logger

log = get_logger(__name__)


class DashboardPresenter:
    def __init__(self, view: Any, model: Any = None):
        self.view = view
        self.model = model or queries
        self.view.btn_refresh.clicked.connect(self.load_dashboard)

    def start(self) -> None:
        self.load_dashboard()

    def load_dashboard(self) -> None:
        """Fetches stats and active items, then updates the view."""
        # 1. Fetch summary statistics
        try:
            stats = self.model.get_dashboard_statistics()
        except Exception as e:
            log.error(f"Failed to load dashboard statistics: {e}")
            stats = {"active_lost": 0, "active_found": 0, "pending_claims": 0, "total_claimed": 0}

        # 2. Fetch active items list
        try:
            items = self.model.get_active_dashboard_items()
        except Exception as e:
            log.error(f"Failed to load active items: {e}")
            items = []

        # 3. Push to view
        self.view.update_counters(
            lost=stats["active_lost"],
            found=stats["active_found"],
            pending=stats["pending_claims"],
            claimed=stats["total_claimed"]
        )
        self.view.show_items(items)