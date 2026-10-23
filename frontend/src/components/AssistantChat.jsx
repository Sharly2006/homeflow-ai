import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, ChevronDown, ChevronRight, Terminal, CheckCircle2, AlertCircle } from 'lucide-react';

const SAMPLE_PROMPTS = [
  'Add a task to clean the kitchen tomorrow.',
  'Remind me to call my grandmother at 6 PM.',
  'Show me all pending household tasks.',
  'Mark the kitchen cleaning task as completed.',
  "Give me a summary of today's household activities.",
  'Show me the latest simulated entry events.',
];

export default function AssistantChat({ onSendMessage, messages = [], isLoading }) {
  const [input, setInput] = useState('');
  const [expandedTraces, setExpandedTraces] = useState({});
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;
    const text = input.trim();
    setInput('');
    onSendMessage(text);
  };

  const handlePromptClick = (prompt) => {
    setInput(prompt);
  };

  const toggleTrace = (index) => {
    setExpandedTraces((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  return (
    <div className="content-card assistant-card">
      <div className="card-header">
        <div className="card-title-group">
          <Sparkles className="text-teal-600" size={20} color="#0d9488" />
          <h2 className="card-title">HomeFlow Natural-Language Assistant</h2>
        </div>
        <span className="badge-counter">MCP Tool Powered</span>
      </div>

      {/* Clickable Quick Prompts */}
      <div className="sample-prompts-label">
        <Sparkles size={13} color="#0d9488" />
        <span>Try a sample household request:</span>
      </div>
      <div className="sample-prompts-container">
        {SAMPLE_PROMPTS.map((prompt, idx) => (
          <button
            key={idx}
            className="sample-prompt-chip"
            onClick={() => handlePromptClick(prompt)}
            disabled={isLoading}
          >
            "{prompt}"
          </button>
        ))}
      </div>

      {/* Input form */}
      <form onSubmit={handleSubmit} className="assistant-input-box">
        <input
          type="text"
          className="assistant-input"
          placeholder="e.g. Add a task to clean the patio, or remind me to take medicine at 9 PM..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={isLoading}
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={!input.trim() || isLoading}
        >
          {isLoading ? (
            <span>Processing...</span>
          ) : (
            <>
              <Send size={16} />
              <span>Send</span>
            </>
          )}
        </button>
      </form>

      {/* Chat History & Execution Traces */}
      <div className="chat-history">
        {messages.length === 0 ? (
          <div className="empty-state">
            <p>Ready to assist. Click a sample request above or type your household instruction.</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`chat-bubble ${msg.sender}`}>
              <div className="assistant-response-text">{msg.text}</div>

              {/* Expandable Activity Trace for Assistant Responses */}
              {msg.trace && (
                <div>
                  <button
                    className="tool-trace-toggle"
                    onClick={() => toggleTrace(index)}
                    type="button"
                  >
                    <Terminal size={12} />
                    <span>Tool Trace: {msg.trace.tool_called || 'Orchestrator'}</span>
                    {expandedTraces[index] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  </button>

                  {expandedTraces[index] && (
                    <div className="tool-trace-box">
                      <div className="trace-row">
                        <span className="trace-key">Tool Executed: </span>
                        <span className="trace-val-tool">{msg.trace.tool_called || 'None'}</span>
                      </div>
                      <div className="trace-row">
                        <span className="trace-key">Status: </span>
                        <span>{msg.trace.execution_status}</span>
                      </div>
                      {msg.trace.arguments && (
                        <div className="trace-row">
                          <span className="trace-key">Validated Arguments: </span>
                          <pre style={{ margin: '4px 0', color: '#cbd5e1' }}>
                            {JSON.stringify(msg.trace.arguments, null, 2)}
                          </pre>
                        </div>
                      )}
                      {msg.trace.tool_result && (
                        <div className="trace-row">
                          <span className="trace-key">Execution Result: </span>
                          <pre style={{ margin: '4px 0', color: '#93c5fd' }}>
                            {JSON.stringify(msg.trace.tool_result, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="chat-bubble assistant" style={{ fontStyle: 'italic', color: '#64748b' }}>
            HomeFlow Assistant is evaluating request and selecting MCP tool...
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}
