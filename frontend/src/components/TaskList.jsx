import React, { useState } from 'react';
import { CheckSquare, Plus, Trash2, Edit3, Check, Calendar, AlertCircle } from 'lucide-react';

export default function TaskList({ tasks = [], onToggleTask, onDeleteTask, onSaveTask }) {
  const [filter, setFilter] = useState('all');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [taskToDelete, setTaskToDelete] = useState(null);

  // Form states
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('general');
  const [priority, setPriority] = useState('medium');
  const [dueDate, setDueDate] = useState('');

  const openCreateModal = () => {
    setEditingTask(null);
    setTitle('');
    setDescription('');
    setCategory('general');
    setPriority('medium');
    setDueDate('');
    setIsModalOpen(true);
  };

  const openEditModal = (task) => {
    setEditingTask(task);
    setTitle(task.title || '');
    setDescription(task.description || '');
    setCategory(task.category || 'general');
    setPriority(task.priority || 'medium');
    setDueDate(task.due_date || '');
    setIsModalOpen(true);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;

    onSaveTask({
      id: editingTask?.id,
      title: title.trim(),
      description: description.trim(),
      category: category.trim(),
      priority,
      due_date: dueDate || null,
    });

    setIsModalOpen(false);
  };

  const confirmDelete = () => {
    if (taskToDelete) {
      onDeleteTask(taskToDelete.id);
      setTaskToDelete(null);
    }
  };

  // Filter tasks
  const filteredTasks = tasks.filter((t) => {
    if (filter === 'pending') return !t.is_completed;
    if (filter === 'completed') return t.is_completed;
    return true;
  });

  const todayStr = new Date().toISOString().split('T')[0];

  return (
    <div className="content-card">
      <div className="card-header">
        <div className="card-title-group">
          <CheckSquare size={20} color="#0d9488" />
          <h2 className="card-title">Household Tasks</h2>
          <span className="badge-counter">{filteredTasks.length}</span>
        </div>

        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <div className="filters-bar">
            {['all', 'pending', 'completed'].map((f) => (
              <button
                key={f}
                className={`filter-btn ${filter === f ? 'active' : ''}`}
                onClick={() => setFilter(f)}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>

          <button className="btn-primary" onClick={openCreateModal} style={{ padding: '6px 12px', fontSize: '0.82rem' }}>
            <Plus size={15} />
            <span>New Task</span>
          </button>
        </div>
      </div>

      {filteredTasks.length === 0 ? (
        <div className="empty-state">
          <p>No {filter !== 'all' ? filter : ''} household tasks found.</p>
        </div>
      ) : (
        <div className="task-list">
          {filteredTasks.map((task) => {
            const isOverdue = !task.is_completed && task.due_date && task.due_date < todayStr;

            return (
              <div key={task.id} className={`task-item ${task.is_completed ? 'completed' : ''}`}>
                <div className="task-left">
                  <div
                    className={`checkbox-custom ${task.is_completed ? 'checked' : ''}`}
                    onClick={() => onToggleTask(task.id, !task.is_completed)}
                    title={task.is_completed ? 'Mark pending' : 'Mark completed'}
                  >
                    {task.is_completed && <Check size={14} />}
                  </div>

                  <div className="task-content">
                    <div className={`task-title ${task.is_completed ? 'completed' : ''}`}>
                      {task.title}
                    </div>
                    {task.description && <div className="task-desc">{task.description}</div>}

                    <div className="task-meta">
                      <span className={`priority-tag ${task.priority}`}>{task.priority}</span>
                      <span className="category-tag">{task.category}</span>
                      {task.due_date && (
                        <span className={`due-tag ${isOverdue ? 'overdue' : ''}`}>
                          <Calendar size={12} />
                          <span>{task.due_date} {isOverdue && '(Overdue)'}</span>
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="item-actions">
                  <button
                    className="action-icon-btn"
                    title="Edit task"
                    onClick={() => openEditModal(task)}
                  >
                    <Edit3 size={15} />
                  </button>
                  <button
                    className="action-icon-btn danger"
                    title="Delete task"
                    onClick={() => setTaskToDelete(task)}
                  >
                    <Trash2 size={15} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Create / Edit Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{editingTask ? 'Edit Household Task' : 'Add Household Task'}</h3>
              <button onClick={() => setIsModalOpen(false)}>✕</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Task Title *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    placeholder="e.g. Inspect bathroom sink plumbing"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description / Instructions</label>
                  <textarea
                    rows={2}
                    className="form-textarea"
                    placeholder="Optional notes or details"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                  />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                  <div className="form-group">
                    <label className="form-label">Category</label>
                    <select
                      className="form-select"
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                    >
                      <option value="general">General</option>
                      <option value="cleaning">Cleaning</option>
                      <option value="kitchen">Kitchen</option>
                      <option value="maintenance">Maintenance</option>
                      <option value="outdoor">Outdoor / Garden</option>
                      <option value="groceries">Groceries</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Priority</label>
                    <select
                      className="form-select"
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                    >
                      <option value="low">Low</option>
                      <option value="medium">Medium</option>
                      <option value="high">High</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label className="form-label">Due Date</label>
                  <input
                    type="date"
                    className="form-input"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
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
                  {editingTask ? 'Save Changes' : 'Create Task'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {taskToDelete && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ maxWidth: '420px' }}>
            <div className="modal-header">
              <h3>Confirm Task Deletion</h3>
              <button onClick={() => setTaskToDelete(null)}>✕</button>
            </div>
            <div className="modal-body">
              <p style={{ color: '#475569', fontSize: '0.93rem' }}>
                Are you sure you want to permanently delete task <strong>"{taskToDelete.title}"</strong>?
              </p>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setTaskToDelete(null)}>
                Cancel
              </button>
              <button
                className="btn-primary"
                style={{ background: '#dc2626' }}
                onClick={confirmDelete}
              >
                Delete Task
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
