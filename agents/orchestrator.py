"""
Agent Orchestrator - Coordinates multi-agent workflow execution
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import time

from .email_parser import EmailParser
from .cost_optimizer import CostOptimizer
from .observability import ObservabilityLogger


class AgentOrchestrator:
    """Orchestrates multi-agent workflows for procurement email processing"""
    
    def __init__(self):
        self.email_parser = EmailParser()
        self.cost_optimizer = CostOptimizer()
        self.observability = ObservabilityLogger()
        
        # Agent registry
        self.agents = {
            "inbox_agent": {
                "name": "Inbox Agent",
                "status": "idle",
                "active_tasks": 0,
                "description": "Parses emails and extracts entities"
            },
            "po_tracker": {
                "name": "PO Tracker Agent",
                "status": "idle",
                "active_tasks": 0,
                "description": "Tracks purchase orders and delivery dates"
            },
            "change_manager": {
                "name": "Change Manager Agent",
                "status": "idle",
                "active_tasks": 0,
                "description": "Handles price and quantity changes"
            },
            "routing_agent": {
                "name": "Routing Agent",
                "status": "idle",
                "active_tasks": 0,
                "description": "Routes emails to appropriate agents"
            }
        }
    
    async def process_email(
        self,
        sender: str,
        subject: str,
        body: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Process email through multi-agent workflow"""
        execution_id = f"exec_{int(time.time())}_{hash(sender + subject) % 10000}"
        start_time = time.time()
        
        try:
            # Step 1: Inbox Agent - Parse email
            self.agents["inbox_agent"]["status"] = "active"
            self.agents["inbox_agent"]["active_tasks"] += 1
            
            entities = self.email_parser.extract_entities(body, subject)
            intent_result = self.email_parser.classify_intent(subject, body)
            
            parse_duration = (time.time() - start_time) * 1000
            
            self.observability.log_event(
                agent_name="inbox_agent",
                action="parse_email",
                context={"sender": sender, "subject": subject},
                outcome="success",
                duration_ms=parse_duration,
                execution_id=execution_id
            )
            
            # Step 2: Routing Agent - Determine workflow
            self.agents["routing_agent"]["status"] = "active"
            self.agents["routing_agent"]["active_tasks"] += 1
            
            routed_agent = self._route_email(intent_result["intent"], entities)
            
            routing_duration = 10.0  # Simulated
            self.observability.log_decision(
                agent_name="routing_agent",
                decision=f"route_to_{routed_agent}",
                reasoning=f"Intent: {intent_result['intent']}, PO: {entities.get('po_number', 'N/A')}",
                inputs={"intent": intent_result, "entities": entities},
                execution_id=execution_id
            )
            
            # Step 3: Execute workflow based on routing
            workflow_result = await self._execute_workflow(
                routed_agent,
                intent_result,
                entities,
                sender,
                execution_id
            )
            
            total_duration = (time.time() - start_time) * 1000
            total_cost = workflow_result.get("cost", 0.0)
            
            # Update agent statuses
            self.agents["inbox_agent"]["status"] = "idle"
            self.agents["inbox_agent"]["active_tasks"] = max(0, self.agents["inbox_agent"]["active_tasks"] - 1)
            self.agents["routing_agent"]["status"] = "idle"
            self.agents["routing_agent"]["active_tasks"] = max(0, self.agents["routing_agent"]["active_tasks"] - 1)
            
            return {
                "execution_id": execution_id,
                "intent": intent_result["intent"],
                "routed_agent": routed_agent,
                "entities": entities,
                "workflow_result": workflow_result,
                "cost": total_cost,
                "duration_ms": total_duration
            }
            
        except Exception as e:
            self.observability.log_event(
                agent_name="orchestrator",
                action="process_email",
                context={"error": str(e)},
                outcome="failure",
                execution_id=execution_id
            )
            raise
    
    def _route_email(self, intent: str, entities: Dict[str, Any]) -> str:
        """Route email to appropriate agent based on intent"""
        routing_rules = {
            "delivery_delay": "po_tracker",
            "price_change": "change_manager",
            "quantity_change": "change_manager",
            "acknowledgement_request": "po_tracker",
            "quality_issue": "change_manager",
            "general_inquiry": "inbox_agent"
        }
        
        return routing_rules.get(intent, "inbox_agent")
    
    async def _execute_workflow(
        self,
        agent_name: str,
        intent: Dict[str, Any],
        entities: Dict[str, Any],
        sender: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """Execute workflow for routed agent"""
        
        if agent_name == "po_tracker":
            return await self._po_tracker_workflow(intent, entities, sender, execution_id)
        elif agent_name == "change_manager":
            return await self._change_manager_workflow(intent, entities, sender, execution_id)
        else:
            return {"action": "logged", "cost": 0.0}
    
    async def _po_tracker_workflow(
        self,
        intent: Dict[str, Any],
        entities: Dict[str, Any],
        sender: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """PO Tracker Agent workflow"""
        self.agents["po_tracker"]["status"] = "active"
        self.agents["po_tracker"]["active_tasks"] += 1
        
        po_number = entities.get("po_number")
        
        # Simulate LLM call for decision making
        prompt = f"PO {po_number} has delivery update. Intent: {intent['intent']}. Dates: {entities.get('dates', [])}"
        response, cost = await self.cost_optimizer.call_llm(
            task_type="decision_making",
            prompt=prompt,
            context={"intent": intent, "entities": entities}
        )
        
        # Determine action
        action = "update_erp"
        if intent["intent"] == "delivery_delay":
            action = "escalate_if_critical"
        elif intent["intent"] == "acknowledgement_request":
            action = "send_acknowledgement"
        
        self.observability.log_event(
            agent_name="po_tracker",
            action=action,
            context={"po_number": po_number, "sender": sender},
            outcome="success",
            cost=cost,
            execution_id=execution_id
        )
        
        self.agents["po_tracker"]["status"] = "idle"
        self.agents["po_tracker"]["active_tasks"] = max(0, self.agents["po_tracker"]["active_tasks"] - 1)
        
        return {"action": action, "cost": cost, "po_number": po_number}
    
    async def _change_manager_workflow(
        self,
        intent: Dict[str, Any],
        entities: Dict[str, Any],
        sender: str,
        execution_id: str
    ) -> Dict[str, Any]:
        """Change Manager Agent workflow"""
        self.agents["change_manager"]["status"] = "active"
        self.agents["change_manager"]["active_tasks"] += 1
        
        # Simulate impact analysis
        prompt = f"Analyze impact of {intent['intent']} for supplier {sender}. Entities: {entities}"
        response, cost = await self.cost_optimizer.call_llm(
            task_type="multi_step_reasoning",
            prompt=prompt,
            context={"intent": intent, "entities": entities}
        )
        
        action = "requires_approval" if intent["intent"] in ["price_change", "quantity_change"] else "log_change"
        
        self.observability.log_event(
            agent_name="change_manager",
            action=action,
            context={"intent": intent["intent"], "sender": sender},
            outcome="success",
            cost=cost,
            execution_id=execution_id
        )
        
        self.agents["change_manager"]["status"] = "idle"
        self.agents["change_manager"]["active_tasks"] = max(0, self.agents["change_manager"]["active_tasks"] - 1)
        
        return {"action": action, "cost": cost}
    
    async def get_agent_statuses(self) -> List[Dict[str, Any]]:
        """Get status of all agents"""
        statuses = []
        for agent_id, agent_info in self.agents.items():
            metrics = self.observability.get_agent_metrics(agent_id)
            statuses.append({
                "id": agent_id,
                "name": agent_info["name"],
                "status": agent_info["status"],
                "active_tasks": agent_info["active_tasks"],
                "total_cost": metrics.get("total_cost", 0.0),
                "success_rate": metrics.get("success_rate", 0.0)
            })
        return statuses
    
    async def override_decision(self, agent_id: str, decision: str, reason: str):
        """Override agent decision"""
        if agent_id in self.agents:
            self.observability.log_override(agent_id, decision, reason)
            return {"status": "overridden", "agent": agent_id}
        raise ValueError(f"Agent {agent_id} not found")

