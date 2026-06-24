"""Main application window and central stacked widget.

Provides a simple `MainWindow` implementation that other presenters can
register views with via `add_view(name, widget)` and switch between using
`show_view(name)`.

This file intentionally keeps the UI minimal so presenters can plug in
their real QWidget subclasses later.
"""

from typing import Dict, Optional
from pathlib import Path # NEW

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap # NEW
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

        # --- ADDING THE INTERNAL LOGO ---
        logo_label = QLabel(self._sidebar)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Resolve the path to where LOGO.jpg is stored
        root_dir = Path(__file__).parent.parent
        logo_path = root_dir / "LOGO.png"
        
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # Smoothly scale the logo to a maximum width of 100 pixels
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            
            # Add a little breathing room at the top
            sidebar_layout.addSpacing(15)
            sidebar_layout.addWidget(logo_label)
        # --------------------------------

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
        self._add_sidebar_action(sidebar_layout, "maintenance", "🛠️  Maintenance")

        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        sidebar_layout.addItem(vertical_spacer)

        self._current_theme = "light"
        self.btn_theme_toggle = QPushButton("🌙  Dark Mode", self._sidebar)
        self.btn_theme_toggle.setObjectName("themeToggleButton")
        self.btn_theme_toggle.clicked.connect(self.toggle_theme)
        self.btn_theme_toggle.setStyleSheet("""
            QPushButton {
                background-color: #1F2937;
                color: #FFFFFF;
                font-family: "Segoe UI", sans-serif;
                font-size: 13px;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 10px 15px;
                margin: 10px 12px;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        sidebar_layout.addWidget(self.btn_theme_toggle)

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

    def toggle_theme(self) -> None:
        """Switch stylesheets between light and dark mode."""
        from pathlib import Path
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance()
        if not app:
            return

        current_theme = getattr(self, "_current_theme", "light")
        assets_dir = Path(__file__).resolve().parent.parent / "assets"

        if current_theme == "light":
            new_theme = "dark"
            qss_path = assets_dir / "styles_dark.qss"
            self.btn_theme_toggle.setText("☀️  Light Mode")
        else:
            new_theme = "light"
            qss_path = assets_dir / "styles.qss"
            self.btn_theme_toggle.setText("🌙  Dark Mode")

        try:
            with qss_path.open("r", encoding="utf-8") as fh:
                app.setStyleSheet(fh.read())
            self._current_theme = new_theme
        except Exception as e:
            print(f"Failed to load stylesheet {qss_path.name}: {e}")
