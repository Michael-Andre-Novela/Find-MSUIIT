import logging
import os
import sys
from datetime import datetime

# =====================================================================
# LOGGER CONFIGURATION
# =====================================================================

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
LOG_FILE = os.path.join(LOG_DIR, "find_msuiit.log")

# Log format: timestamp | level | module | message
LOG_FORMAT = "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def _setup_logger(name: str = "FindMSUIIT") -> logging.Logger:
    """
    Internal setup: creates and configures the root application logger.
    Attaches both a console handler and a rotating file handler.
    Called once at module load; subsequent calls return the cached logger.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on re-import
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # Capture all levels; handlers filter independently

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # --- Console Handler (INFO and above) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # --- File Handler (DEBUG and above, persistent) ---
    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Singleton logger instance for the application
_logger = _setup_logger()


# =====================================================================
# PUBLIC LOGGING API  (info / debug / warn / error)
# =====================================================================

def get_logger(module_name: str = "App") -> logging.Logger:
    """
    Returns a child logger scoped to a specific module/presenter/view.

    Usage:
        from modules.logger import get_logger
        log = get_logger(__name__)
        log.info("Dashboard loaded.")

    Args:
        module_name: Typically pass __name__ from the calling module.

    Returns:
        A logging.Logger child of the root FindMSUIIT logger.
    """
    return _logger.getChild(module_name)


def info(message: str, module: str = "App") -> None:
    """
    Logs an informational message. Use for normal operational events
    (e.g., 'Item reported', 'Claim approved').

    Args:
        message: Human-readable description of the event.
        module:  Name of the calling module for context (default: 'App').
    """
    get_logger(module).info(message)


def debug(message: str, module: str = "App") -> None:
    """
    Logs a debug-level message. Use for verbose tracing during development
    (e.g., query parameters, intermediate values). Suppressed in production
    console output but always written to the log file.

    Args:
        message: Diagnostic detail.
        module:  Name of the calling module for context.
    """
    get_logger(module).debug(message)


def warn(message: str, module: str = "App") -> None:
    """
    Logs a warning. Use for recoverable issues or unexpected-but-handled
    states (e.g., 'Duplicate constituent ID attempted').

    Args:
        message: Description of the warning condition.
        module:  Name of the calling module for context.
    """
    get_logger(module).warning(message)


def error(message: str, module: str = "App", exc_info: bool = False) -> None:
    """
    Logs an error. Use for failures that affect functionality
    (e.g., database write failures, missing records).

    Args:
        message:  Description of the error.
        module:   Name of the calling module for context.
        exc_info: If True, appends the current exception traceback to the log.
                  Pass True inside except blocks for full stack traces.
    """
    get_logger(module).error(message, exc_info=exc_info)


# =====================================================================
# INTEGRATION POINTS — DB Activity Log Bridge
# =====================================================================

def log_db_activity(item_id: int, action: str, details: str) -> None:
    """
    Integration point: writes a structured entry to the SQLite activity_log
    table via queries.py. Use this for item-level audit trail events that
    must persist beyond the session log file.

    Separates the concern of 'application logging' (file/console) from
    'business event logging' (database), while keeping a single call site.

    Args:
        item_id: The item this activity is associated with.
        action:  Short action label (e.g., 'Claim Approved', 'Status Updated').
        details: Full descriptive detail for the log entry.

    Example:
        log_db_activity(42, "Status Updated", "Admin changed status to Archived.")
    """
    try:
        # Lazy import to avoid circular dependency at module load
        from models import queries
        # FIX: format matches DB CHECK constraint — YYYY-MM-DD HH:MM (no seconds)
        action_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        with queries.get_connection() as conn:
            conn.execute("""
                INSERT INTO activity_log (item_id, details, actions, action_date)
                VALUES (?, ?, ?, ?)
            """, (item_id, details, action, action_date))
            conn.commit()
        debug(f"DB activity logged → item {item_id} | {action}", module="Logger")
    except Exception as e:
        error(f"Failed to write DB activity log for item {item_id}: {e}",
              module="Logger", exc_info=True)


def log_system_event(event: str, details: str = "") -> None:
    """
    Integration point: logs a system-level event (startup, shutdown,
    DB init, integrity check) that is not tied to a specific item.
    Written to the file log only (no DB row created).

    Args:
        event:   Short event name (e.g., 'DB Initialized', 'App Started').
        details: Optional additional context.
    """
    message = f"[SYSTEM] {event}" + (f" — {details}" if details else "")
    info(message, module="System")


# =====================================================================
# CONVENIENCE: Decorator for automatic function-level debug tracing
# =====================================================================

def trace(func):
    """
    Decorator that logs entry and exit of any function at DEBUG level.
    Useful for tracing presenter or query function calls during development.

    Usage:
        from modules.logger import trace

        @trace
        def my_function(arg1, arg2):
            ...
    """
    import functools

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        debug(f"→ Entering {func.__qualname__}()", module="Trace")
        result = func(*args, **kwargs)
        debug(f"← Exiting  {func.__qualname__}()", module="Trace")
        return result
    return wrapper


# =====================================================================
# MODULE SELF-TEST
# =====================================================================

if __name__ == "__main__":
    log_system_event("Logger Self-Test", "Verifying all log levels.")
    info("This is an INFO message.", module="Test")
    debug("This is a DEBUG message — visible in log file only.", module="Test")
    warn("This is a WARN message.", module="Test")
    error("This is an ERROR message (no exception).", module="Test")
    print(f"\nLog file written to: {LOG_FILE}")