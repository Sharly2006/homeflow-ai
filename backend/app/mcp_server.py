"""
Official MCP Server implementation for HomeFlow AI using Python MCP SDK (2.x MCPServer).
Exposes 10 household coordination tools connecting directly to the shared service layer.
Can be executed standalone via stdio or streamable HTTP for external MCP clients
(e.g., Claude Desktop, Antigravity, Cursor, etc.).
"""

import sys
import os
import json
import asyncio
from typing import Optional, Dict, Any, List

# Ensure parent directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mcp.server.mcpserver import MCPServer
from app.services.household_service import HouseholdService
from app.database import init_db

# Initialize MCP Server instance
mcp = MCPServer("HomeFlow AI Household MCP Server")


@mcp.tool()
def create_task(
    title: str,
    description: str = "",
    category: str = "general",
    priority: str = "medium",
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Create a new household task in SQLite database.
    
    Args:
        title: Short title or summary of task (e.g. 'Clean kitchen counters')
        description: Detailed instructions or notes
        category: Category such as 'kitchen', 'cleaning', 'maintenance', 'outdoor', 'groceries'
        priority: Task priority: 'low', 'medium', or 'high'
        due_date: Target completion date in YYYY-MM-DD format
    """
    try:
        task = HouseholdService.create_task(
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date,
        )
        return {
            "success": True,
            "message": f"Task '{task['title']}' created successfully with ID #{task['id']}.",
            "task": task,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_tasks(status: str = "all", category: Optional[str] = None) -> Dict[str, Any]:
    """
    List household tasks filtered by completion status and optional category.
    
    Args:
        status: Filter tasks by 'all', 'pending', or 'completed'
        category: Optional category filter (e.g. 'cleaning', 'kitchen')
    """
    try:
        tasks = HouseholdService.list_tasks(status=status, category=category)
        return {
            "success": True,
            "count": len(tasks),
            "status_filter": status,
            "tasks": tasks,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def update_task(
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    due_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Update details of an existing household task.
    
    Args:
        task_id: Numeric ID of the task
        title: Updated title
        description: Updated description
        category: Updated category
        priority: 'low', 'medium', or 'high'
        due_date: Updated due date in YYYY-MM-DD format
    """
    try:
        updated = HouseholdService.update_task(
            task_id=task_id,
            title=title,
            description=description,
            category=category,
            priority=priority,
            due_date=due_date,
        )
        return {
            "success": True,
            "message": f"Task #{task_id} updated successfully.",
            "task": updated,
        }
    except KeyError:
        return {"success": False, "error": f"Task #{task_id} not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def complete_task(task_id: int) -> Dict[str, Any]:
    """
    Mark a household task as completed.
    
    Args:
        task_id: Numeric ID of the task to mark as completed
    """
    try:
        completed = HouseholdService.complete_task(task_id=task_id)
        return {
            "success": True,
            "message": f"Task #{task_id} ('{completed['title']}') marked as completed.",
            "task": completed,
        }
    except KeyError:
        return {"success": False, "error": f"Task #{task_id} not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def delete_task(task_id: int) -> Dict[str, Any]:
    """
    Permanently delete a household task by ID.
    
    Args:
        task_id: Numeric ID of the task to delete
    """
    try:
        deleted = HouseholdService.delete_task(task_id=task_id)
        return {
            "success": True,
            "message": f"Task #{task_id} ('{deleted['title']}') was permanently deleted.",
            "task": deleted,
        }
    except KeyError:
        return {"success": False, "error": f"Task #{task_id} not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def create_reminder(title: str, remind_at: str) -> Dict[str, Any]:
    """
    Create a scheduled household reminder.
    
    Args:
        title: Reminder title (e.g. 'Call grandmother', 'Take out trash')
        remind_at: Scheduled reminder time in ISO 8601 (e.g. '2026-10-24T18:00:00')
    """
    try:
        reminder = HouseholdService.create_reminder(title=title, remind_at=remind_at)
        return {
            "success": True,
            "message": f"Reminder '{reminder['title']}' scheduled for {reminder['remind_at']}.",
            "reminder": reminder,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_reminders(include_completed: bool = False) -> Dict[str, Any]:
    """
    List upcoming household reminders.
    
    Args:
        include_completed: Whether to include already completed reminders
    """
    try:
        reminders = HouseholdService.list_reminders(include_completed=include_completed)
        return {
            "success": True,
            "count": len(reminders),
            "reminders": reminders,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def complete_reminder(reminder_id: int) -> Dict[str, Any]:
    """
    Mark a household reminder as completed.
    
    Args:
        reminder_id: Numeric ID of reminder
    """
    try:
        reminder = HouseholdService.complete_reminder(reminder_id=reminder_id)
        return {
            "success": True,
            "message": f"Reminder #{reminder_id} ('{reminder['title']}') marked as completed.",
            "reminder": reminder,
        }
    except KeyError:
        return {"success": False, "error": f"Reminder #{reminder_id} not found."}
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def get_daily_summary() -> Dict[str, Any]:
    """
    Generate an accurate factual summary of today's household tasks,
    upcoming reminders, and simulated entry events.
    """
    try:
        summary = HouseholdService.get_daily_summary()
        return {
            "success": True,
            "summary": summary,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@mcp.tool()
def list_simulated_entry_events(limit: int = 10) -> Dict[str, Any]:
    """
    Retrieve recent simulated entry events (e.g. front door opened, motion detected).
    All data is clearly labelled as SIMULATED.
    
    Args:
        limit: Maximum number of events to retrieve (default 10)
    """
    try:
        events = HouseholdService.list_simulated_entry_events(limit=limit)
        return {
            "success": True,
            "disclaimer": "ILLUSTRATIVE SIMULATED DATA ONLY - Not connected to real physical security hardware.",
            "count": len(events),
            "events": events,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Dictionary mapping tool names directly to their underlying functions
# for fast, seamless in-process execution by the Assistant Orchestrator
MCP_TOOLS_REGISTRY = {
    "create_task": create_task,
    "list_tasks": list_tasks,
    "update_task": update_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "create_reminder": create_reminder,
    "list_reminders": list_reminders,
    "complete_reminder": complete_reminder,
    "get_daily_summary": get_daily_summary,
    "list_simulated_entry_events": list_simulated_entry_events,
}


def main():
    """Main runner to launch the MCP server over stdio for external MCP clients."""
    init_db(seed=True)
    print("Starting HomeFlow AI MCP Server over stdio...", file=sys.stderr)
    asyncio.run(mcp.run_stdio_async())


if __name__ == "__main__":
    main()
