"""
REST API routes for HomeFlow AI.
Provides clean, documented endpoints for frontend integration and tool execution.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
    EntryEventCreate,
    EntryEventResponse,
    DailySummaryResponse,
    AssistantRequest,
    AssistantResponse,
    HealthResponse,
)
from app.services.household_service import HouseholdService
from app.assistant.orchestrator import AssistantOrchestrator
from app.assistant.llm_provider import LLMProvider
from app.mcp_server import MCP_TOOLS_REGISTRY

router = APIRouter(prefix="/api")


# -------------------------------------------------------------
# SYSTEM & HEALTH
# -------------------------------------------------------------
@router.get("/health", response_model=HealthResponse, tags=["System"])
async def check_health():
    """Returns backend, database, MCP layer, and AI provider health status."""
    llm_active, provider_name = LLMProvider.get_provider_status()
    # Verify DB connectivity
    try:
        tasks = HouseholdService.list_tasks(status="all")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return HealthResponse(
        status="healthy",
        version="1.0.0-hackathon",
        database=db_status,
        mcp_tools_count=len(MCP_TOOLS_REGISTRY),
        ai_provider=provider_name,
    )


# -------------------------------------------------------------
# NATURAL LANGUAGE ASSISTANT
# -------------------------------------------------------------
@router.post("/assistant", response_model=AssistantResponse, tags=["Assistant"])
async def process_assistant_command(req: AssistantRequest):
    """
    Process natural language commands through the Assistant Orchestration layer.
    Executes tools via MCP layer, logs execution trace, and returns friendly response.
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    return await AssistantOrchestrator.process_request(req.query)


@router.get("/actions", tags=["Assistant"])
async def list_action_traces(limit: int = Query(default=10, ge=1, le=50)):
    """Retrieve recent assistant tool execution audit traces."""
    return HouseholdService.list_action_logs(limit=limit)


# -------------------------------------------------------------
# HOUSEHOLD TASKS CRUD
# -------------------------------------------------------------
@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
async def create_task(task_in: TaskCreate):
    """Create a new household task."""
    try:
        return HouseholdService.create_task(
            title=task_in.title,
            description=task_in.description or "",
            category=task_in.category or "general",
            priority=task_in.priority or "medium",
            due_date=task_in.due_date,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tasks", response_model=List[TaskResponse], tags=["Tasks"])
async def list_tasks(
    status: str = Query(default="all", pattern="^(all|pending|completed)$"),
    category: Optional[str] = Query(default=None),
):
    """List tasks filtered by status and optional category."""
    return HouseholdService.list_tasks(status=status, category=category)


@router.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: int):
    """Get single task by ID."""
    try:
        return HouseholdService.get_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")


@router.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def update_task(task_id: int, updates: TaskUpdate):
    """Update task fields."""
    try:
        return HouseholdService.update_task(
            task_id=task_id,
            title=updates.title,
            description=updates.description,
            category=updates.category,
            priority=updates.priority,
            due_date=updates.due_date,
            is_completed=updates.is_completed,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tasks/{task_id}/complete", response_model=TaskResponse, tags=["Tasks"])
async def complete_task(task_id: int):
    """Mark a task as completed."""
    try:
        return HouseholdService.complete_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")


@router.delete("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def delete_task(task_id: int):
    """Permanently delete a task."""
    try:
        return HouseholdService.delete_task(task_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")


# -------------------------------------------------------------
# REMINDERS CRUD
# -------------------------------------------------------------
@router.post("/reminders", response_model=ReminderResponse, status_code=status.HTTP_201_CREATED, tags=["Reminders"])
async def create_reminder(rem_in: ReminderCreate):
    """Create a new household reminder."""
    try:
        return HouseholdService.create_reminder(
            title=rem_in.title,
            remind_at=rem_in.remind_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/reminders", response_model=List[ReminderResponse], tags=["Reminders"])
async def list_reminders(include_completed: bool = Query(default=False)):
    """List scheduled reminders with overdue indicators."""
    return HouseholdService.list_reminders(include_completed=include_completed)


@router.post("/reminders/{reminder_id}/complete", response_model=ReminderResponse, tags=["Reminders"])
async def complete_reminder(reminder_id: int):
    """Mark a reminder as completed."""
    try:
        return HouseholdService.complete_reminder(reminder_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Reminder with ID {reminder_id} not found.")


@router.delete("/reminders/{reminder_id}", response_model=ReminderResponse, tags=["Reminders"])
async def delete_reminder(reminder_id: int):
    """Delete a reminder."""
    try:
        return HouseholdService.delete_reminder(reminder_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Reminder with ID {reminder_id} not found.")


# -------------------------------------------------------------
# DAILY SUMMARY
# -------------------------------------------------------------
@router.get("/summary", response_model=DailySummaryResponse, tags=["Summary"])
async def get_daily_summary():
    """Derive full daily summary of tasks, reminders, and entry activity."""
    return HouseholdService.get_daily_summary()


# -------------------------------------------------------------
# SIMULATED ENTRY EVENTS
# -------------------------------------------------------------
@router.get("/events", response_model=List[EntryEventResponse], tags=["Events"])
async def list_events(limit: int = Query(default=15, ge=1, le=50)):
    """Retrieve simulated entrance and sensor activity records."""
    return HouseholdService.list_simulated_entry_events(limit=limit)


@router.post("/events", response_model=EntryEventResponse, status_code=status.HTTP_201_CREATED, tags=["Events"])
async def trigger_simulated_event(event_in: EntryEventCreate):
    """
    Trigger a simulated entry event for live hackathon demonstration
    (e.g. Front Door Opened, Porch Motion Detected).
    """
    return HouseholdService.create_simulated_entry_event(
        event_type=event_in.event_type,
        location=event_in.location,
        details=event_in.details or f"Interactive demo: {event_in.event_type.replace('_', ' ').title()}",
    )


# -------------------------------------------------------------
# MCP SERVER INSPECTION
# -------------------------------------------------------------
@router.get("/mcp/tools", tags=["MCP"])
async def list_mcp_tools():
    """
    List all 10 tools currently registered on the official MCP Server,
    providing full transparency into the MCP architecture.
    """
    tools = []
    for name, fn in MCP_TOOLS_REGISTRY.items():
        tools.append({
            "name": name,
            "description": (fn.__doc__ or "").strip(),
        })
    return {
        "server_name": "HomeFlow AI Household MCP Server",
        "mcp_sdk_version": "2.3.0",
        "tools_count": len(tools),
        "tools": tools,
    }
