"""
Tests for Assistant Orchestrator natural language intent parsing,
execution trace generation, and ambiguity follow-ups.
"""

import asyncio
import pytest
from app.assistant.orchestrator import AssistantOrchestrator


def test_assistant_add_task():
    response = asyncio.run(AssistantOrchestrator.process_request("Add a task to clean the kitchen tomorrow."))
    assert response.action_taken is True
    assert response.data_refreshed is True
    assert response.trace is not None
    assert response.trace.tool_called == "create_task"
    assert "clean the kitchen" in response.trace.arguments["title"].lower()
    assert response.trace.arguments["due_date"] is not None
    assert response.trace.execution_status == "success"
    assert "clean the kitchen" in response.reply.lower()


def test_assistant_create_reminder():
    response = asyncio.run(AssistantOrchestrator.process_request("Remind me to call my grandmother at 6 PM."))
    assert response.action_taken is True
    assert response.data_refreshed is True
    assert response.trace is not None
    assert response.trace.tool_called == "create_reminder"
    assert "call" in response.trace.arguments["title"].lower()
    assert "T18:00:00" in response.trace.arguments["remind_at"]
    assert response.trace.execution_status == "success"


def test_assistant_list_pending_tasks():
    response = asyncio.run(AssistantOrchestrator.process_request("Show me all pending household tasks."))
    assert response.action_taken is True
    assert response.trace.tool_called == "list_tasks"
    assert response.trace.arguments["status"] == "pending"
    assert "pending" in response.reply.lower()


def test_assistant_complete_task_by_keyword():
    # First create a task
    asyncio.run(AssistantOrchestrator.process_request("Add a task to clean the windows tomorrow."))
    # Now complete it
    response = asyncio.run(AssistantOrchestrator.process_request("Mark the windows task as completed."))
    assert response.action_taken is True
    assert response.trace.tool_called == "complete_task"
    assert response.trace.execution_status == "success"
    assert "marked as completed" in response.reply.lower()


def test_assistant_daily_summary():
    response = asyncio.run(AssistantOrchestrator.process_request("Give me a summary of today's household activities."))
    assert response.action_taken is True
    assert response.trace.tool_called == "get_daily_summary"
    assert "overview" in response.reply.lower() or "tasks" in response.reply.lower()


def test_assistant_simulated_entry_events():
    response = asyncio.run(AssistantOrchestrator.process_request("Show me the latest simulated entry events."))
    assert response.action_taken is True
    assert response.trace.tool_called == "list_simulated_entry_events"
    assert "simulated" in response.reply.lower()


def test_assistant_ambiguous_task_requests_clarification():
    response = asyncio.run(AssistantOrchestrator.process_request("Add a task"))
    assert response.action_taken is False
    assert response.follow_up_needed is True
    assert "title" in response.reply.lower() or "what task" in response.reply.lower()


def test_assistant_ambiguous_reminder_requests_clarification():
    response = asyncio.run(AssistantOrchestrator.process_request("Remind me to call the electrician"))
    # Time is missing
    assert response.action_taken is False
    assert response.follow_up_needed is True
    assert "when" in response.reply.lower() or "time" in response.reply.lower()
