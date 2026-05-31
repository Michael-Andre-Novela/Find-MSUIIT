"""Report item view placeholder widget."""

from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ReportItemView(QWidget):
	def __init__(self, parent: Optional[QWidget] = None):
		super().__init__(parent)
		layout = QVBoxLayout(self)
		layout.addWidget(QLabel("Report Item view (placeholder)"))

