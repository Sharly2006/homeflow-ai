import React from 'react';
import { CheckCircle2, Clock, Bell, ShieldAlert } from 'lucide-react';

export default function DashboardSummary({ summary }) {
  const pendingCount = summary?.pending_tasks_count ?? 0;
  const completedCount = summary?.completed_tasks_count ?? 0;
  const remindersCount = summary?.upcoming_reminders_count ?? 0;
  const eventsCount = summary?.today_events_count ?? 0;
  const overdueCount = summary?.overdue_tasks_count ?? 0;

  return (
    <div className="summary-grid">
      <div className="summary-card">
        <div className="summary-info">
          <div className="summary-label">Pending Chores</div>
          <div className="summary-value">{pendingCount}</div>
          {overdueCount > 0 && (
            <span style={{ fontSize: '0.74rem', color: '#dc2626', fontWeight: 600 }}>
              ⚠️ {overdueCount} task{overdueCount !== 1 ? 's' : ''} overdue
            </span>
          )}
        </div>
        <div className="summary-icon-box teal">
          <Clock size={24} />
        </div>
      </div>

      <div className="summary-card">
        <div className="summary-info">
          <div className="summary-label">Completed Tasks</div>
          <div className="summary-value">{completedCount}</div>
          <span style={{ fontSize: '0.74rem', color: '#059669', fontWeight: 600 }}>
            Done & verified
          </span>
        </div>
        <div className="summary-icon-box emerald">
          <CheckCircle2 size={24} />
        </div>
      </div>

      <div className="summary-card">
        <div className="summary-info">
          <div className="summary-label">Upcoming Reminders</div>
          <div className="summary-value">{remindersCount}</div>
          <span style={{ fontSize: '0.74rem', color: '#2563eb', fontWeight: 600 }}>
            In-app schedule
          </span>
        </div>
        <div className="summary-icon-box blue">
          <Bell size={24} />
        </div>
      </div>

      <div className="summary-card">
        <div className="summary-info">
          <div className="summary-label">Simulated Events</div>
          <div className="summary-value">{eventsCount}</div>
          <span style={{ fontSize: '0.74rem', color: '#d97706', fontWeight: 600 }}>
            SIMULATED Sensor feed
          </span>
        </div>
        <div className="summary-icon-box amber">
          <ShieldAlert size={24} />
        </div>
      </div>
    </div>
  );
}
