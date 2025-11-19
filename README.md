# Lumari AI Demo: Multi-Agent Procurement Email Automation

A weekend demonstration project showcasing multi-agent orchestration, email parsing, observability, and cost optimization for supply chain operations.

## 🎯 What This Demonstrates

This project directly addresses Lumari's core value proposition by implementing:

1. **Multi-Agent Orchestration** - Coordinated agents for email processing, PO tracking, and routing
2. **Supply Chain Entity Extraction** - Parses PO numbers, dates, quantities, part numbers from unstructured emails
3. **Agent Observability** - Real-time dashboard showing agent execution, decisions, and performance metrics
4. **LLM Cost Optimization** - Intelligent model routing, caching, and task complexity analysis
5. **Integration Architecture** - Extensible framework for connecting to ERPs, email, and other tools

## 🏗️ Architecture

```
┌─────────────────┐
│  Email Inbox    │
└────────┬────────┘
         │
    ┌────▼──────────────────────────┐
    │   Inbox Agent                 │
    │   - Parse emails              │
    │   - Extract entities          │
    │   - Classify intent           │
    └────┬──────────────────────────┘
         │
    ┌────▼──────────────────────────┐
    │   Routing Agent               │
    │   - Decision tree             │
    │   - Context awareness         │
    └────┬──────────────────────────┘
         │
    ┌────┬────────────┬─────────────┐
    │    │            │             │
┌───▼──┐ ┌──▼───┐ ┌──▼──────┐ ┌───▼────┐
│ PO   │ │Change│ │Approval │ │Notify  │
│Tracker│ │Mgmt │ │ Agent   │ │ Agent  │
└──────┘ └──────┘ └─────────┘ └────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

**Note:** Demo works without OpenAI API key or spaCy model (uses regex parsing). For full functionality, optionally add:
- OpenAI API key to `.env` file
- spaCy model: `python3 -m spacy download en_core_web_sm` (may have version conflicts, demo works fine without it)

### 2. Test Using Terminal Only

#### Run the Test Script

```bash
python3 test_demo.py
```

This will process 4 sample supplier emails and show:
- Email parsing and intent classification
- Multi-agent routing decisions
- Entity extraction (PO numbers, dates, quantities)
- System metrics and agent statuses

#### Test Individual Emails via API

Start the server (optional, for API testing):
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Then test with curl:

```bash
# Test delivery delay email
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "supplier@example.com",
    "subject": "PO #12345 Delivery Update",
    "body": "Dear buyer, PO #12345 will be delayed by 3 days. New delivery date: Dec 15, 2024. Quantity: 500 units."
  }'

# Test price change email
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "vendor@supplychain.com",
    "subject": "Price Change Notification",
    "body": "The price for Part #ABC-123 has increased from $10.00 to $12.00 per unit, effective January 1, 2025. This affects PO #67890."
  }'

# Check agent statuses
curl http://localhost:8000/api/agents/status

# View execution timeline
curl http://localhost:8000/api/observability/timeline

# Get system metrics
curl http://localhost:8000/api/observability/metrics
```

#### Terminal Testing Summary

The demo can be fully tested via terminal using:

1. **Quick Test**: `python3 test_demo.py` - Processes sample emails, shows all metrics
2. **API Testing**: Start server, use curl commands to test individual endpoints
3. **No Web UI Required**: All functionality accessible via terminal/API

## Features

### Multi-Agent System
- **Inbox Agent**: Parses emails, extracts supply chain entities (PO numbers, dates, quantities)
- **PO Tracker Agent**: Monitors delivery dates, sends nudges, updates status
- **Change Management Agent**: Handles price changes, quantity modifications
- **Routing Agent**: Intelligent message passing between agents

### Observability Dashboard
- Real-time agent execution timeline
- Decision provenance tracking
- Performance metrics (success rate, response time, cost)
- Visual workflow visualization

### Cost Optimization
- **Model Routing**: Small models for simple tasks (GPT-3.5), large for complex (GPT-4)
- **Semantic Caching**: Reuse responses for similar queries
- **Task Complexity Analysis**: Automatically routes to appropriate model tier
- **Batch Processing**: Aggregate similar requests

### Integration Architecture
- Extensible connector framework
- Email integration (IMAP/SMTP ready)
- Spreadsheet export/import
- ERP integration hooks (SAP, Oracle, NetSuite ready)

## Command Center UI

The web interface (`/`) provides:
- Agent status monitoring
- Email processing queue
- Execution timeline viewer
- Cost analytics dashboard
- Manual override controls

## API Endpoints

- `POST /api/process-email` - Process a supplier email
- `GET /api/agents/status` - Get all agent statuses
- `GET /api/observability/timeline` - Get execution timeline
- `GET /api/observability/metrics` - Get performance metrics
- `POST /api/agents/{agent_id}/override` - Override agent decision

## 📈 Metrics Tracked

- Agent success rate
- Average response time per agent
- LLM cost per agent action
- Cache hit rate
- Human override rate
- Intent classification accuracy

## Technical Highlights

- **Agent Communication Protocol**: Structured message passing between agents
- **Context Management**: Shared state via Redis for agent coordination
- **Error Handling**: Graceful degradation with retry logic
- **Audit Logging**: Full traceability of agent decisions
- **Fine-Tuning Ready**: Architecture supports domain-specific model training

## Why This Matters for Lumari

This demo showcases:
- Proven multi-agent orchestration 
- Integration architecture patterns 
- Observability infrastructure 
- Cost optimization strategies 

All built with production-ready patterns that scale to enterprise deployments.

---

**Built for Lumari AI** | Demonstrating expertise in agentic workflow orchestration, integration architecture, observability, and cost optimization.

