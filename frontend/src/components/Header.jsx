import React from 'react';
import { Home, Sparkles, Server, Cpu, Calendar, FileText } from 'lucide-react';

export default function Header({ health, onOpenSummary, onOpenMcpModal }) {
  const todayFormatted = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <header className="app-header">
      <div className="brand-section">
        <div className="brand-logo">
          <Home size={24} />
        </div>
        <div className="brand-titles">
          <h1>
            HomeFlow AI
            <span className="hackathon-badge">Amazon Hackathon</span>
          </h1>
          <p className="brand-subtitle">
            Intelligent Household Task & Routine Coordination Assistant
          </p>
        </div>
      </div>

      <div className="header-status-pills">
        <div className="status-pill">
          <Calendar size={14} className="text-muted" />
          <span>{todayFormatted}</span>
        </div>

        <div className="status-pill" title="Backend SQLite & FastAPI status">
          <span className={`status-dot ${health?.status === 'healthy' ? 'online' : ''}`} />
          <Server size={14} />
          <span>API: {health?.database === 'connected' ? 'Connected' : 'Offline'}</span>
        </div>

        <div
          className="status-pill cursor-pointer hover:bg-slate-100"
          title="Click to view official MCP tool specifications"
          onClick={onOpenMcpModal}
          style={{ cursor: 'pointer' }}
        >
          <span className="status-dot active" />
          <Cpu size={14} />
          <span>MCP Tools: {health?.mcp_tools_count ?? 10}</span>
        </div>

        <div className="status-pill" title="Active AI provider mode">
          <Sparkles size={14} color="#0d9488" />
          <span>{health?.ai_provider?.split(' ')[0] || 'Rule-based'}</span>
        </div>

        <button
          className="btn-secondary"
          onClick={onOpenSummary}
          title="Generate fresh daily household report"
        >
          <FileText size={16} />
          <span>Daily Summary</span>
        </button>
      </div>
    </header>
  );
}
