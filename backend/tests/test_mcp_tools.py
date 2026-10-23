"""
Tests for official MCP Server tools implementation and registry.
"""

from app.mcp_server import MCP_TOOLS_REGISTRY


def test_mcp_tools_registry_contains_required_ten_tools():
    expected_tools = [
        "create_task",
        "list_tasks",
        "update_task",
        "complete_task",
        "delete_task",
        "create_reminder",
        "list_reminders",
        "complete_reminder",
        "get_daily_summary",
        "list_simulated_entry_events",
    ]
    for tool_name in expected_tools:
        assert tool_name in MCP_TOOLS_REGISTRY, f"Missing MCP tool: {tool_name}"


def test_mcp_task_tools_lifecycle():
    create_fn = MCP_TOOLS_REGISTRY["create_task"]
    list_fn = MCP_TOOLS_REGISTRY["list_tasks"]
    update_fn = MCP_TOOLS_REGISTRY["update_task"]
    complete_fn = MCP_TOOLS_REGISTRY["complete_task"]
    delete_fn = MCP_TOOLS_REGISTRY["delete_task"]

    # 1. Create
    res = create_fn(title="Clean pantry shelves", priority="high", due_date="2026-10-28")
    assert res["success"] is True
    task_id = res["task"]["id"]

    # 2. List
    list_res = list_fn(status="pending")
    assert list_res["success"] is True
    assert any(t["id"] == task_id for t in list_res["tasks"])

    # 3. Update
    update_res = update_fn(task_id=task_id, priority="low")
    assert update_res["success"] is True
    assert update_res["task"]["priority"] == "low"

    # 4. Complete
    complete_res = complete_fn(task_id=task_id)
    assert complete_res["success"] is True
    assert complete_res["task"]["is_completed"] == 1

    # 5. Delete
    delete_res = delete_fn(task_id=task_id)
    assert delete_res["success"] is True

    # 6. Delete missing ID
    err_res = delete_fn(task_id=99999)
    assert err_res["success"] is False
    assert "not found" in err_res["error"]


def test_mcp_reminder_tools_lifecycle():
    create_fn = MCP_TOOLS_REGISTRY["create_reminder"]
    list_fn = MCP_TOOLS_REGISTRY["list_reminders"]
    complete_fn = MCP_TOOLS_REGISTRY["complete_reminder"]

    # Create
    res = create_fn(title="Call pharmacy for refill", remind_at="2026-10-26T14:30:00")
    assert res["success"] is True
    rem_id = res["reminder"]["id"]

    # List
    list_res = list_fn(include_completed=False)
    assert list_res["success"] is True
    assert any(r["id"] == rem_id for r in list_res["reminders"])

    # Complete
    comp_res = complete_fn(reminder_id=rem_id)
    assert comp_res["success"] is True
    assert comp_res["reminder"]["is_completed"] == 1


def test_mcp_summary_and_events_tools():
    summary_fn = MCP_TOOLS_REGISTRY["get_daily_summary"]
    events_fn = MCP_TOOLS_REGISTRY["list_simulated_entry_events"]

    s_res = summary_fn()
    assert s_res["success"] is True
    assert "summary" in s_res

    e_res = events_fn(limit=5)
    assert e_res["success"] is True
    assert len(e_res["events"]) >= 1
    assert "SIMULATED" in e_res["disclaimer"]
