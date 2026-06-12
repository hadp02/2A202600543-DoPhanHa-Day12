"""
Cost Guard with Redis
"""
import time
from fastapi import HTTPException
from app.config import settings

def check_and_record_cost(r, user_id: str, input_tokens: int, output_tokens: int):
    """
    Track daily cost per user using Redis.
    """
    if not r:
        return 0.0
        
    today = time.strftime("%Y-%m-%d")
    cost_key = f"cost:{user_id}:{today}"
    
    # Calculate the cost of the current request
    # Formula: $0.15 / 1M input tokens, $0.60 / 1M output tokens
    cost = (input_tokens / 1000) * 0.00015 + (output_tokens / 1000) * 0.0006
    
    # Get current cost from Redis
    current_cost = float(r.get(cost_key) or 0.0)
    
    if current_cost >= settings.daily_budget_usd:
        raise HTTPException(
            status_code=503, 
            detail=f"Daily budget exhausted. Current: ${current_cost:.4f}"
        )
        
    # Increment the cost
    new_cost = r.incrbyfloat(cost_key, cost)
    # Keep the cost record for 2 days
    r.expire(cost_key, 86400 * 2) 
    
    return new_cost

def get_daily_cost(r, user_id: str) -> float:
    if not r:
        return 0.0
    today = time.strftime("%Y-%m-%d")
    cost_key = f"cost:{user_id}:{today}"
    return float(r.get(cost_key) or 0.0)
