"""
Quick test script for the Lumari AI demo
Run this to test the multi-agent system with sample emails
"""

import asyncio
from agents.orchestrator import AgentOrchestrator
from datetime import datetime


async def test_email_processing():
    """Test the multi-agent system with sample supplier emails"""
    
    orchestrator = AgentOrchestrator()
    observability = orchestrator.observability
    
    # Sample emails that demonstrate different intents
    test_emails = [
        {
            "sender": "supplier@acme.com",
            "subject": "PO #12345 Delivery Update",
            "body": "Dear buyer, Purchase Order #12345 will be delayed by 3 days. New delivery date: December 15, 2024. Quantity: 500 units. We apologize for the inconvenience.",
            "expected_intent": "delivery_delay"
        },
        {
            "sender": "vendor@supplychain.com",
            "subject": "Price Change Notification - Order #67890",
            "body": "Please be advised that the price for Part #ABC-123 has increased from $10.00 to $12.00 per unit, effective January 1, 2025. This affects PO #67890. Please confirm acceptance.",
            "expected_intent": "price_change"
        },
        {
            "sender": "manufacturer@global.com",
            "subject": "Please acknowledge receipt of PO #99999",
            "body": "We have received your Purchase Order #99999 for 1,000 units. Please confirm receipt so we can proceed with production. Delivery scheduled for March 20, 2025.",
            "expected_intent": "acknowledgement_request"
        },
        {
            "sender": "distributor@parts.com",
            "subject": "Quantity revision for order #11111",
            "body": "Regarding PO #11111, we need to revise the quantity from 250 units to 300 units. All other terms remain the same. Please confirm if this works.",
            "expected_intent": "quantity_change"
        }
    ]
    
    print("🚀 Testing Lumari AI Multi-Agent System\n")
    print("=" * 60)
    
    for i, email in enumerate(test_emails, 1):
        print(f"\n📧 Test Email {i}/{len(test_emails)}")
        print(f"From: {email['sender']}")
        print(f"Subject: {email['subject']}")
        print(f"Expected Intent: {email['expected_intent']}")
        print("-" * 60)
        
        try:
            result = await orchestrator.process_email(
                sender=email['sender'],
                subject=email['subject'],
                body=email['body'],
                timestamp=datetime.now()
            )
            
            print(f"✅ Processed successfully")
            print(f"   Intent: {result['intent']}")
            print(f"   Routed to: {result['routed_agent']}")
            print(f"   PO Number: {result['entities'].get('po_number', 'N/A')}")
            print(f"   Cost: ${result['cost']:.4f}")
            print(f"   Duration: {result['duration_ms']:.2f}ms")
            
            if result['intent'] == email['expected_intent']:
                print(f"   ✓ Intent classification correct!")
            else:
                print(f"   ⚠ Intent mismatch (expected {email['expected_intent']})")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("\n📊 System Metrics")
    print("-" * 60)
    
    metrics = observability.get_metrics()
    print(f"Total Emails Processed: {metrics['total_processed']}")
    print(f"Success Rate: {metrics['success_rate']:.1f}%")
    print(f"Total Cost: ${metrics['total_cost']:.4f}")
    
    # Get cost optimizer stats
    cost_stats = orchestrator.cost_optimizer.get_stats()
    print(f"\n💰 Cost Optimization Stats")
    print(f"Cache Hit Rate: {cost_stats['cache_hit_rate']:.1f}%")
    print(f"Estimated Savings: ${cost_stats['estimated_savings']:.4f}")
    
    # Get agent statuses
    print(f"\n🤖 Agent Statuses")
    statuses = await orchestrator.get_agent_statuses()
    for status in statuses:
        print(f"   {status['name']}: {status['status']} ({status['active_tasks']} tasks)")
    
    print("\n" + "=" * 60)
    print("✨ Demo complete!")


if __name__ == "__main__":
    asyncio.run(test_email_processing())

