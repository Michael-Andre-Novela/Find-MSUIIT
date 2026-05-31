import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from models.connection import initialize_db
from models.queries import verify_database_integrity

from views.main_window import MainWindow


def _load_stylesheet(path: Path):
    try:
        with path.open("r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return None


def main():
    initialize_db()
    if not verify_database_integrity():
        raise RuntimeError("Database integrity check failed.")

    app = QApplication(sys.argv)

    # Load global stylesheet if present
    qss_path = Path(__file__).parent / "assets" / "styles.qss"
    stylesheet = _load_stylesheet(qss_path)
    if stylesheet:
        app.setStyleSheet(stylesheet)

    window = MainWindow()
    window.setWindowTitle("FindIIT")
    window.resize(1000, 640)

    # --- Initialize core presenters and views
    try:
        from views.dashboard_view import DashboardView
        from presenters.dashboard_presenter import DashboardPresenter

        dashboard_view = DashboardView()
        dashboard_presenter = DashboardPresenter(dashboard_view)
        # register and show dashboard
        window.add_view("dashboard", dashboard_view)
        dashboard_presenter.start()
        window.show_view("dashboard")
    except Exception:
        # Non-fatal: if presenters are not ready, still show the main window empty
        pass

    # Register lightweight placeholder views for toolbar navigation
    try:
        from views.items_view import ItemsView
        from views.claims_view import ClaimsView
        from views.report_item_view import ReportItemView
        from views.constituents_view import ConstituentsView
        from views.activity_log_view import ActivityLogView

        window.add_view("items", ItemsView())
        window.add_view("claims", ClaimsView())
        window.add_view("report", ReportItemView())
        window.add_view("constituents", ConstituentsView())
        window.add_view("activity", ActivityLogView())
    except Exception:
        pass

    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())