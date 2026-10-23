"""
SQLite Database initialization and connection management for HomeFlow AI.
Thread-safe connection handling and table migrations.
"""

import os
import sqlite3
from pathlib import Path
from contextlib import contextmanager

BASE_DIR = Path(__file__).resolve().parent.parent


def get_db_path() -> str:
    """Return the absolute path to the SQLite database file."""
    env_path = os.getenv("HOMEFLOW_DB_PATH")
    if env_path:
        db_file = Path(env_path)
    else:
        db_file = BASE_DIR / "homeflow.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return str(db_file)


@contextmanager
def get_db_connection():
    """
    Context manager for SQLite connections.
    Ensures connection isolation and automatic commit/rollback.
    """
    path = get_db_path()
    conn = sqlite3.connect(path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(seed: bool = True):
    """
    Initialize SQLite database tables and seed with initial demonstration data
    if tables are empty. Prevents duplicate seed data on repeated restarts.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Household Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT 'general',
                priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
                due_date TEXT,
                is_completed INTEGER DEFAULT 0 CHECK(is_completed IN (0, 1)),
                completed_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
        """)

        # Household Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                remind_at TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0 CHECK(is_completed IN (0, 1)),
                completed_at TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # Simulated Entry Events table (strictly segregated)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS simulated_entry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                location TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                details TEXT,
                is_simulated INTEGER DEFAULT 1
            );
        """)

        # Assistant Action Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS action_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                tool_called TEXT,
                arguments TEXT,
                status TEXT NOT NULL,
                result TEXT,
                created_at TEXT NOT NULL
            );
        """)

        if seed:
            _seed_initial_demo_data(cursor)


def _seed_initial_demo_data(cursor: sqlite3.Cursor):
    """
    Seed initial demonstration records if tables are empty.
    All sample records are clearly labelled as demonstration or SIMULATED.
    """
    from datetime import datetime, timedelta, timezone

    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")
    created_at = now.isoformat()

    # 1. Seed tasks if none exist
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        demo_tasks = [
            (
                "Clean kitchen counters & dishwasher",
                "Wipe surfaces, run eco-cycle on dishwasher, empty recycling bin",
                "kitchen",
                "high",
                today_str,
                0,
                None,
                created_at,
                created_at,
            ),
            (
                "Inspect HVAC air filter in hallway",
                "Check airflow and replace MERV 11 filter if dusty",
                "maintenance",
                "medium",
                tomorrow_str,
                0,
                None,
                created_at,
                created_at,
            ),
            (
                "Water indoor plants in living room",
                "Water fiddle-leaf fig and monstera with room-temp water",
                "cleaning",
                "low",
                today_str,
                1,
                (now - timedelta(hours=2)).isoformat(),
                created_at,
                created_at,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO tasks (title, description, category, priority, due_date, is_completed, completed_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            demo_tasks,
        )

    # 2. Seed reminders if none exist
    cursor.execute("SELECT COUNT(*) FROM reminders")
    if cursor.fetchone()[0] == 0:
        demo_reminders = [
            (
                "Call grandmother for weekly check-in",
                f"{today_str}T18:00:00",
                0,
                None,
                created_at,
            ),
            (
                "Take out curbside recycling bin",
                f"{tomorrow_str}T07:30:00",
                0,
                None,
                created_at,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO reminders (title, remind_at, is_completed, completed_at, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            demo_reminders,
        )

    # 3. Seed simulated entry events if none exist
    cursor.execute("SELECT COUNT(*) FROM simulated_entry_events")
    if cursor.fetchone()[0] == 0:
        demo_events = [
            (
                "door_opened",
                "Front Door",
                (now - timedelta(hours=4, minutes=12)).isoformat(),
                "SIMULATED: Front entrance door sensor opened (morning departure)",
                1,
            ),
            (
                "door_closed",
                "Front Door",
                (now - timedelta(hours=4, minutes=11)).isoformat(),
                "SIMULATED: Front entrance door sensor reported closed & secured",
                1,
            ),
            (
                "motion_detected",
                "Front Porch",
                (now - timedelta(hours=1, minutes=45)).isoformat(),
                "SIMULATED: Optical motion detected at front porch entryway",
                1,
            ),
            (
                "doorbell_ring",
                "Front Door",
                (now - timedelta(hours=1, minutes=44)).isoformat(),
                "SIMULATED: Front door chime button activated (Package delivery)",
                1,
            ),
        ]
        cursor.executemany(
            """
            INSERT INTO simulated_entry_events (event_type, location, timestamp, details, is_simulated)
            VALUES (?, ?, ?, ?, ?)
            """,
            demo_events,
        )
