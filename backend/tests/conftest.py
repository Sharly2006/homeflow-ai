"""
Pytest fixtures and isolated SQLite database setup for HomeFlow AI tests.
"""

import os
import sys
import tempfile
import pytest

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import init_db


@pytest.fixture(autouse=True)
def setup_isolated_db():
    """Create a temporary SQLite database for each test session or test."""
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_homeflow.db")
    original_env = os.environ.get("HOMEFLOW_DB_PATH")
    os.environ["HOMEFLOW_DB_PATH"] = temp_db_path

    # Initialize tables and initial seed
    init_db(seed=True)

    yield temp_db_path

    # Cleanup
    if original_env is not None:
        os.environ["HOMEFLOW_DB_PATH"] = original_env
    else:
        os.environ.pop("HOMEFLOW_DB_PATH", None)

    try:
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)
    except Exception:
        pass
