"""
Integration tests for FastAPI REST endpoints and status codes.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert data["mcp_tools_count"] == 10
    assert "ai_provider" in data


def test_api_tasks_crud_lifecycle():
    # 1. Create task
    payload = {
        "title": "Clean garage floor",
        "category": "maintenance",
        "priority": "medium",
        "due_date": "2026-10-27",
    }
    create_resp = client.post("/api/tasks", json=payload)
    assert create_resp.status_code == 201
    task_id = create_resp.json()["id"]

    # 2. Get task
    get_resp = client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["title"] == "Clean garage floor"

    # 3. Update task
    update_resp = client.put(f"/api/tasks/{task_id}", json={"priority": "high"})
    assert update_resp.status_code == 200
    assert update_resp.json()["priority"] == "high"

    # 4. Complete task
    comp_resp = client.post(f"/api/tasks/{task_id}/complete")
    assert comp_resp.status_code == 200
    assert comp_resp.json()["is_completed"] is True

    # 5. Delete task
    del_resp = client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 200

    # 6. Verify 404
    missing_resp = client.get(f"/api/tasks/{task_id}")
    assert missing_resp.status_code == 404


def test_api_reminders_lifecycle():
    payload = {
        "title": "Check mail delivery",
        "remind_at": "2026-10-26T16:00:00",
    }
    create_resp = client.post("/api/reminders", json=payload)
    assert create_resp.status_code == 201
    rem_id = create_resp.json()["id"]

    list_resp = client.get("/api/reminders")
    assert list_resp.status_code == 200
    assert any(r["id"] == rem_id for r in list_resp.json())

    comp_resp = client.post(f"/api/reminders/{rem_id}/complete")
    assert comp_resp.status_code == 200
    assert comp_resp.json()["is_completed"] is True

    del_resp = client.delete(f"/api/reminders/{rem_id}")
    assert del_resp.status_code == 200


def test_api_daily_summary():
    response = client.get("/api/summary")
    assert response.status_code == 200
    data = response.json()
    assert "pending_tasks_count" in data
    assert "completed_tasks_count" in data
    assert "ai_narrative" in data


def test_api_simulated_events():
    get_resp = client.get("/api/events")
    assert get_resp.status_code == 200
    events = get_resp.json()
    assert len(events) >= 1

    post_resp = client.post("/api/events", json={
        "event_type": "motion_detected",
        "location": "Garage Entry",
        "details": "Interior motion detector tripped",
    })
    assert post_resp.status_code == 201
    assert post_resp.json()["location"] == "Garage Entry"


def test_api_assistant_endpoint():
    response = client.post("/api/assistant", json={"query": "Show me all pending household tasks."})
    assert response.status_code == 200
    data = response.json()
    assert data["action_taken"] is True
    assert data["trace"]["tool_called"] == "list_tasks"


def test_api_mcp_tools_endpoint():
    response = client.get("/api/mcp/tools")
    assert response.status_code == 200
    data = response.json()
    assert data["tools_count"] == 10
    assert any(t["name"] == "create_task" for t in data["tools"])


def test_cors_preflight_for_vercel_production_origin():
    origin = "https://homeflow-ai-ochre.vercel.app"
    response = client.options(
        "/api/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin
    assert "GET" in response.headers.get("access-control-allow-methods", "")


def test_cors_request_for_vercel_assistant_endpoint():
    origin = "https://homeflow-ai-ochre.vercel.app"
    response = client.post(
        "/api/assistant",
        json={"query": "Show me all pending household tasks."},
        headers={"Origin": origin},
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin


def test_cors_preflight_for_localhost():
    origin = "http://localhost:5173"
    response = client.options(
        "/api/tasks",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == origin

