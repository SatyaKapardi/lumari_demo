# Terminal Testing Guide

This guide shows how to test the Lumari AI demo using **only the terminal** (no web browser required).

## Quick Test (Recommended)

Run the automated test script:

```bash
python3 test_demo.py
```

This processes 4 sample supplier emails and displays:
- ✅ Intent classification results
- ✅ Entity extraction (PO numbers, dates, quantities)
- ✅ Agent routing decisions
- ✅ System performance metrics
- ✅ Cost optimization statistics

## Manual API Testing

### 1. Start the Server

```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Test Email Processing

#### Test Delivery Delay Email
```bash
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "supplier@acme.com",
    "subject": "PO #12345 Delivery Update",
    "body": "Dear buyer, PO #12345 will be delayed by 3 days. New delivery date: December 15, 2024. Quantity: 500 units."
  }'
```

#### Test Price Change Email
```bash
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "vendor@supplychain.com",
    "subject": "Price Change Notification - Order #67890",
    "body": "Please be advised that the price for Part #ABC-123 has increased from $10.00 to $12.00 per unit, effective January 1, 2025. This affects PO #67890."
  }'
```

#### Test Acknowledgement Request
```bash
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "manufacturer@global.com",
    "subject": "Please acknowledge receipt of PO #99999",
    "body": "We have received your Purchase Order #99999 for 1,000 units. Please confirm receipt so we can proceed with production."
  }'
```

#### Test Quantity Revision
```bash
curl -X POST http://localhost:8000/api/process-email \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "distributor@parts.com",
    "subject": "Quantity revision for order #11111",
    "body": "Regarding PO #11111, we need to revise the quantity from 250 units to 300 units. All other terms remain the same."
  }'
```

### 3. Check System Status

#### Get Agent Statuses
```bash
curl http://localhost:8000/api/agents/status | python3 -m json.tool
```

#### View Execution Timeline
```bash
curl http://localhost:8000/api/observability/timeline | python3 -m json.tool
```

#### Get Performance Metrics
```bash
curl http://localhost:8000/api/observability/metrics | python3 -m json.tool
```

### 4. Test Agent Override

```bash
curl -X POST http://localhost:8000/api/agents/po_tracker/override \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "do_not_escalate",
    "reason": "Manual override - supplier notified separately"
  }'
```

## Expected Output Examples

### Successful Email Processing
```json
{
  "status": "processed",
  "intent": "delivery_delay",
  "routed_to": "po_tracker",
  "extracted_entities": {
    "po_number": "12345",
    "quantities": ["500"],
    "dates": ["December 15, 2024", "Dec 15, 2024"],
    "part_numbers": [],
    "prices": [],
    "confidence": 0.5
  },
  "execution_id": "exec_1234567890_1234",
  "cost": 0.0
}
```

### Agent Statuses
```json
[
  {
    "id": "inbox_agent",
    "name": "Inbox Agent",
    "status": "idle",
    "active_tasks": 0,
    "total_cost": 0.0,
    "success_rate": 100.0
  },
  {
    "id": "po_tracker",
    "name": "PO Tracker Agent",
    "status": "idle",
    "active_tasks": 0,
    "total_cost": 0.0,
    "success_rate": 100.0
  }
]
```

## Testing Checklist

- [ ] Run `python3 test_demo.py` - All 4 test emails processed successfully
- [ ] Test delivery delay email - Routes to PO Tracker agent
- [ ] Test price change email - Routes to Change Manager agent
- [ ] Test acknowledgement request - Routes to PO Tracker agent
- [ ] Test quantity revision - Routes to Change Manager agent
- [ ] Check agent statuses - All agents show correct status
- [ ] View timeline - Shows execution events
- [ ] Check metrics - Shows system performance stats

## Troubleshooting

**Server won't start?**
- Check if port 8000 is already in use: `lsof -ti:8000`
- Kill existing process: `kill -9 $(lsof -ti:8000)`
- Use different port: `python3 -m uvicorn main:app --port 8001`

**Import errors?**
- Install dependencies: `pip3 install -r requirements.txt`
- Make sure you're in the project directory

**No response from API?**
- Ensure server is running: Check terminal output
- Test server health: `curl http://localhost:8000/`

---

**All testing can be done via terminal - no web browser required!** 🚀

