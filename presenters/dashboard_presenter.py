"""Dashboard presenter: bridges `views.dashboard_view.DashboardView` and `models.queries`.

It exposes a simple `start()` method that loads dashboard data and updates the view.
"""

from typing import Any

from models import queries


class DashboardPresenter:
	def __init__(self, view: Any, model=None):
		self.view = view
		self.model = model or queries

	def start(self):
		items = self.model.get_active_dashboard_items()
		# Presenters own how data maps to the view
		self.view.show_items(items)

	def refresh(self):
		self.start()

