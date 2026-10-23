import React, { useState } from 'react';
import { Bell, Plus, Trash2, Check, Clock, AlertTriangle } from 'lucide-react';

export default function ReminderList({ reminders = [], onToggleReminder, onDeleteReminder, onCreateReminder }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [remindAt, setRemindAt] = useState('');

  // Default time 2 hours from now
  const openModal = () => {
    const d = new Date();
    d.setHours(d.getHours() + 2);
    d.setMinutes(0);
    // Format YYYY-MM-DDTHH:MM
    const localIso = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
    setTitle('');
    setRemindAt(localIso);
    setIsModalOpen(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim() || !remindAt) return;
    onCreateReminder({
      title: title.trim(),
      remind_at: remindAt,
    });
    setIsModalOpen(false);
  };

  const formatTime = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="content-card">
      <div className="card-header">
        <div className="card-title-group">
          <Bell size={20} color="#2563eb" />
          <h2 className="card-title">Household Reminders</h2>
          <span className="badge-counter">{reminders.length}</span>
        </div>

        <button className="btn-primary" onClick={openModal} style={{ padding: '6px 12px', fontSize: '0.82rem' }}>
          <Plus size={15} />
          <span>New Reminder</span>
        </button>
      </div>

      <div style={{ fontSize: '0.74rem', color: '#64748b', marginBottom: '12px' }}>
        * In-app prototype schedule. Notifications are presented within the application interface.
      </div>

      {reminders.length === 0 ? (
        <div className="empty-state">
          <p>No active reminders scheduled. Set a reminder using the assistant or the button above.</p>
        </div>
      ) : (
        <div className="reminder-list">
          {reminders.map((rem) => (
            <div key={rem.id} className={`reminder-item ${rem.is_completed ? 'completed' : ''}`}>
              <div className="task-left">
                <div
                  className={`checkbox-custom ${rem.is_completed ? 'checked' : ''}`}
                  onClick={() => onToggleReminder(rem.id, !rem.is_completed)}
                  title={rem.is_completed ? 'Mark uncompleted' : 'Mark completed'}
                >
                  {rem.is_completed && <Check size={14} />}
                </div>

                <div className="task-content">
                  <div className={`task-title ${rem.is_completed ? 'completed' : ''}`}>
                    {rem.title}
                  </div>
                  <div className="task-meta">
                    <span className={`due-tag ${rem.is_overdue ? 'overdue' : ''}`}>
                      <Clock size={12} />
                      <span>{formatTime(rem.remind_at)}</span>
                      {rem.is_overdue && (
                        <span style={{ fontWeight: 700, marginLeft: 4 }}>• Overdue</span>
                      )}
                    </span>
                  </div>
                </div>
              </div>

              <div className="item-actions">
                <button
                  className="action-icon-btn danger"
                  title="Delete reminder"
                  onClick={() => onDeleteReminder(rem.id)}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Create Household Reminder</h3>
              <button onClick={() => setIsModalOpen(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Reminder Title *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Call grandmother, or Take out recycling"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Scheduled Date & Time *</label>
                  <input
                    type="datetime-local"
                    required
                    className="form-input"
                    value={remindAt}
                    onChange={(e) => setRemindAt(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn-primary">
                  Set Reminder
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
