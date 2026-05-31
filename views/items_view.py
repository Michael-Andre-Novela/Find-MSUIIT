"""Items view placeholder widget."""

from typing import Optional

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ItemsView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Items view (placeholder)"))
