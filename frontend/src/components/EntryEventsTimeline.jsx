import React, { useState } from 'react';
import { Shield, ShieldAlert, DoorOpen, Activity, Bell, Lock, PlusCircle } from 'lucide-react';

export default function EntryEventsTimeline({ events = [], onTriggerEvent }) {
  const [selectedType, setSelectedType] = useState('door_opened');
  const [location, setLocation] = useState('Front Door');

  const handleSimulate = () => {
    let details = '';
    if (selectedType === 'door_opened') details = 'Front entrance door sensor opened';
    else if (selectedType === 'door_closed') details = 'Door securely closed';
    else if (selectedType === 'motion_detected') details = 'Motion sensor triggered';
    else if (selectedType === 'doorbell_ring') details = 'Door chime button pressed';

    onTriggerEvent({
      event_type: selectedType,
      location,
      details,
    });
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'door_opened':
        return <DoorOpen size={16} color="#d97706" />;
      case 'door_closed':
        return <Lock size={16} color="#059669" />;
      case 'motion_detected':
        return <Activity size={16} color="#2563eb" />;
      case 'doorbell_ring':
        return <Bell size={16} color="#7c3aed" />;
      default:
        return <Shield size={16} color="#64748b" />;
    }
  };

  const formatTimestamp = (ts) => {
    try {
      const d = new Date(ts);
      return d.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true,
      });
    } catch {
      return ts;
    }
  };

  return (
    <div className="content-card">
      <div className="card-header">
        <div className="card-title-group">
          <ShieldAlert size={20} color="#d97706" />
          <h2 className="card-title">Simulated Entry Events</h2>
          <span className="badge-counter">{events.length}</span>
        </div>
      </div>

      <div className="simulated-disclaimer">
        <span>⚠️</span>
        <span>
          <strong>SIMULATED DATA ONLY:</strong> Illustrative sensor logs. Not connected to physical locks, alarms, or security cameras.
        </span>
      </div>

      {/* Simulator Control Box */}
      <div
        style={{
          background: '#f8fafc',
          border: '1px solid #e2e8f0',
          borderRadius: '10px',
          padding: '12px 14px',
          marginBottom: '16px',
        }}
      >
        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#334155', marginBottom: '8px' }}>
          Simulate a Live Entry Event:
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          <select
            className="form-select"
            style={{ flex: 1, minWidth: '150px', fontSize: '0.82rem', padding: '6px 10px' }}
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
          >
            <option value="door_opened">Door Opened</option>
            <option value="door_closed">Door Closed</option>
            <option value="motion_detected">Motion Detected</option>
            <option value="doorbell_ring">Doorbell Pressed</option>
          </select>

          <select
            className="form-select"
            style={{ flex: 1, minWidth: '130px', fontSize: '0.82rem', padding: '6px 10px' }}
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          >
            <option value="Front Door">Front Door</option>
            <option value="Front Porch">Front Porch</option>
            <option value="Back Patio">Back Patio</option>
            <option value="Garage Entry">Garage Entry</option>
          </select>

          <button
            className="btn-secondary"
            onClick={handleSimulate}
            style={{ fontSize: '0.82rem', padding: '6px 12px' }}
          >
            <PlusCircle size={14} color="#d97706" />
            <span>Emit Event</span>
          </button>
        </div>
      </div>

      {/* Timeline */}
      {events.length === 0 ? (
        <div className="empty-state">
          <p>No entry events logged yet.</p>
        </div>
      ) : (
        <div className="timeline-list">
          {events.map((ev) => (
            <div key={ev.id} className="timeline-item">
              <div className="timeline-dot" />
              <div className="timeline-box">
                <div className="timeline-top">
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 700, fontSize: '0.88rem' }}>
                    {getEventIcon(ev.event_type)}
                    {ev.event_type.replace('_', ' ').toUpperCase()} • {ev.location}
                  </span>
                  <span className="timeline-time">{formatTimestamp(ev.timestamp)}</span>
                </div>
                <div className="timeline-details">{ev.details}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
