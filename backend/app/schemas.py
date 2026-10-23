"""
Pydantic schemas for data validation and API request/response handling.
"""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(default="", max_length=1000, description="Optional task details")
    category: Optional[str] = Field(default="general", max_length=50, description="Task category (e.g. cleaning, maintenance)")
    priority: Optional[str] = Field(default="medium", pattern="^(low|medium|high)$", description="Priority level: low, medium, high")
    due_date: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD format")

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v.strip() == "":
            return None
        # Verify valid date or ISO format
        cleaned = v.strip().split("T")[0]
        try:
            datetime.strptime(cleaned, "%Y-%m-%d")
            return cleaned
        except ValueError:
            raise ValueError("Due date must be in YYYY-MM-DD or ISO 8601 format.")


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    category: Optional[str] = Field(default=None, max_length=50)
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    due_date: Optional[str] = None
    is_completed: Optional[bool] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    priority: str
    due_date: Optional[str]
    is_completed: bool
    completed_at: Optional[str]
    created_at: str
    updated_at: str


class ReminderCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Reminder title")
    remind_at: str = Field(..., description="Target time for reminder (ISO 8601 or YYYY-MM-DDTHH:MM:SS)")

    @field_validator("remind_at")
    @classmethod
    def validate_remind_at(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("remind_at cannot be empty.")
        cleaned = v.strip()
        # Accept YYYY-MM-DDTHH:MM or YYYY-MM-DD HH:MM or ISO
        cleaned = cleaned.replace(" ", "T")
        try:
            # Try parsing with datetime.fromisoformat
            datetime.fromisoformat(cleaned)
            return cleaned
        except Exception:
            raise ValueError("remind_at must be a valid ISO 8601 timestamp (e.g. 2026-10-24T18:00:00).")


class ReminderUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    remind_at: Optional[str] = None
    is_completed: Optional[bool] = None


class ReminderResponse(BaseModel):
    id: int
    title: str
    remind_at: str
    is_completed: bool
    completed_at: Optional[str]
    created_at: str
    is_overdue: bool = False


class EntryEventCreate(BaseModel):
    event_type: str = Field(..., pattern="^(door_opened|door_closed|motion_detected|doorbell_ring|lock_engaged)$")
    location: str = Field(..., min_length=1, max_length=100)
    details: Optional[str] = Field(default="")


class EntryEventResponse(BaseModel):
    id: int
    event_type: str
    location: str
    timestamp: str
    details: Optional[str]
    is_simulated: bool = True


class DailySummaryResponse(BaseModel):
    date: str
    pending_tasks_count: int
    completed_tasks_count: int
    overdue_tasks_count: int
    upcoming_reminders_count: int
    today_events_count: int
    pending_tasks: List[TaskResponse]
    completed_tasks: List[TaskResponse]
    upcoming_reminders: List[ReminderResponse]
    recent_events: List[EntryEventResponse]
    ai_narrative: str


class AssistantTrace(BaseModel):
    tool_called: Optional[str] = None
    arguments: Optional[Dict[str, Any]] = None
    execution_status: str  # 'success', 'error', 'clarification_needed', 'no_tool'
    tool_result: Optional[Any] = None


class AssistantRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="User instruction in natural language")


class AssistantResponse(BaseModel):
    reply: str
    action_taken: bool
    trace: Optional[AssistantTrace] = None
    data_refreshed: bool = False
    follow_up_needed: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    mcp_tools_count: int
    ai_provider: str
