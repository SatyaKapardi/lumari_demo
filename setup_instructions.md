# Setup Instructions for Lumari AI Demo

## Quick Start (5 minutes)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

**Note:** The demo works without OpenAI API key for testing (uses mock responses). For full functionality, add your key to `.env`.

### 2. Run the Web UI

```bash
uvicorn main:app --reload
```

Visit `http://localhost:8000` to see the Command Center dashboard.

### 3. Test with Sample Emails

Run the test script:

```bash
python test_demo.py
```

Or use the web UI to manually enter supplier emails.

## What's Included

### Core Features

1. **Multi-Agent Orchestration** (`agents/orchestrator.py`)
   - Coordinates Inbox Agent, PO Tracker, Change Manager, and Routing Agent
   - Implements message passing between agents
   - Handles workflow execution

2. **Email Parsing** (`agents/email_parser.py`)
   - Extracts PO numbers, dates, quantities, part numbers
   - Intent classification (delivery delay, price change, etc.)
   - Uses regex + spaCy for entity extraction

3. **Cost Optimization** (`agents/cost_optimizer.py`)
   - Intelligent model routing (GPT-3.5 vs GPT-4)
   - Semantic caching to reduce API calls
   - Task complexity analysis
   - Cascading inference (try small model first)

4. **Observability** (`agents/observability.py`)
   - Logs every agent action with context
   - Tracks execution timeline
   - Performance metrics (success rate, cost, response time)
   - Decision provenance tracking

5. **Command Center UI** (`main.py`)
   - Real-time agent status monitoring
   - Email processing interface
   - Execution timeline viewer
   - Cost analytics dashboard

## Architecture Highlights

### Multi-Agent Communication

Agents communicate through the orchestrator using structured messages:
- Agent name, action, context, priority
- Shared state via Redis (ready for production)
- Acknowledgment system
- Failure handling and retry logic

### Integration Patterns

The code demonstrates:
- **Extensible connector framework** (ready for ERP integrations)
- **Email processing pipeline** (IMAP/SMTP ready)
- **Spreadsheet export hooks** (CSV/Excel ready)
- **Webhook support patterns** (for real-time updates)

### Cost Optimization Strategies

1. **Model Routing**: Simple tasks → GPT-3.5, Complex → GPT-4
2. **Semantic Caching**: Reuse responses for similar queries
3. **Batch Processing**: Aggregate similar requests (ready to implement)
4. **Fine-tuning Ready**: Architecture supports domain-specific models

## Production Readiness Notes

This is a weekend demo, but shows production patterns:

- ✅ Structured logging (ready for ELK/Datadog)
- ✅ Metrics collection (ready for Prometheus)
- ✅ Error handling with graceful degradation
- ✅ Agent coordination patterns (scalable)
- ✅ Cost tracking (ready for billing integration)

To make production-ready:
- Replace in-memory cache with Redis
- Add persistent storage (PostgreSQL)
- Implement actual ERP connectors (SAP, Oracle, NetSuite)
- Add authentication/authorization
- Set up monitoring/alerting
- Add comprehensive tests

## Why This Matters for Lumari

This demo directly addresses your tracks:

**Track 1 (Agentic Workflow Orchestration)**: ✅
- Multi-agent coordination
- Workflow decomposition
- Context management between agents

**Track 2 (Integration Architecture)**: ✅
- Extensible connector framework
- Data transformation patterns
- Error handling strategies

**Track 3 (Agent Observability)**: ✅
- Execution timeline
- Decision provenance
- Performance metrics

**Track 4 (Cost Optimization)**: ✅
- Model routing
- Caching strategies
- Task complexity analysis

## Sample Test Cases

The demo includes test emails covering:
- Delivery delays (routes to PO Tracker)
- Price changes (routes to Change Manager)
- Quantity revisions (routes to Change Manager)
- Acknowledgement requests (routes to PO Tracker)

## Next Steps

To extend this demo:
1. Add more agent types (Approval Agent, Notification Agent)
2. Implement actual email integration (Gmail API, Outlook)
3. Add spreadsheet import/export
4. Create ERP connector stubs (SAP, Oracle)
5. Add fine-tuning pipeline for domain-specific models
6. Implement batch processing for cost savings

---

Built to demonstrate expertise in exactly what Lumari needs. 🚀

