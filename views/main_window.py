"""Main application window and central stacked widget.

Provides a simple `MainWindow` implementation that other presenters can
register views with via `add_view(name, widget)` and switch between using
`show_view(name)`.

This file intentionally keeps the UI minimal so presenters can plug in
their real QWidget subclasses later.
"""

from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QMainWindow,
)


class MainWindow(QMainWindow):
    """Central application window with a `QStackedWidget`."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._views: Dict[str, QWidget] = {}
        self._nav_buttons: Dict[str, QPushButton] = {}

        central_widget = QWidget(self)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._sidebar = QFrame(central_widget)
        self._sidebar.setObjectName("sidebarFrame")
        self._build_sidebar_layout()
        main_layout.addWidget(self._sidebar)

        self._stack = QStackedWidget(central_widget)
        main_layout.addWidget(self._stack)

        self.setCentralWidget(central_widget)

    def _build_sidebar_layout(self) -> None:
        """Assembles the internal vertical menu layout inside the sidebar."""
        sidebar_layout = QVBoxLayout(self._sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(4)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        brand_label = QLabel("Find-MSUIIT", self._sidebar)
        brand_label.setObjectName("brandLabel")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sidebar_layout.addWidget(brand_label)
        sidebar_layout.addSpacing(15)

        self._add_sidebar_action(sidebar_layout, "dashboard", "📊  Dashboard")
        self._add_sidebar_action(sidebar_layout, "items", "📦  Items")
        self._add_sidebar_action(sidebar_layout, "claims", "🗂️  Manage Claims")
        self._add_sidebar_action(sidebar_layout, "report", "📝  Report Item")
        self._add_sidebar_action(sidebar_layout, "constituents", "👥  Constituents")
        self._add_sidebar_action(sidebar_layout, "activity", "📜  Activity Log")

        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        sidebar_layout.addItem(vertical_spacer)

    def _add_sidebar_action(self, layout: QVBoxLayout, view_name: str, label: str) -> None:
        """Creates a checkable, exclusive navigation sidebar button link."""
        btn = QPushButton(label, self._sidebar)
        btn.setCheckable(True)
        btn.setAutoExclusive(True)
        btn.setObjectName("navButton")
        btn.clicked.connect(lambda: self.show_view_safe(view_name))
        layout.addWidget(btn)
        self._nav_buttons[view_name] = btn

    def add_view(self, name: str, widget: QWidget) -> None:
        """Add a view widget under `name` and register it in the stack."""
        if name in self._views:
            old = self._views[name]
            idx = self._stack.indexOf(old)
            if idx != -1:
                self._stack.removeWidget(old)
        self._views[name] = widget
        self._stack.addWidget(widget)

    def show_view(self, name: str) -> None:
        """Switch to the view previously registered with `add_view`."""
        widget = self._views.get(name)
        if widget is None:
            raise KeyError(f"no view named {name!r} registered")
        self._stack.setCurrentWidget(widget)
        if name in self._nav_buttons:
            self._nav_buttons[name].setChecked(True)

    def get_view(self, name: str) -> QWidget:
        """Return the registered widget for `name` or raise KeyError."""
        widget = self._views.get(name)
        if widget is None:
            raise KeyError(f"no view named {name!r} registered")
        return widget

    def show_view_safe(self, name: str) -> None:
        """Attempt to show a view if registered; otherwise show a brief message."""
        try:
            self.show_view(name)
        except KeyError:
            try:
                self.statusBar().showMessage(f"View '{name}' not available", 3000)
            except Exception:
                pass
