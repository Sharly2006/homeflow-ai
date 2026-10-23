"""
Shared household service layer for HomeFlow AI.
Encapsulates all database operations, validation, and domain logic.
Reused by the REST API, MCP server, and Assistant Orchestrator.
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.database import get_db_connection


class HouseholdService:
    """Service class providing thread-safe operations on SQLite database."""

    # -------------------------------------------------------------
    # TASK OPERATIONS
    # -------------------------------------------------------------
    @staticmethod
    def create_task(
        title: str,
        description: str = "",
        category: str = "general",
        priority: str = "medium",
        due_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new household task."""
        if not title or not title.strip():
            raise ValueError("Task title is required and cannot be empty.")

        priority = priority.lower() if priority else "medium"
        if priority not in ("low", "medium", "high"):
            priority = "medium"

        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tasks (title, description, category, priority, due_date, is_completed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 0, ?, ?)
                """,
                (title.strip(), (description or "").strip(), (category or "general").strip(), priority, due_date, now, now),
            )
            task_id = cursor.lastrowid

        return HouseholdService.get_task(task_id)

    @staticmethod
    def get_task(task_id: int) -> Dict[str, Any]:
        """Retrieve a specific task by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Task with ID {task_id} not found.")
            return dict(row)

    @staticmethod
    def list_tasks(status: str = "all", category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List tasks with optional status filter ('all', 'pending', 'completed')
        and optional category filter.
        """
        query = "SELECT * FROM tasks WHERE 1=1"
        params: List[Any] = []

        if status == "pending":
            query += " AND is_completed = 0"
        elif status == "completed":
            query += " AND is_completed = 1"

        if category:
            query += " AND LOWER(category) = LOWER(?)"
            params.append(category)

        query += " ORDER BY is_completed ASC, CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, id DESC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def find_task_by_title(keyword: str) -> Optional[Dict[str, Any]]:
        """Find the best matching pending or active task by title keyword."""
        if not keyword or not keyword.strip():
            return None
        import re
        cleaned = re.sub(r"[^\w\s]", " ", keyword.strip().lower()).strip()
        words = [w for w in cleaned.split() if len(w) > 2]

        with get_db_connection() as conn:
            cursor = conn.cursor()
            # 1. Try phrase match
            cursor.execute(
                """
                SELECT * FROM tasks 
                WHERE LOWER(title) LIKE ? 
                ORDER BY is_completed ASC, id DESC LIMIT 1
                """,
                (f"%{cleaned}%",),
            )
            row = cursor.fetchone()
            if row:
                return dict(row)

            # 2. Try individual significant words
            for word in words:
                cursor.execute(
                    """
                    SELECT * FROM tasks 
                    WHERE LOWER(title) LIKE ? 
                    ORDER BY is_completed ASC, id DESC LIMIT 1
                    """,
                    (f"%{word}%",),
                )
                row = cursor.fetchone()
                if row:
                    return dict(row)

            return None

    @staticmethod
    def update_task(task_id: int, **fields) -> Dict[str, Any]:
        """Update fields on an existing task."""
        # Ensure task exists
        HouseholdService.get_task(task_id)

        allowed = {"title", "description", "category", "priority", "due_date", "is_completed"}
        updates = []
        params = []
        now = datetime.now(timezone.utc).isoformat()

        for key, val in fields.items():
            if key in allowed and val is not None:
                if key == "is_completed":
                    val_int = 1 if val else 0
                    updates.append("is_completed = ?")
                    params.append(val_int)
                    if val_int == 1:
                        updates.append("completed_at = ?")
                        params.append(now)
                    else:
                        updates.append("completed_at = NULL")
                else:
                    updates.append(f"{key} = ?")
                    params.append(val)

        if updates:
            updates.append("updated_at = ?")
            params.append(now)
            params.append(task_id)

            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)

        return HouseholdService.get_task(task_id)

    @staticmethod
    def complete_task(task_id: int) -> Dict[str, Any]:
        """Mark a task as completed."""
        return HouseholdService.update_task(task_id, is_completed=True)

    @staticmethod
    def delete_task(task_id: int) -> Dict[str, Any]:
        """Delete a task by ID. Returns the deleted task data."""
        task = HouseholdService.get_task(task_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return task

    # -------------------------------------------------------------
    # REMINDER OPERATIONS
    # -------------------------------------------------------------
    @staticmethod
    def create_reminder(title: str, remind_at: str) -> Dict[str, Any]:
        """Create a new household reminder."""
        if not title or not title.strip():
            raise ValueError("Reminder title is required.")
        if not remind_at or not remind_at.strip():
            raise ValueError("Reminder time (remind_at) is required.")

        # Normalize and validate ISO datetime
        cleaned_time = remind_at.strip().replace(" ", "T")
        try:
            datetime.fromisoformat(cleaned_time)
        except Exception:
            raise ValueError(f"Invalid timestamp format: '{remind_at}'. Please use ISO 8601 (e.g. YYYY-MM-DDTHH:MM:SS).")

        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO reminders (title, remind_at, is_completed, created_at)
                VALUES (?, ?, 0, ?)
                """,
                (title.strip(), cleaned_time, now),
            )
            reminder_id = cursor.lastrowid

        return HouseholdService.get_reminder(reminder_id)

    @staticmethod
    def get_reminder(reminder_id: int) -> Dict[str, Any]:
        """Retrieve a specific reminder by ID."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Reminder with ID {reminder_id} not found.")
            data = dict(row)
            data["is_overdue"] = HouseholdService._check_overdue(data["remind_at"], data["is_completed"])
            return data

    @staticmethod
    def find_reminder_by_title(keyword: str) -> Optional[Dict[str, Any]]:
        """Find reminder matching keyword."""
        if not keyword:
            return None
        import re
        cleaned = re.sub(r"[^\w\s]", " ", keyword.strip().lower()).strip()
        words = [w for w in cleaned.split() if len(w) > 2]

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM reminders
                WHERE LOWER(title) LIKE ?
                ORDER BY is_completed ASC, remind_at ASC LIMIT 1
                """,
                (f"%{cleaned}%",),
            )
            row = cursor.fetchone()
            if row:
                data = dict(row)
                data["is_overdue"] = HouseholdService._check_overdue(data["remind_at"], data["is_completed"])
                return data

            for word in words:
                cursor.execute(
                    """
                    SELECT * FROM reminders
                    WHERE LOWER(title) LIKE ?
                    ORDER BY is_completed ASC, remind_at ASC LIMIT 1
                    """,
                    (f"%{word}%",),
                )
                row = cursor.fetchone()
                if row:
                    data = dict(row)
                    data["is_overdue"] = HouseholdService._check_overdue(data["remind_at"], data["is_completed"])
                    return data
            return None

    @staticmethod
    def list_reminders(include_completed: bool = False) -> List[Dict[str, Any]]:
        """List upcoming and overdue reminders."""
        query = "SELECT * FROM reminders"
        if not include_completed:
            query += " WHERE is_completed = 0"
        query += " ORDER BY is_completed ASC, remind_at ASC"

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            result = []
            for r in rows:
                item = dict(r)
                item["is_overdue"] = HouseholdService._check_overdue(item["remind_at"], item["is_completed"])
                result.append(item)
            return result

    @staticmethod
    def complete_reminder(reminder_id: int) -> Dict[str, Any]:
        """Mark a reminder as completed."""
        HouseholdService.get_reminder(reminder_id)
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE reminders
                SET is_completed = 1, completed_at = ?
                WHERE id = ?
                """,
                (now, reminder_id),
            )
        return HouseholdService.get_reminder(reminder_id)

    @staticmethod
    def delete_reminder(reminder_id: int) -> Dict[str, Any]:
        """Delete a reminder by ID."""
        reminder = HouseholdService.get_reminder(reminder_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        return reminder

    @staticmethod
    def _check_overdue(remind_at_str: str, is_completed: int) -> bool:
        """Helper to determine if an uncompleted reminder is past its scheduled time."""
        if is_completed:
            return False
        try:
            target = datetime.fromisoformat(remind_at_str)
            now = datetime.now(target.tzinfo) if target.tzinfo else datetime.now()
            return now > target
        except Exception:
            return False

    # -------------------------------------------------------------
    # SIMULATED ENTRY EVENTS
    # -------------------------------------------------------------
    @staticmethod
    def list_simulated_entry_events(limit: int = 10) -> List[Dict[str, Any]]:
        """List recent simulated entry events (door/motion sensors)."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM simulated_entry_events
                ORDER BY timestamp DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    @staticmethod
    def create_simulated_entry_event(event_type: str, location: str, details: str = "") -> Dict[str, Any]:
        """
        Record a new simulated event for live interactive demonstration.
        Labels the record strictly as SIMULATED.
        """
        now = datetime.now(timezone.utc).isoformat()
        sim_details = f"SIMULATED: {details}" if not details.startswith("SIMULATED:") else details
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO simulated_entry_events (event_type, location, timestamp, details, is_simulated)
                VALUES (?, ?, ?, ?, 1)
                """,
                (event_type, location, now, sim_details),
            )
            event_id = cursor.lastrowid

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM simulated_entry_events WHERE id = ?", (event_id,))
            return dict(cursor.fetchone())

    # -------------------------------------------------------------
    # DAILY SUMMARY CALCULATION
    # -------------------------------------------------------------
    @staticmethod
    def get_daily_summary() -> Dict[str, Any]:
        """
        Derive an accurate, factual summary of today's household activities
        strictly based on database records.
        """
        now = datetime.now(timezone.utc)
        today_date = now.strftime("%Y-%m-%d")

        all_tasks = HouseholdService.list_tasks(status="all")
        pending_tasks = [t for t in all_tasks if not t["is_completed"]]
        completed_tasks = [t for t in all_tasks if t["is_completed"]]

        # Calculate overdue tasks
        overdue_tasks = []
        for t in pending_tasks:
            due = t.get("due_date")
            if due and due < today_date:
                overdue_tasks.append(t)

        reminders = HouseholdService.list_reminders(include_completed=False)
        events = HouseholdService.list_simulated_entry_events(limit=5)

        # Build factual narrative
        pending_count = len(pending_tasks)
        completed_count = len(completed_tasks)
        reminders_count = len(reminders)
        overdue_count = len(overdue_tasks)

        narrative_parts = [
            f"Here is your household overview for {today_date}:",
            f"• Tasks: You have {pending_count} pending task{'s' if pending_count != 1 else ''} and {completed_count} completed.",
        ]
        if overdue_count > 0:
            narrative_parts.append(f"• Attention: {overdue_count} task{'s are' if overdue_count != 1 else ' is'} past the scheduled due date.")
        if reminders_count > 0:
            narrative_parts.append(f"• Reminders: {reminders_count} upcoming reminder{'s' if reminders_count != 1 else ''} scheduled.")
        else:
            narrative_parts.append("• Reminders: No active upcoming reminders at this moment.")

        if events:
            narrative_parts.append(f"• Simulated Entry Activity: {len(events)} recent events logged (latest: {events[0]['event_type'].replace('_', ' ').title()} at {events[0]['location']}).")

        return {
            "date": today_date,
            "pending_tasks_count": pending_count,
            "completed_tasks_count": completed_count,
            "overdue_tasks_count": overdue_count,
            "upcoming_reminders_count": reminders_count,
            "today_events_count": len(events),
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "upcoming_reminders": reminders,
            "recent_events": events,
            "ai_narrative": "\n".join(narrative_parts),
        }

    # -------------------------------------------------------------
    # ACTION LOGGING
    # -------------------------------------------------------------
    @staticmethod
    def log_action(
        query: str,
        tool_called: Optional[str],
        arguments: Optional[Dict[str, Any]],
        status: str,
        result: Optional[str] = None,
    ):
        """Audit logging of assistant actions and tool executions."""
        now = datetime.now(timezone.utc).isoformat()
        args_json = json.dumps(arguments) if arguments else None
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO action_logs (query, tool_called, arguments, status, result, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (query, tool_called, args_json, status, result, now),
            )

    @staticmethod
    def list_action_logs(limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent assistant activity traces."""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM action_logs
                ORDER BY id DESC LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            logs = []
            for r in rows:
                item = dict(r)
                if item.get("arguments"):
                    try:
                        item["arguments"] = json.loads(item["arguments"])
                    except Exception:
                        pass
                logs.append(item)
            return logs
