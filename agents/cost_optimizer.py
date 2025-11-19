"""
Cost Optimizer - Intelligent LLM model routing and caching
"""

from typing import Dict, Any, Optional, Tuple
from functools import lru_cache
import hashlib
import json
from enum import Enum

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class ModelTier(Enum):
    SMALL = "gpt-3.5-turbo"  # Cheap, fast
    MEDIUM = "gpt-3.5-turbo-16k"  # Moderate cost
    LARGE = "gpt-4"  # Expensive, accurate


class CostOptimizer:
    """Optimizes LLM costs through intelligent routing and caching"""
    
    def __init__(self):
        self.cache = {}  # In-memory semantic cache (use Redis in production)
        self.stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_cost": 0.0,
            "calls_by_tier": {tier.value: 0 for tier in ModelTier}
        }
        
        # Cost per 1K tokens (approximate)
        self.costs = {
            ModelTier.SMALL: {"input": 0.0015, "output": 0.002},
            ModelTier.MEDIUM: {"input": 0.003, "output": 0.004},
            ModelTier.LARGE: {"input": 0.03, "output": 0.06}
        }
    
    def analyze_task_complexity(self, task_type: str, context: Dict[str, Any]) -> ModelTier:
        """Analyze task complexity and route to appropriate model"""
        
        # Simple tasks -> small model
        simple_tasks = ["extract_po_number", "parse_date", "extract_quantity"]
        if task_type in simple_tasks:
            return ModelTier.SMALL
        
        # Medium complexity -> medium model
        medium_tasks = ["classify_intent", "extract_entities", "format_response"]
        if task_type in medium_tasks:
            # Check if context is simple
            if len(context.get("text", "")) < 500:
                return ModelTier.SMALL
            return ModelTier.MEDIUM
        
        # Complex tasks -> large model
        complex_tasks = ["multi_step_reasoning", "decision_making", "coordination"]
        if task_type in complex_tasks or context.get("requires_reasoning", False):
            return ModelTier.LARGE
        
        # Default to medium
        return ModelTier.MEDIUM
    
    def _generate_cache_key(self, task_type: str, prompt: str, context: Dict[str, Any]) -> str:
        """Generate semantic cache key"""
        # Simple hash-based cache (in production, use embeddings for semantic similarity)
        key_data = f"{task_type}:{prompt}:{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_response(self, task_type: str, prompt: str, context: Dict[str, Any]) -> Optional[Any]:
        """Check cache for similar request"""
        cache_key = self._generate_cache_key(task_type, prompt, context)
        
        if cache_key in self.cache:
            self.stats["cache_hits"] += 1
            return self.cache[cache_key]
        
        self.stats["cache_misses"] += 1
        return None
    
    def cache_response(self, task_type: str, prompt: str, context: Dict[str, Any], response: Any):
        """Cache response for future use"""
        cache_key = self._generate_cache_key(task_type, prompt, context)
        self.cache[cache_key] = response
        
        # Limit cache size (in production, use Redis with TTL)
        if len(self.cache) > 1000:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    async def call_llm(
        self, 
        task_type: str, 
        prompt: str, 
        context: Dict[str, Any] = None,
        force_tier: Optional[ModelTier] = None
    ) -> Tuple[Any, float]:
        """Call LLM with cost optimization"""
        context = context or {}
        
        # Check cache first
        cached = self.get_cached_response(task_type, prompt, context)
        if cached:
            return cached, 0.0
        
        # Determine model tier
        tier = force_tier or self.analyze_task_complexity(task_type, context)
        
        # Cascading inference: try small first, escalate if needed
        if not force_tier and task_type not in ["extract_po_number", "parse_date"]:
            # Try small model first
            try:
                response, cost = await self._call_openai(ModelTier.SMALL, prompt)
                # Simple confidence check
                if len(response) > 10:  # Has meaningful response
                    self.stats["calls_by_tier"][ModelTier.SMALL.value] += 1
                    self.cache_response(task_type, prompt, context, response)
                    return response, cost
            except:
                pass
        
        # Use determined tier
        response, cost = await self._call_openai(tier, prompt)
        self.stats["calls_by_tier"][tier.value] += 1
        self.stats["total_cost"] += cost
        
        # Cache response
        self.cache_response(task_type, prompt, context, response)
        
        return response, cost
    
    async def _call_openai(self, tier: ModelTier, prompt: str) -> Tuple[str, float]:
        """Call OpenAI API (mock implementation for demo)"""
        # Mock implementation - in production, call actual OpenAI API
        # For demo purposes, return simulated response
        
        if not OPENAI_AVAILABLE:
            # Return mock response
            mock_responses = {
                ModelTier.SMALL: f"Mock response from {tier.value}",
                ModelTier.MEDIUM: f"Detailed mock response from {tier.value}",
                ModelTier.LARGE: f"Comprehensive mock response from {tier.value} with reasoning"
            }
            # Estimate tokens (rough: 1 token ≈ 4 chars)
            input_tokens = len(prompt) / 4
            output_tokens = len(mock_responses[tier]) / 4
            
            cost = (input_tokens * self.costs[tier]["input"] + 
                   output_tokens * self.costs[tier]["output"]) / 1000
            
            return mock_responses[tier], cost
        
        # Real OpenAI implementation would go here
        client = None  # OpenAI() if configured
        # response = client.chat.completions.create(...)
        
        return "Response", 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        total_calls = self.stats["cache_hits"] + self.stats["cache_misses"]
        cache_hit_rate = (self.stats["cache_hits"] / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "cache_hit_rate": round(cache_hit_rate, 2),
            "cache_hits": self.stats["cache_hits"],
            "cache_misses": self.stats["cache_misses"],
            "total_cost": round(self.stats["total_cost"], 4),
            "calls_by_tier": self.stats["calls_by_tier"],
            "estimated_savings": round(self.stats["cache_hits"] * 0.002, 4)  # $0.002 per cached call
        }

