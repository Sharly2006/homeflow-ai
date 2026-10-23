import React, { useState } from 'react';
import { FileText, Copy, Check, X, AlertCircle } from 'lucide-react';

export default function DailySummaryModal({ summary, isOpen, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !summary) return null;

  const copyToClipboard = () => {
    if (!summary?.ai_narrative) return;
    navigator.clipboard.writeText(summary.ai_narrative);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '600px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileText size={20} color="#0d9488" />
            <h3>Daily Household Summary ({summary.date})</h3>
          </div>
          <button onClick={onClose} style={{ fontSize: '1.2rem', color: '#64748b' }}>✕</button>
        </div>

        <div className="modal-body">
          {/* Key Metric Badges */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', marginBottom: '16px' }}>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 600 }}>PENDING</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a' }}>{summary.pending_tasks_count}</div>
            </div>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 600 }}>COMPLETED</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#059669' }}>{summary.completed_tasks_count}</div>
            </div>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 600 }}>REMINDERS</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#2563eb' }}>{summary.upcoming_reminders_count}</div>
            </div>
            <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
              <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: 600 }}>EVENTS</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 800, color: '#d97706' }}>{summary.today_events_count}</div>
            </div>
          </div>

          {/* Factual Narrative */}
          <div
            style={{
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: '10px',
              padding: '16px',
              fontFamily: 'inherit',
              fontSize: '0.92rem',
              lineHeight: '1.6',
              whiteSpace: 'pre-line',
              color: '#1e293b',
            }}
          >
            {summary.ai_narrative}
          </div>

          <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#64748b' }}>
            ℹ️ This overview is derived directly from your live SQLite database records.
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-secondary" onClick={copyToClipboard}>
            {copied ? <Check size={15} color="#059669" /> : <Copy size={15} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy Summary'}</span>
          </button>
          <button className="btn-primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
