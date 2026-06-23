```markdown
# Find-MSUIIT — Lost & Found Management System

A desktop application for managing lost and found items at Mindanao State University - Iligan Institute of Technology (MSU-IIT). Built with **PySide6** and **SQLite**, following the **MVP (Model-View-Presenter)** architectural pattern.

---

## 📋 Features

- **Item Registration** — Report lost or found items with details (name, description, category, location, date)
- **Auto-Matching** — Intelligent similarity matching between lost and found items
- **Claim Management** — File, review, approve, or reject ownership claims with audit trails
- **Constituent Registry** — Manage student/staff profiles with validation
- **Activity Logging** — Complete audit trail of all system actions with filtering
- **Historical Archives** — Browse and restore archived items
- **Database Backup & Restore** — Create and restore database snapshots
- **Dark/Light Theme Toggle** — Switch between light and dark mode seamlessly
- **Search & Filter** — Find items by name, category, type, or status

---

## 🏗️ Architecture

### Directory Structure

``
find-iit/
├── models/
│   ├── connection.py       # Database initialization & schema (DDL)
│   ├── queries.py          # Data access layer (CRUD operations)
│   └── matching.py         # Auto-matching algorithm for lost/found items
├── presenters/
│   ├── dashboard_presenter.py
│   ├── items_presenter.py
│   ├── claims_presenter.py
│   ├── constituents_presenter.py
│   ├── activity_log_presenter.py
│   └── report_item_presenter.py
├── views/
│   ├── main_window.py      # Central sidebar & stacked widget navigation
│   ├── dashboard_view.py   # Statistics overview & active items table
│   ├── items_view.py       # Search & manage active items
│   ├── claims_view.py      # File & process ownership claims
│   ├── constituents_view.py # Register & manage user profiles
│   ├── activity_log_view.py # System activity timeline & archives
│   ├── report_item_view.py # Lost/found item reporting form
│   └── popups.py           # Dialog windows (matches, categories, edit)
├── modules/
│   ├── logger.py           # Unified logging (console + file + DB)
│   └── __init__.py
├── assets/
│   ├── styles.qss          # Light mode stylesheet (Qt Style Sheet)
│   └── styles_dark.qss     # Dark mode stylesheet
├── database/
│   ├── find_iit.db         # SQLite database (auto-created)
│   └── migrate_db.py       # Database migration & initialization script
├── logs/
│   └── find_msuiit.log     # Application event log
├── main.py                 # Application entry point
├── README.md
└── requirements.txt
```

### Design Pattern: MVP (Model-View-Presenter)

- **Model** (`models/`) — Database queries, business logic, data validation
- **View** (`views/`) — Qt UI components, layout, event binding
- **Presenter** (`presenters/`) — Coordinates between view and model, handles navigation and state

**Flow:** User interaction in View → signals to Presenter → Presenter queries Model → Model returns data → Presenter formats & sends to View → View updates UI

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- **SQLite3** (included with Python)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd find-iit
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database:**
   ```bash
   python models/connection.py
   ```

   Or use the migration script:
   ```bash
   python database/migrate_db.py
   ```

### Running the Application

```bash
python main.py
```

The app will launch with the Dashboard tab active. Use the sidebar to navigate between views.

---

## 📊 Database Schema

### Core Tables

| Table | Purpose | Key Fields |
|---|---|---|
| `categories` | Item classifications | `category_id`, `category_name`, `description` |
| `constituents` | Campus users (students/staff) | `constituent_id`, `id_number`, `name`, `contact_email`, `contact_phone` |
| `items` | All tracked items (master table) | `item_id`, `name`, `type` (Lost/Found), `status` (Active/Claimed/Archived), `category_id` |
| `lost` | Lost item reports | `item_id` (PK), `constituent_id`, `date_lost`, `location_lost` |
| `found` | Found item reports | `item_id` (PK), `constituent_id`, `date_found`, `location_found` |
| `claim` | Ownership claims | `item_id` (PK), `constituent_id`, `claim_date`, `claim_status` (Pending/Approved/Rejected) |
| `activity_log` | System audit trail | `log_id`, `item_id`, `actions`, `details`, `action_date` |

### Relationships

```
constituents ──────→ items (1:N)
                      ↓
              ┌───────┼───────┐
              ↓       ↓       ↓
            lost    found   claim ←─── constituents (N:1)
              ↓       ↓       ↓
              └───────┴───────┘
                      ↓
              activity_log (1:N)

categories ──→ items (1:N)
```

---

## 🗄️ Database Management

### Rebuild Database from Schema

Completely reinitialize the database with the current DDL schema:

```bash
python database/migrate_db.py
```

This will:
- Drop existing tables (if any)
- Create all tables from scratch
- Seed default categories
- Insert test data (optional)

### Dry-Run Mode

Preview what the migration will do without making changes:

```bash
python database/migrate_db.py --dry-run
```

### Backup & Restore

Use the **Maintenance** tab in the app to:
- Create a new database backup
- List existing backups
- Restore from a selected backup snapshot

Backups are stored in the `database/backups/` directory.

### Database Optimization

In the **Maintenance** tab, run **Optimize Database (VACUUM)** to:
- Reclaim unused disk space
- Reindex all tables
- Improve query performance

---

## 🎨 Theming

### Light Mode (Default)
- Clean white backgrounds with subtle borders
- Dark text for contrast
- MSU-IIT maroon accent color (#7A1C1C)

### Dark Mode
- Charcoal backgrounds (#111827) with lighter text
- Reduced eye strain for evening use
- Toggle via the 🌙/☀️ button in the sidebar

All colors are defined in QSS files (`assets/styles.qss`, `assets/styles_dark.qss`), not hardcoded in views.

---

## 📝 Logging

The application logs to two destinations:

1. **Console Output** — Info level and above (visible while running)
2. **File Log** — Debug level and above (saved to `logs/find_msuiit.log`)
3. **Database Log** — Activity log table (`activity_log`) for audit trails

Access the **Activity Log** tab to view system actions with filtering by:
- All Activity
- Items Registration
- Claims Processed
- System Alerts

---

## 🔍 Auto-Matching Algorithm

Located in `models/matching.py`, the algorithm:

1. **Compares** lost items against found items using weighted similarity scoring
2. **Weights** by field importance:
   - Item name: 40%
   - Description: 35%
   - Category: 25%
3. **Normalizes** text (lowercases, removes punctuation, strips stop words)
4. **Scores** using combined sequence matching (60%) + token overlap (40%)
5. **Filters** by threshold (default: 0.45 / 45% match)
6. **Ranks** results by score (highest first)

**Usage:**
```python
from models.matching import find_matches_for_item

lost_item = queries.get_item_details(item_id=5, item_type='Lost')
candidates = queries.search_active_items(item_type='Found')
matches = find_matches_for_item(lost_item, candidates)

for match in matches:
    print(f"{match['name']} — {match['match_score']:.1%} match")
```

---

## 🔐 Data Validation

### Input Validation (Presenters)

- **ID Numbers** — Must match `YYYY-NNNN` format (e.g., `2026-0001`)
- **Emails** — Standard email format validation
- **Phone Numbers** — 11 digits starting with `09` (Philippine mobile format)
- **Names** — Letters, spaces, hyphens, and dots only
- **Dates** — ISO 8601 format (`YYYY-MM-DD`)

### Database Constraints (DDL)

- **Primary Keys** — Enforced uniqueness
- **Foreign Keys** — Referential integrity with cascading deletes
- **Check Constraints** — Type and status enumerations
- **Unique Constraints** — Category names, ID numbers
- **Not Null** — Required fields validated at schema level

---

## 🐛 Troubleshooting

### Database Won't Initialize

```bash
# Check if database file exists
ls -la database/find_iit.db

# Rebuild from scratch
python models/connection.py

# Or use migration script with verbose output
python database/migrate_db.py --verbose
```

### Activity Log Not Showing

1. Ensure `activity_log_presenter.py` is wired in `main.py`
2. Check that button signals are connected: `btn_refresh.clicked.connect(self.load_logs)`
3. Review filter keywords in presenter (must match action values in DB)

### Theme Toggle Not Working

1. Verify QSS files exist in `assets/`
2. Check that `main_window.py` has `toggle_theme()` method
3. Ensure stylesheet paths are correct relative to project root

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify paths in main.py
python -c "from models import queries; print('OK')"
python -c "from presenters import dashboard_presenter; print('OK')"
```

---

## 📚 Development

### Adding a New View

1. Create `views/new_view.py` with a `QWidget` subclass
2. Create `presenters/new_presenter.py` with signal connections
3. Register in `main.py`:
   ```python
   from views.new_view import NewView
   from presenters.new_presenter import NewPresenter
   
   new_view = NewView()
   new_presenter = NewPresenter(new_view)
   new_presenter.start()
   window.add_view("new", new_view)
   ```
4. Add sidebar button in `main_window.py`: `self._add_sidebar_action(sidebar_layout, "new", "📌  New View")`

### Running Tests

```bash
# Unit tests (when available)
pytest tests/

# Linting
flake8 models/ presenters/ views/

# Type checking
mypy models/
```
