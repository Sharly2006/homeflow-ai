"""
Assistant Orchestration Layer for HomeFlow AI.
Parses natural language requests, validates parameters, handles ambiguities,
executes tools via the MCP tool registry, logs audit traces, and generates
human-readable conversational responses.
"""

import re
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple

from app.mcp_server import MCP_TOOLS_REGISTRY
from app.services.household_service import HouseholdService
from app.assistant.llm_provider import LLMProvider
from app.schemas import AssistantResponse, AssistantTrace


class AssistantOrchestrator:
    """Orchestrates NL request processing, tool dispatch, and trace generation."""

    @classmethod
    async def process_request(cls, query: str) -> AssistantResponse:
        """Main entrypoint for processing user natural language requests."""
        query_clean = query.strip()
        now = datetime.now()
        current_iso = now.isoformat()

        # Step 1: Try LLM first if configured
        llm_active, provider_name = LLMProvider.get_provider_status()
        llm_plan = None
        if llm_active:
            llm_plan = await LLMProvider.parse_with_llm(query_clean, current_iso)

        # Step 2: Use LLM plan if valid, else fall back to rule-based engine
        if llm_plan and "tool" in llm_plan:
            tool_name = llm_plan.get("tool")
            args = llm_plan.get("arguments", {})
            clarification = llm_plan.get("clarification_needed")
            if clarification:
                HouseholdService.log_action(query_clean, None, None, "clarification_needed", clarification)
                return AssistantResponse(
                    reply=clarification,
                    action_taken=False,
                    trace=AssistantTrace(execution_status="clarification_needed"),
                    follow_up_needed=True,
                )
        else:
            # Rule-based intent analysis
            tool_name, args, clarification = cls._parse_rule_based(query_clean, now)
            if clarification:
                HouseholdService.log_action(query_clean, None, None, "clarification_needed", clarification)
                return AssistantResponse(
                    reply=clarification,
                    action_taken=False,
                    trace=AssistantTrace(execution_status="clarification_needed"),
                    follow_up_needed=True,
                )

        if not tool_name or tool_name not in MCP_TOOLS_REGISTRY:
            reply = (
                "I couldn't identify a specific household tool for that request. "
                "You can ask me to add tasks, set reminders, show pending chores, "
                "view daily summaries, or check simulated entry events."
            )
            HouseholdService.log_action(query_clean, None, None, "no_tool", reply)
            return AssistantResponse(
                reply=reply,
                action_taken=False,
                trace=AssistantTrace(execution_status="no_tool"),
                follow_up_needed=False,
            )

        # Step 3: Execute tool via MCP Tool Layer
        tool_fn = MCP_TOOLS_REGISTRY[tool_name]
        try:
            result = tool_fn(**args)
            success = result.get("success", False)
            status = "success" if success else "error"
            
            # Format friendly natural-language reply
            reply = cls._format_reply(tool_name, args, result)
            data_refreshed = tool_name in (
                "create_task", "update_task", "complete_task", "delete_task",
                "create_reminder", "complete_reminder"
            ) and success

            HouseholdService.log_action(
                query=query_clean,
                tool_called=tool_name,
                arguments=args,
                status=status,
                result=str(result),
            )

            return AssistantResponse(
                reply=reply,
                action_taken=True,
                data_refreshed=data_refreshed,
                trace=AssistantTrace(
                    tool_called=tool_name,
                    arguments=args,
                    execution_status=status,
                    tool_result=result,
                ),
            )
        except Exception as e:
            error_msg = f"Failed executing tool '{tool_name}': {str(e)}"
            HouseholdService.log_action(query_clean, tool_name, args, "error", error_msg)
            return AssistantResponse(
                reply=f"Sorry, an error occurred while executing {tool_name}: {str(e)}",
                action_taken=False,
                trace=AssistantTrace(
                    tool_called=tool_name,
                    arguments=args,
                    execution_status="error",
                    tool_result={"error": str(e)},
                ),
            )

    @classmethod
    def _parse_rule_based(cls, q: str, now: datetime) -> Tuple[Optional[str], Dict[str, Any], Optional[str]]:
        """
        Deterministic, robust rule-based parsing supporting all required hackathon demo flows.
        """
        lower = q.lower()

        # 1. DAILY SUMMARY
        if any(p in lower for p in ["summary", "overview", "what's happening today", "status report", "activities today"]):
            return "get_daily_summary", {}, None

        # 2. SIMULATED ENTRY EVENTS
        if any(p in lower for p in ["entry event", "entry-event", "door opened", "door motion", "sensors", "who came", "front door activity", "security event"]):
            return "list_simulated_entry_events", {"limit": 10}, None

        # 3. COMPLETE TASK
        # e.g., "Mark the kitchen cleaning task as completed", "Complete task 2", "Mark task #3 as done"
        if any(p in lower for p in ["mark", "complete", "finish", "done"]):
            if "reminder" in lower:
                # Complete reminder
                id_match = re.search(r"#?(\d+)", lower)
                if id_match:
                    return "complete_reminder", {"reminder_id": int(id_match.group(1))}, None
                # Search by keyword
                keyword = re.sub(r"\b(mark|complete|the|reminder|as|done|finished)\b|[^\w\s]", " ", lower).strip()
                rem = HouseholdService.find_reminder_by_title(keyword)
                if rem:
                    return "complete_reminder", {"reminder_id": rem["id"]}, None
                return None, {}, "Which reminder would you like to mark as completed? Please specify the title or ID."

            # Complete task
            id_match = re.search(r"#?(\d+)", lower)
            if id_match:
                return "complete_task", {"task_id": int(id_match.group(1))}, None

            # Extract task name keyword
            # e.g. "mark the kitchen cleaning task as completed" -> keyword "kitchen cleaning"
            cleaned_kw = re.sub(r"\b(mark|the|task|as|completed|complete|done|finished)\b|[^\w\s]", " ", lower).strip()
            if cleaned_kw:
                found_task = HouseholdService.find_task_by_title(cleaned_kw)
                if found_task:
                    return "complete_task", {"task_id": found_task["id"]}, None
            return None, {}, "Which task would you like to mark as completed? Please specify the task title or ID."

        # 4. DELETE TASK
        if any(p in lower for p in ["delete task", "remove task"]):
            id_match = re.search(r"#?(\d+)", lower)
            if id_match:
                return "delete_task", {"task_id": int(id_match.group(1))}, None
            cleaned_kw = re.sub(r"(delete|remove|task|the|#)", "", lower).strip()
            if cleaned_kw:
                found_task = HouseholdService.find_task_by_title(cleaned_kw)
                if found_task:
                    return "delete_task", {"task_id": found_task["id"]}, None
            return None, {}, "Which task would you like to delete? Please specify the task title or ID."

        # 5. CREATE REMINDER
        # e.g., "Remind me to call my grandmother at 6 PM", "Set a reminder to take out trash tomorrow at 8 AM"
        if "remind" in lower:
            # Check if user just typed "Remind me" without content
            if lower.strip() in ["remind", "remind me", "set reminder", "create reminder"]:
                return None, {}, "What would you like to be reminded of, and when? (For example: 'Remind me to call grandma at 6 PM')"

            # Extract title and time
            # Target patterns: "remind me to <title> at/on <time>"
            match = re.search(r"remind(?: me)?(?: to)?\s+(.+)", q, re.IGNORECASE)
            full_content = match.group(1) if match else q

            # Extract time if present
            remind_at = cls._extract_datetime(full_content, now)
            if not remind_at:
                return None, {}, f"When would you like to be reminded to {full_content.strip()}? (e.g. 'at 6 PM' or 'tomorrow at 9 AM')"

            # Clean reminder title
            title = re.sub(r"\s+(?:at|on|tomorrow|today|tonight)\s+.*$", "", full_content, flags=re.IGNORECASE).strip()
            title = re.sub(r"^to\s+", "", title, flags=re.IGNORECASE).strip()
            if not title:
                title = full_content.strip()

            return "create_reminder", {"title": title.capitalize(), "remind_at": remind_at}, None

        # 6. LIST REMINDERS
        if any(p in lower for p in ["reminders", "list reminders", "show reminders", "upcoming reminders"]):
            return "list_reminders", {"include_completed": False}, None

        # 7. CREATE TASK
        # e.g., "Add a task to clean the kitchen tomorrow", "Create a task to buy groceries"
        if any(p in lower for p in ["add a task", "add task", "create a task", "create task", "new task"]):
            # Check if user just typed "Add a task" without title
            if lower.strip() in ["add a task", "add task", "create a task", "create task", "new task"]:
                return None, {}, "What task would you like to add? Please specify a title (e.g. 'Clean the kitchen counters')."

            # Extract title and possible due date
            match = re.search(r"(?:add|create)(?:\s+a)?\s+task(?:\s+to)?\s+(.+)", q, re.IGNORECASE)
            content = match.group(1) if match else q

            # Check for due date in string (e.g. 'tomorrow', 'today', 'on Friday', 'YYYY-MM-DD')
            due_date = cls._extract_date(content, now)
            priority = "high" if "high priority" in lower or "urgent" in lower else ("low" if "low priority" in lower else "medium")

            # Clean title
            title = re.sub(r"\s+(?:tomorrow|today|on\s+\w+|by\s+\w+|next\s+\w+).*$", "", content, flags=re.IGNORECASE).strip()
            title = re.sub(r"\s+with\s+(?:high|medium|low)\s+priority.*$", "", title, flags=re.IGNORECASE).strip()
            title = re.sub(r"^to\s+", "", title, flags=re.IGNORECASE).strip()

            category = "general"
            for cat in ["kitchen", "cleaning", "maintenance", "groceries", "garden", "chores"]:
                if cat in title.lower():
                    category = cat
                    break

            if not title:
                return None, {}, "What is the title of the task you would like to add?"

            return "create_task", {
                "title": title.capitalize(),
                "description": "",
                "category": category,
                "priority": priority,
                "due_date": due_date,
            }, None

        # 8. LIST TASKS
        # e.g., "Show me all pending household tasks", "List tasks", "What tasks do I have?"
        if any(p in lower for p in ["tasks", "list tasks", "show tasks", "pending tasks", "completed tasks", "chores"]):
            status = "pending" if "pending" in lower else ("completed" if "completed" in lower else "all")
            return "list_tasks", {"status": status}, None

        return None, {}, None

    @classmethod
    def _extract_date(cls, text: str, now: datetime) -> Optional[str]:
        """Extract a date string YYYY-MM-DD from user prompt."""
        lower = text.lower()
        if "tomorrow" in lower:
            return (now + timedelta(days=1)).strftime("%Y-%m-%d")
        if "today" in lower:
            return now.strftime("%Y-%m-%d")
        # Direct YYYY-MM-DD regex
        match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if match:
            return match.group(1)
        return None

    @classmethod
    def _extract_datetime(cls, text: str, now: datetime) -> Optional[str]:
        """Extract target ISO datetime for a reminder."""
        lower = text.lower()
        target_day = now
        if "tomorrow" in lower:
            target_day = now + timedelta(days=1)

        # Look for time patterns: "6 PM", "6:30 PM", "18:00", "6am"
        time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", lower)
        if time_match:
            hours = int(time_match.group(1))
            minutes = int(time_match.group(2) or 0)
            ampm = time_match.group(3).lower()
            if ampm == "pm" and hours < 12:
                hours += 12
            elif ampm == "am" and hours == 12:
                hours = 0
            return target_day.replace(hour=hours, minute=minutes, second=0, microsecond=0).isoformat()

        # Look for 24-hour pattern: "at 18:00"
        time_24 = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", lower)
        if time_24:
            hours = int(time_24.group(1))
            minutes = int(time_24.group(2))
            return target_day.replace(hour=hours, minute=minutes, second=0, microsecond=0).isoformat()

        # Default fallback to 1 hour from now if user said "in an hour"
        if "in an hour" in lower:
            return (now + timedelta(hours=1)).isoformat()

        return None

    @classmethod
    def _format_reply(cls, tool_name: str, args: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Construct user-friendly natural language answer from real tool outcome."""
        if not result.get("success", False):
            return f"I couldn't complete that action: {result.get('error', 'Unknown error')}."

        if tool_name == "create_task":
            task = result.get("task", {})
            due = f" due on {task.get('due_date')}" if task.get("due_date") else ""
            return f"I've added the task '{task.get('title')}' (#{task.get('id')}){due} with {task.get('priority')} priority."

        if tool_name == "create_reminder":
            rem = result.get("reminder", {})
            return f"Reminder scheduled: '{rem.get('title')}' for {rem.get('remind_at')}."

        if tool_name == "complete_task":
            task = result.get("task", {})
            return f"Great job! Task #{task.get('id')} ('{task.get('title')}') has been marked as completed."

        if tool_name == "complete_reminder":
            rem = result.get("reminder", {})
            return f"Reminder #{rem.get('id')} ('{rem.get('title')}') marked as completed."

        if tool_name == "delete_task":
            task = result.get("task", {})
            return f"Task #{task.get('id')} ('{task.get('title')}') was deleted."

        if tool_name == "list_tasks":
            tasks = result.get("tasks", [])
            status = result.get("status_filter", "all")
            if not tasks:
                return f"You currently have no {status} tasks."
            lines = [f"Found {len(tasks)} {status} task{'s' if len(tasks) != 1 else ''}:"]
            for t in tasks[:6]:
                status_symbol = "✓" if t.get("is_completed") else "○"
                due_info = f" (Due: {t.get('due_date')})" if t.get("due_date") else ""
                lines.append(f"• [{status_symbol}] #{t.get('id')}: {t.get('title')}{due_info}")
            if len(tasks) > 6:
                lines.append(f"...and {len(tasks) - 6} more displayed on your dashboard.")
            return "\n".join(lines)

        if tool_name == "list_reminders":
            reminders = result.get("reminders", [])
            if not reminders:
                return "You have no upcoming reminders scheduled right now."
            lines = [f"Here are your upcoming reminders ({len(reminders)}):"]
            for r in reminders:
                lines.append(f"• #{r.get('id')}: {r.get('title')} at {r.get('remind_at')}")
            return "\n".join(lines)

        if tool_name == "get_daily_summary":
            summary = result.get("summary", {})
            return summary.get("ai_narrative", "Daily summary generated successfully.")

        if tool_name == "list_simulated_entry_events":
            events = result.get("events", [])
            if not events:
                return "No simulated entry events found in the event log."
            lines = ["Here are the recent simulated entry events (Simulated Data Only):"]
            for e in events[:5]:
                t_str = e.get("timestamp", "").split("T")[-1][:5]
                lines.append(f"• [{t_str}] {e.get('event_type').replace('_', ' ').title()} - {e.get('location')} ({e.get('details')})")
            return "\n".join(lines)

        return result.get("message", "Action executed successfully.")
