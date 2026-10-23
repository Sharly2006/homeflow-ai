"""
Tests for Household Task CRUD operations, filtering, and error handling.
"""

import pytest
from app.services.household_service import HouseholdService


def test_create_task_success():
    task = HouseholdService.create_task(
        title="Vacuum upstairs hallway",
        description="Pay special attention to rugs",
        category="cleaning",
        priority="high",
        due_date="2026-10-25",
    )
    assert task["id"] is not None
    assert task["title"] == "Vacuum upstairs hallway"
    assert task["priority"] == "high"
    assert task["is_completed"] == 0
    assert task["due_date"] == "2026-10-25"


def test_create_task_empty_title_raises_error():
    with pytest.raises(ValueError, match="Task title is required"):
        HouseholdService.create_task(title="   ")


def test_list_tasks_filtering():
    # Retrieve all seeded + new tasks
    all_tasks = HouseholdService.list_tasks(status="all")
    assert len(all_tasks) >= 3

    pending = HouseholdService.list_tasks(status="pending")
    for t in pending:
        assert t["is_completed"] == 0

    completed = HouseholdService.list_tasks(status="completed")
    for t in completed:
        assert t["is_completed"] == 1


def test_update_task():
    task = HouseholdService.create_task(title="Fix basement shelf", priority="low")
    updated = HouseholdService.update_task(task["id"], priority="high", description="Added screws")
    assert updated["priority"] == "high"
    assert updated["description"] == "Added screws"


def test_complete_task():
    task = HouseholdService.create_task(title="Replace porch lightbulb")
    assert task["is_completed"] == 0
    completed = HouseholdService.complete_task(task["id"])
    assert completed["is_completed"] == 1
    assert completed["completed_at"] is not None


def test_delete_task():
    task = HouseholdService.create_task(title="Temporary scratch task")
    task_id = task["id"]
    deleted = HouseholdService.delete_task(task_id)
    assert deleted["id"] == task_id

    # Verify task is no longer present
    with pytest.raises(KeyError):
        HouseholdService.get_task(task_id)


def test_get_nonexistent_task_raises_keyerror():
    with pytest.raises(KeyError, match="Task with ID 99999 not found"):
        HouseholdService.get_task(99999)
