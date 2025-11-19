"""
Lumari AI Demo - Multi-Agent Procurement Email Automation System
Main FastAPI application with Command Center UI
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

from agents.orchestrator import AgentOrchestrator

app = FastAPI(title="Lumari AI Demo - Command Center", version="1.0.0")

# Initialize core components
orchestrator = AgentOrchestrator()
observability = orchestrator.observability

# Serve static files for UI
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)


class EmailRequest(BaseModel):
    sender: EmailStr
    subject: str
    body: str
    timestamp: Optional[datetime] = None


class AgentOverride(BaseModel):
    decision: str
    reason: str


@app.get("/", response_class=HTMLResponse)
async def command_center():
    """Main Command Center Dashboard"""
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Lumari Command Center</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e27;
            color: #e4e7eb;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        h1 { font-size: 32px; margin-bottom: 10px; }
        .subtitle { opacity: 0.9; font-size: 16px; }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1a1f3a;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2d3748;
        }
        .card h2 {
            font-size: 18px;
            margin-bottom: 15px;
            color: #a0aec0;
        }
        .metric {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .label { font-size: 14px; opacity: 0.7; }
        .agent-list { list-style: none; }
        .agent-item {
            padding: 12px;
            margin-bottom: 10px;
            background: #252b45;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .agent-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        .status-active { background: #48bb78; }
        .status-idle { background: #ed8936; }
        .agent-name { font-weight: 600; }
        .agent-metric { font-size: 12px; opacity: 0.7; margin-top: 5px; }
        .section {
            background: #1a1f3a;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid #2d3748;
        }
        .section h2 { margin-bottom: 20px; color: #a0aec0; }
        .email-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        input, textarea {
            background: #252b45;
            border: 1px solid #2d3748;
            border-radius: 8px;
            padding: 12px;
            color: #e4e7eb;
            font-size: 14px;
            width: 100%;
        }
        textarea { min-height: 120px; resize: vertical; }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { opacity: 0.9; }
        .timeline-item {
            padding: 15px;
            margin-bottom: 10px;
            background: #252b45;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .timeline-time { font-size: 12px; opacity: 0.6; margin-bottom: 5px; }
        .timeline-action { font-weight: 600; margin-bottom: 5px; }
        .timeline-context { font-size: 13px; opacity: 0.8; }
        .loading { opacity: 0.6; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Lumari Command Center</h1>
        <div class="subtitle">Multi-Agent Procurement Email Automation System</div>
    </div>

    <div class="dashboard">
        <div class="card">
            <h2>System Status</h2>
            <div class="metric" id="total-processed">0</div>
            <div class="label">Emails Processed</div>
        </div>
        <div class="card">
            <h2>Cost Efficiency</h2>
            <div class="metric" id="cache-hit-rate">0%</div>
            <div class="label">Cache Hit Rate</div>
        </div>
        <div class="card">
            <h2>Agent Performance</h2>
            <div class="metric" id="success-rate">0%</div>
            <div class="label">Success Rate</div>
        </div>
        <div class="card">
            <h2>Active Agents</h2>
            <ul class="agent-list" id="agent-list">
                <li class="agent-item">
                    <span class="agent-status status-idle"></span>
                    <span class="agent-name">Loading...</span>
                </li>
            </ul>
        </div>
    </div>

    <div class="section">
        <h2>📧 Process Supplier Email</h2>
        <form class="email-form" id="email-form">
            <input type="email" id="sender" placeholder="supplier@example.com" required>
            <input type="text" id="subject" placeholder="Email Subject" required>
            <textarea id="body" placeholder="Email body content..." required></textarea>
            <button type="submit">Process Email →</button>
        </form>
    </div>

    <div class="section">
        <h2>📊 Execution Timeline</h2>
        <div id="timeline"></div>
    </div>

    <script>
        async function loadDashboard() {
            try {
                const [metrics, agents, timeline] = await Promise.all([
                    fetch('/api/observability/metrics').then(r => r.json()),
                    fetch('/api/agents/status').then(r => r.json()),
                    fetch('/api/observability/timeline').then(r => r.json())
                ]);

                document.getElementById('total-processed').textContent = metrics.total_processed || 0;
                document.getElementById('cache-hit-rate').textContent = (metrics.cache_hit_rate || 0).toFixed(1) + '%';
                document.getElementById('success-rate').textContent = (metrics.success_rate || 0).toFixed(1) + '%';

                const agentList = document.getElementById('agent-list');
                agentList.innerHTML = agents.map(agent => `
                    <li class="agent-item">
                        <span class="agent-status status-${agent.status}"></span>
                        <span class="agent-name">${agent.name}</span>
                        <div class="agent-metric">${agent.active_tasks} active tasks | $${agent.total_cost.toFixed(4)}</div>
                    </li>
                `).join('');

                const timelineDiv = document.getElementById('timeline');
                timelineDiv.innerHTML = timeline.slice(0, 10).map(event => `
                    <div class="timeline-item">
                        <div class="timeline-time">${new Date(event.timestamp).toLocaleString()}</div>
                        <div class="timeline-action">${event.agent}: ${event.action}</div>
                        <div class="timeline-context">${event.context}</div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            }
        }

        document.getElementById('email-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const form = e.target;
            const button = form.querySelector('button');
            button.disabled = true;
            button.classList.add('loading');

            try {
                const response = await fetch('/api/process-email', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        sender: document.getElementById('sender').value,
                        subject: document.getElementById('subject').value,
                        body: document.getElementById('body').value
                    })
                });

                const result = await response.json();
                alert(`Email processed! Intent: ${result.intent}, PO Number: ${result.extracted_entities.po_number || 'N/A'}`);
                
                form.reset();
                setTimeout(loadDashboard, 1000);
            } catch (error) {
                alert('Error processing email: ' + error.message);
            } finally {
                button.disabled = false;
                button.classList.remove('loading');
            }
        });

        loadDashboard();
        setInterval(loadDashboard, 5000);
    </script>
</body>
</html>
    """


@app.post("/api/process-email")
async def process_email(email: EmailRequest, background_tasks: BackgroundTasks):
    """Process a supplier email through the multi-agent system"""
    try:
        # Process email through orchestration layer
        result = await orchestrator.process_email(
            sender=email.sender,
            subject=email.subject,
            body=email.body,
            timestamp=email.timestamp or datetime.now()
        )
        
        return {
            "status": "processed",
            "intent": result.get("intent"),
            "routed_to": result.get("routed_agent"),
            "extracted_entities": result.get("entities", {}),
            "execution_id": result.get("execution_id"),
            "cost": result.get("cost", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    return await orchestrator.get_agent_statuses()


@app.get("/api/observability/timeline")
async def get_timeline(limit: int = 50):
    """Get agent execution timeline"""
    return await observability.get_timeline(limit=limit)


@app.get("/api/observability/metrics")
async def get_metrics():
    """Get system performance metrics"""
    return await observability.get_metrics()


@app.post("/api/agents/{agent_id}/override")
async def override_agent(agent_id: str, override: AgentOverride):
    """Override an agent decision"""
    return await orchestrator.override_decision(agent_id, override.decision, override.reason)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

