# Find-MSUIIT

Current layout:

- `models/` for database and data access code
- `presenters/` for UI-to-model coordination
- `views/` for Qt view wrappers and UI assets
- `database/` for the SQLite data file only
- `main.py` for the app entry point

Rebuild the database from the current schema with:

```bash
python database/migrate_db.py
```

Preview the migration without changing files:

```bash
python database/migrate_db.py --dry-run
```