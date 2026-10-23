"""
Tests for Reminder CRUD operations, validation, and overdue detection.
"""

import pytest
from datetime import datetime, timedelta, timezone
from app.services.household_service import HouseholdService


def test_create_reminder_success():
    future_time = (datetime.now() + timedelta(hours=3)).isoformat()
    reminder = HouseholdService.create_reminder(
        title="Check oven thermometer",
        remind_at=future_time,
    )
    assert reminder["id"] is not None
    assert reminder["title"] == "Check oven thermometer"
    assert reminder["is_completed"] == 0
    assert reminder["is_overdue"] is False


def test_create_reminder_invalid_time_raises_error():
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        HouseholdService.create_reminder(
            title="Invalid reminder",
            remind_at="not-a-valid-datetime",
        )


def test_create_reminder_empty_title_raises_error():
    with pytest.raises(ValueError, match="Reminder title is required"):
        HouseholdService.create_reminder(
            title="",
            remind_at="2026-10-24T10:00:00",
        )


def test_overdue_reminder_detection():
    past_time = (datetime.now() - timedelta(hours=2)).isoformat()
    reminder = HouseholdService.create_reminder(
        title="Overdue lawn watering",
        remind_at=past_time,
    )
    assert reminder["is_overdue"] is True

    # Complete it, and check it is no longer marked overdue
    completed = HouseholdService.complete_reminder(reminder["id"])
    assert completed["is_completed"] == 1
    assert completed["is_overdue"] is False


def test_delete_reminder():
    future_time = (datetime.now() + timedelta(days=2)).isoformat()
    reminder = HouseholdService.create_reminder(
        title="Dentist checkup reminder",
        remind_at=future_time,
    )
    reminder_id = reminder["id"]
    deleted = HouseholdService.delete_reminder(reminder_id)
    assert deleted["id"] == reminder_id

    with pytest.raises(KeyError):
        HouseholdService.get_reminder(reminder_id)


def test_get_nonexistent_reminder_raises_keyerror():
    with pytest.raises(KeyError):
        HouseholdService.get_reminder(88888)
