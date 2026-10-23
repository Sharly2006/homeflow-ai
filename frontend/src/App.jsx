import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import DashboardSummary from './components/DashboardSummary';
import AssistantChat from './components/AssistantChat';
import TaskList from './components/TaskList';
import ReminderList from './components/ReminderList';
import EntryEventsTimeline from './components/EntryEventsTimeline';
import DailySummaryModal from './components/DailySummaryModal';
import McpStatusModal from './components/McpStatusModal';
import { api } from './services/api';

export default function App() {
  const [health, setHealth] = useState(null);
  const [summary, setSummary] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [reminders, setReminders] = useState([]);
  const [events, setEvents] = useState([]);
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Hello! I am your HomeFlow AI household coordination assistant. I can manage tasks, organize upcoming reminders, track simulated entry events, and produce daily summaries using MCP tools.',
      trace: null,
    },
  ]);
  const [isAssistantLoading, setIsAssistantLoading] = useState(false);

  // Modals
  const [isSummaryOpen, setIsSummaryOpen] = useState(false);
  const [isMcpOpen, setIsMcpOpen] = useState(false);

  // Fetch all dashboard data
  const refreshData = useCallback(async () => {
    try {
      const [healthData, summaryData, tasksData, remindersData, eventsData] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getSummary().catch(() => null),
        api.getTasks('all').catch(() => []),
        api.getReminders(false).catch(() => []),
        api.getEntryEvents(10).catch(() => []),
      ]);

      if (healthData) setHealth(healthData);
      if (summaryData) setSummary(summaryData);
      setTasks(tasksData || []);
      setReminders(remindersData || []);
      setEvents(eventsData || []);
    } catch (err) {
      console.error('Failed refreshing dashboard:', err);
    }
  }, []);

  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Assistant Natural Language Interaction
  const handleSendMessage = async (queryText) => {
    // Append user message immediately
    setMessages((prev) => [...prev, { sender: 'user', text: queryText }]);
    setIsAssistantLoading(true);

    try {
      const res = await api.sendAssistantMessage(queryText);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: res.reply,
          trace: res.trace,
        },
      ]);

      // Automatically refresh dashboard if an action changed database state
      if (res.data_refreshed) {
        await refreshData();
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'assistant',
          text: `Error processing instruction: ${err.message}`,
          trace: { execution_status: 'error', tool_result: { error: err.message } },
        },
      ]);
    } finally {
      setIsAssistantLoading(false);
    }
  };

  // Task Handlers
  const handleToggleTask = async (taskId, isCompleted) => {
    try {
      if (isCompleted) {
        await api.completeTask(taskId);
      } else {
        await api.updateTask(taskId, { is_completed: false });
      }
      await refreshData();
    } catch (err) {
      alert(`Could not update task: ${err.message}`);
    }
  };

  const handleSaveTask = async (taskData) => {
    try {
      if (taskData.id) {
        await api.updateTask(taskData.id, taskData);
      } else {
        await api.createTask(taskData);
      }
      await refreshData();
    } catch (err) {
      alert(`Could not save task: ${err.message}`);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await api.deleteTask(taskId);
      await refreshData();
    } catch (err) {
      alert(`Could not delete task: ${err.message}`);
    }
  };

  // Reminder Handlers
  const handleToggleReminder = async (remId, isCompleted) => {
    try {
      if (isCompleted) {
        await api.completeReminder(remId);
      }
      await refreshData();
    } catch (err) {
      alert(`Could not update reminder: ${err.message}`);
    }
  };

  const handleCreateReminder = async (remData) => {
    try {
      await api.createReminder(remData);
      await refreshData();
    } catch (err) {
      alert(`Could not create reminder: ${err.message}`);
    }
  };

  const handleDeleteReminder = async (remId) => {
    try {
      await api.deleteReminder(remId);
      await refreshData();
    } catch (err) {
      alert(`Could not delete reminder: ${err.message}`);
    }
  };

  // Simulated Entry Event Trigger
  const handleTriggerEvent = async (eventData) => {
    try {
      await api.triggerSimulatedEvent(eventData);
      await refreshData();
    } catch (err) {
      alert(`Could not trigger simulated event: ${err.message}`);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <Header
        health={health}
        onOpenSummary={() => setIsSummaryOpen(true)}
        onOpenMcpModal={() => setIsMcpOpen(true)}
      />

      {/* Metric Cards */}
      <DashboardSummary summary={summary} />

      {/* Main Two-Column Layout */}
      <div className="main-layout">
        {/* Left Column: Natural Language Assistant + Household Tasks */}
        <div className="main-column-left">
          <AssistantChat
            onSendMessage={handleSendMessage}
            messages={messages}
            isLoading={isAssistantLoading}
          />

          <TaskList
            tasks={tasks}
            onToggleTask={handleToggleTask}
            onSaveTask={handleSaveTask}
            onDeleteTask={handleDeleteTask}
          />
        </div>

        {/* Right Column: Reminders + Simulated Entry Events */}
        <div className="main-column-right">
          <ReminderList
            reminders={reminders}
            onToggleReminder={handleToggleReminder}
            onDeleteReminder={handleDeleteReminder}
            onCreateReminder={handleCreateReminder}
          />

          <EntryEventsTimeline
            events={events}
            onTriggerEvent={handleTriggerEvent}
          />
        </div>
      </div>

      {/* Modals */}
      <DailySummaryModal
        summary={summary}
        isOpen={isSummaryOpen}
        onClose={() => setIsSummaryOpen(false)}
      />

      <McpStatusModal
        isOpen={isMcpOpen}
        onClose={() => setIsMcpOpen(false)}
      />
    </div>
  );
}
