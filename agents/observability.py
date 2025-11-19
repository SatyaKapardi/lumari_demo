"""
Observability Logger - Tracks agent execution, decisions, and performance
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict
import json


class ObservabilityLogger:
    """Logs agent actions, decisions, and performance metrics"""
    
    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self.agent_metrics: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "total_cost": 0.0,
            "total_time": 0.0,
            "overrides": 0
        })
    
    def log_event(
        self,
        agent_name: str,
        action: str,
        context: Dict[str, Any],
        outcome: str = "success",
        cost: float = 0.0,
        duration_ms: float = 0.0,
        execution_id: Optional[str] = None
    ):
        """Log an agent action event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "action": action,
            "context": json.dumps(context) if isinstance(context, dict) else str(context),
            "outcome": outcome,
            "cost": cost,
            "duration_ms": duration_ms,
            "execution_id": execution_id or f"exec_{len(self.events)}"
        }
        
        self.events.append(event)
        
        # Update agent metrics
        metrics = self.agent_metrics[agent_name]
        metrics["total_actions"] += 1
        if outcome == "success":
            metrics["successful_actions"] += 1
        else:
            metrics["failed_actions"] += 1
        metrics["total_cost"] += cost
        metrics["total_time"] += duration_ms
        
        # Keep only last 1000 events (in production, use persistent storage)
        if len(self.events) > 1000:
            self.events = self.events[-1000:]
    
    def log_decision(
        self,
        agent_name: str,
        decision: str,
        reasoning: str,
        inputs: Dict[str, Any],
        execution_id: Optional[str] = None
    ):
        """Log agent decision with provenance"""
        self.log_event(
            agent_name=agent_name,
            action=f"decision: {decision}",
            context={
                "reasoning": reasoning,
                "inputs": inputs,
                "decision": decision
            },
            execution_id=execution_id
        )
    
    def log_override(self, agent_name: str, original_decision: str, override_reason: str):
        """Log human override of agent decision"""
        self.agent_metrics[agent_name]["overrides"] += 1
        self.log_event(
            agent_name=agent_name,
            action="override",
            context={
                "original_decision": original_decision,
                "override_reason": override_reason
            },
            outcome="overridden"
        )
    
    def get_timeline(self, limit: int = 50, agent_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get execution timeline"""
        events = self.events
        
        if agent_filter:
            events = [e for e in events if e["agent"] == agent_filter]
        
        # Sort by timestamp (newest first)
        sorted_events = sorted(events, key=lambda x: x["timestamp"], reverse=True)
        
        return sorted_events[:limit]
    
    def get_agent_metrics(self, agent_name: str) -> Dict[str, Any]:
        """Get metrics for specific agent"""
        if agent_name not in self.agent_metrics:
            return {}
        
        metrics = self.agent_metrics[agent_name]
        total = metrics["total_actions"]
        
        return {
            "agent": agent_name,
            "total_actions": total,
            "success_rate": (metrics["successful_actions"] / total * 100) if total > 0 else 0,
            "failure_rate": (metrics["failed_actions"] / total * 100) if total > 0 else 0,
            "avg_response_time_ms": (metrics["total_time"] / total) if total > 0 else 0,
            "total_cost": round(metrics["total_cost"], 4),
            "overrides": metrics["overrides"],
            "override_rate": (metrics["overrides"] / total * 100) if total > 0 else 0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get overall system metrics"""
        total_events = len(self.events)
        successful_events = sum(1 for e in self.events if e["outcome"] == "success")
        
        total_cost = sum(m["total_cost"] for m in self.agent_metrics.values())
        
        return {
            "total_processed": total_events,
            "success_rate": (successful_events / total_events * 100) if total_events > 0 else 0,
            "total_cost": round(total_cost, 4),
            "agent_count": len(self.agent_metrics),
            "events_last_hour": sum(
                1 for e in self.events 
                if (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 3600
            )
        }

