#!/usr/bin/env python3
"""Back up the current SQLite database and rebuild it from the current schema."""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from models.connection import DB_PATH, initialize_db


def backup_database(db_path: Path) -> Path | None:
    """Copy the current database to a timestamped backup file."""
    if not db_path.exists():
        return None

    backup_dir = db_path.parent / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"{db_path.name}.{datetime.now():%Y%m%d-%H%M%S}.bak"
    shutil.copy2(db_path, backup_path)
    return backup_path


def rebuild_database(force: bool = False) -> Path:
    """Recreate the database from the schema definition in `models.connection`."""
    db_path = Path(DB_PATH)

    if db_path.exists() and not force:
        backup_path = backup_database(db_path)
        if backup_path is not None:
            print(f"Backed up existing database to {backup_path}")
        db_path.unlink()
    elif db_path.exists() and force:
        db_path.unlink()

    initialize_db()
    return db_path


def preview_rebuild(force: bool = False) -> None:
    """Show what the migration would do without changing any files."""
    db_path = Path(DB_PATH)

    if db_path.exists():
        if force:
            print(f"Would remove existing database: {db_path}")
            print("Would rebuild the database without creating a backup first.")
        else:
            backup_dir = db_path.parent / "backups"
            backup_path = backup_dir / f"{db_path.name}.{datetime.now():%Y%m%d-%H%M%S}.bak"
            print(f"Would back up existing database to {backup_path}")
            print(f"Would remove existing database: {db_path}")
            print("Would rebuild the database from the current schema.")
    else:
        print("No existing database found.")
        print("Would create a fresh database from the current schema.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Back up and rebuild the Find-MSUIIT SQLite database."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild without creating a backup first.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the migration steps without modifying any files.",
    )
    args = parser.parse_args()

    if args.dry_run:
        preview_rebuild(force=args.force)
        return 0

    rebuilt_path = rebuild_database(force=args.force)
    print(f"Rebuilt database at {rebuilt_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
