"""Minimal dashboard view implemented as a QWidget.

This view is intentionally small: a `QListWidget` that the presenter fills
with items returned by the model. Presenters can call `show_items(items)`
where `items` is a list of dicts.
"""

from typing import List, Dict, Any, Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem


class DashboardView(QWidget):
	def __init__(self, parent: Optional[QWidget] = None):
		super().__init__(parent)
		self._list = QListWidget(self)
		layout = QVBoxLayout(self)
		layout.addWidget(self._list)

	def show_items(self, items: List[Dict[str, Any]]):
		self._list.clear()
		for it in items:
			label = f"[{it.get('type')}] {it.get('name')} (#{it.get('item_id')})"
			QListWidgetItem(label, self._list)

