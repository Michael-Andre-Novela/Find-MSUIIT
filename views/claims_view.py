"""Claims view placeholder widget."""

from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ClaimsView(QWidget):
	def __init__(self, parent: Optional[QWidget] = None):
		super().__init__(parent)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel("Claims view (placeholder)"))

