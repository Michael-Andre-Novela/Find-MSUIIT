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

    # ── Dashboard ─────────────────────────────────────────────────────
    try:
        from views.dashboard_view import DashboardView
        from presenters.dashboard_presenter import DashboardPresenter

        dashboard_view = DashboardView()
        dashboard_presenter = DashboardPresenter(dashboard_view)
        window.add_view("dashboard", dashboard_view)
        dashboard_presenter.start()
        window.show_view("dashboard")
    except Exception:
        pass

    # ── Report Item ───────────────────────────────────────────────────
    try:
        from views.report_item_view import ReportItemView
        from presenters.report_item_presenter import ReportItemPresenter
        
        report_view = ReportItemView()
        report_presenter = ReportItemPresenter(report_view)
        report_presenter.start()
        window.add_view("report", report_view)
    except Exception:
        pass

    # ── Claims ────────────────────────────────────────────────────────
    try:
        from views.claims_view import ClaimsView
        from presenters.claims_presenter import ClaimsPresenter

        claims_view = ClaimsView()
        claims_presenter = ClaimsPresenter(claims_view)
        claims_presenter.start() # Fetches the data for the claims table
        window.add_view("claims", claims_view)
    except Exception:
        pass


    # ── Items Management ──────────────────────────────────────────────
    try:
        from views.items_view import ItemsView
        from presenters.items_presenter import ItemsPresenter

        items_view = ItemsView()
        items_presenter = ItemsPresenter(items_view)
        items_presenter.start() # Loads the active items table data
        window.add_view("items", items_view)
    except Exception:
        pass

    # ── Constituents Directory ────────────────────────────────────────
    try:
        from views.constituents_view import ConstituentsView
        from presenters.constituents_presenter import ConstituentsPresenter

        constituents_view = ConstituentsView()
        constituents_presenter = ConstituentsPresenter(constituents_view)
        
        # MISSING CODE INSERTED: This triggers the database query on startup!
        constituents_presenter.start() 
        
        window.add_view("constituents", constituents_view)
    except Exception:
        pass

    # ── Activity Log & Archives ───────────────────────────────────────
    try:
        from views.activity_log_view import ActivityLogView
        from presenters.activity_log_presenter import ActivityLogPresenter
        
        activity_view = ActivityLogView()
        activity_presenter = ActivityLogPresenter(activity_view)
        
        # MISSING LINE ADDED: Forces the tabs to fetch database data!
        activity_presenter.start() 
        
        window.add_view("activity", activity_view)
    except Exception as e:
        print(f"Failed to load Activity Log view: {e}")

    # ── Maintenance & Backups ─────────────────────────────────────────
    try:
        from views.maintenance_view import MaintenanceView
        from presenters.maintenance_presenter import MaintenancePresenter

        maintenance_view = MaintenanceView()
        maintenance_presenter = MaintenancePresenter(maintenance_view)
        maintenance_presenter.start()
        window.add_view("maintenance", maintenance_view)
    except Exception as e:
        print(f"Failed to load Maintenance view: {e}")
        
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())