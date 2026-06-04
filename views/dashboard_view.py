"""Minimal dashboard view implemented as a QWidget.

This view is intentionally small: a `QListWidget` that the presenter fills
with items returned by the model. Presenters can call `show_items(items)`
where `items` is a list of dicts.
"""

from typing import List, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame, QTextEdit, QLabel


class DashboardView(QWidget):

	def __init__(self, parent: Optional[QWidget] = None):
		super().__init__(parent)

		# 1. This engine stacks everything from top to bottom
		self.main_layout = QVBoxLayout(self)	
		self.main_layout.setContentsMargins(20,20,20,20)
		self.main_layout.setSpacing(15)

		# 2. Title at the top
		self.lbl_title = QLabel("Dashboard Overview", self)
		self.lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1A1A1A;")
		self.main_layout.addWidget(self.lbl_title)

		# 3. Create a horizontal row for stats
		self.cards_row = QHBoxLayout()
		self.cards_row.setSpacing(10)

		self.card_lost = self._create_stat_card("Active Lost Items")
		self.card_found = self._create_stat_card("Active Found Items")

		# Add the cards to the horizontal row
		self.cards_row.addWidget(self.card_lost)
		self.cards_row.addWidget(self.card_found)	

		# Nest the horizontal row inside our main vertical layout
		self.main_layout.addLayout(self.cards_row)
		
		# 4. Below the cards, add a text area for item details
		self.item_display = QTextEdit(self)
		self.item_display.setReadOnly(True) # Keeps users from typing over the text
		self.main_layout.addWidget(self.item_display)

	def _create_stat_card(self, title: str) -> QFrame:
		"""Helper to build a styled metric box container."""
		card = QFrame(self)
		card.setObjectName("statCard")
		card.setMinimumHeight(80)

		card_layout = QVBoxLayout(card)

		lbl_title = QLabel(title, card)
		lbl_title.setStyleSheet("font-size: 11px; font-weight: bold; color: #7A1C1C;")

		lbl_value = QLabel("0", card)
		lbl_value.setStyleSheet("font-size: 24px; font-weight: 800; color: #1A1A1A;")

		card_layout.addWidget(lbl_title)
		card_layout.addWidget(lbl_value, 0, Qt.AlignmentFlag.AlignBottom)

		card.setProperty("displayLabel", lbl_value)  # Store reference for easy updates
		return card

	def update_counter(self, lost_count: int, found_count: int) -> None:
		"""Public method for presenters to update the dashboard metrics."""
		# Find the attached display labels and update their text nodes
		self.card_lost.property("displayLabel").setText(str(lost_count))
		self.card_found.property("displayLabel").setText(str(found_count))
	
	def show_items(self, items: List[dict]) -> None:
		""""Public method for presenters to inject the raw list data"""
		self.item_display.clear()

		if not items:
			self.item_display.append("No active items on the dashboard.")
			return
		
		for item in items:
			#format the dictionary properties passed by the presenter
			name = item.get("name", "Unknown Item")
			status = item.get("status", "Unknown Status")
			self.item_display.append(f". {name} [{status}]")