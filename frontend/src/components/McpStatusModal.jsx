import React, { useState, useEffect } from 'react';
import { Cpu, Copy, Check, Terminal, Code2 } from 'lucide-react';
import { api } from '../services/api';

export default function McpStatusModal({ isOpen, onClose }) {
  const [toolsData, setToolsData] = useState(null);
  const [copiedConfig, setCopiedConfig] = useState(false);

  useEffect(() => {
    if (isOpen) {
      api.getMcpTools()
        .then((data) => setToolsData(data))
        .catch((err) => console.error('Failed to load MCP tools:', err));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const mcpConfigSnippet = JSON.stringify(
    {
      mcpServers: {
        homeflow: {
          command: "python",
          args: [
            "-m",
            "app.mcp_server"
          ],
          cwd: "C:\\Users\\sharl\\.gemini\\antigravity\\scratch\\homeflow-ai\\backend"
        }
      }
    },
    null,
    2
  );

  const copyConfig = () => {
    navigator.clipboard.writeText(mcpConfigSnippet);
    setCopiedConfig(true);
    setTimeout(() => setCopiedConfig(false), 2000);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '680px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={20} color="#2563eb" />
            <h3>Official MCP Server Architecture</h3>
          </div>
          <button onClick={onClose} style={{ fontSize: '1.2rem', color: '#64748b' }}>✕</button>
        </div>

        <div className="modal-body" style={{ maxHeight: '70vh', overflowY: 'auto' }}>
          <p style={{ fontSize: '0.86rem', color: '#475569', marginBottom: '16px' }}>
            HomeFlow AI includes a full standalone Model Context Protocol (MCP) server
            implemented with the official Python MCP SDK (<code>mcp 2.x MCPServer</code>).
            All 10 tools below operate directly against the SQLite database.
          </p>

          <h4 style={{ fontSize: '0.9rem', marginBottom: '8px', color: '#0f172a' }}>
            10 Registered MCP Tools ({toolsData?.tools_count ?? 10}):
          </h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px', marginBottom: '18px' }}>
            {(toolsData?.tools || [
              { name: 'create_task', description: 'Create a new household task in SQLite database.' },
              { name: 'list_tasks', description: 'List household tasks filtered by completion status and category.' },
              { name: 'update_task', description: 'Update details of an existing household task.' },
              { name: 'complete_task', description: 'Mark a household task as completed.' },
              { name: 'delete_task', description: 'Permanently delete a household task by ID.' },
              { name: 'create_reminder', description: 'Create a scheduled household reminder.' },
              { name: 'list_reminders', description: 'List upcoming household reminders.' },
              { name: 'complete_reminder', description: 'Mark a household reminder as completed.' },
              { name: 'get_daily_summary', description: 'Generate factual summary of today\'s household activities.' },
              { name: 'list_simulated_entry_events', description: 'Retrieve recent simulated entry events (door/motion).' },
            ]).map((t, idx) => (
              <div
                key={idx}
                style={{
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <strong style={{ color: '#0d9488', fontFamily: 'var(--font-mono)', fontSize: '0.84rem' }}>
                    {t.name}()
                  </strong>
                  <div style={{ fontSize: '0.78rem', color: '#64748b' }}>{t.description}</div>
                </div>
                <span
                  style={{
                    fontSize: '0.7rem',
                    background: '#e0f2fe',
                    color: '#0369a1',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontWeight: 600,
                  }}
                >
                  Active
                </span>
              </div>
            ))}
          </div>

          <h4 style={{ fontSize: '0.9rem', marginBottom: '6px', color: '#0f172a' }}>
            Client Configuration (Claude Desktop / Antigravity / Cursor):
          </h4>
          <div
            style={{
              background: '#0f172a',
              borderRadius: '8px',
              padding: '12px',
              color: '#f8fafc',
              fontFamily: 'var(--font-mono)',
              fontSize: '0.78rem',
              position: 'relative',
            }}
          >
            <pre style={{ overflowX: 'auto' }}>{mcpConfigSnippet}</pre>
            <button
              onClick={copyConfig}
              style={{
                position: 'absolute',
                top: '10px',
                right: '10px',
                background: '#334155',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '0.72rem',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              {copiedConfig ? <Check size={12} color="#4ade80" /> : <Copy size={12} />}
              <span>{copiedConfig ? 'Copied' : 'Copy'}</span>
            </button>
          </div>
        </div>

        <div className="modal-footer">
          <button className="btn-primary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
