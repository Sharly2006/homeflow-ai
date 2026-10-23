"""
Tests for Daily Summary calculations and Simulated Entry Event handling.
"""

from datetime import datetime, timedelta, timezone
from app.services.household_service import HouseholdService


def test_daily_summary_calculation():
    # Insert specific known tasks and reminders
    HouseholdService.create_task(title="Pending Task A", due_date="2026-10-30")
    HouseholdService.create_task(title="Overdue Task B", due_date="2020-01-01")  # overdue

    summary = HouseholdService.get_daily_summary()

    assert "pending_tasks_count" in summary
    assert "completed_tasks_count" in summary
    assert "overdue_tasks_count" in summary
    assert "upcoming_reminders_count" in summary
    assert "today_events_count" in summary
    assert "ai_narrative" in summary

    assert summary["pending_tasks_count"] >= 2
    assert summary["overdue_tasks_count"] >= 1
    assert "household overview" in summary["ai_narrative"].lower()


def test_simulated_entry_events_retrieval_and_creation():
    # Initial seeded events
    events = HouseholdService.list_simulated_entry_events(limit=10)
    assert len(events) >= 1
    for ev in events:
        assert ev["is_simulated"] == 1
        assert "SIMULATED:" in ev["details"]

    # Trigger a new simulated event
    new_ev = HouseholdService.create_simulated_entry_event(
        event_type="door_opened",
        location="Back Patio",
        details="Patio sliding glass sensor triggered",
    )
    assert new_ev["event_type"] == "door_opened"
    assert new_ev["location"] == "Back Patio"
    assert new_ev["is_simulated"] == 1
    assert "SIMULATED:" in new_ev["details"]

    # Verify it appears at the top of recent events
    recent = HouseholdService.list_simulated_entry_events(limit=1)
    assert recent[0]["id"] == new_ev["id"]
