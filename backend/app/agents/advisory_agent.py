"""
Advisory Agent - Provides farming advice with low autonomy
"""
from typing import Dict, Any, List
from .base import BaseAgent, AgentType

class AdvisoryAgent(BaseAgent):
    """
    Low autonomy agent for providing farming advice
    
    Capabilities:
    - Weather forecasts
    - Crop recommendations
    - Pest management advice
    - Market insights
    
    Security:
    - Read-only access
    - No financial transactions
    - Rate limited to 100/minute
    """
    
    def __init__(self, agent_id: str = "advisory_001"):
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.ADVISORY,
            max_actions_per_minute=100,
            requires_approval_threshold={}  # No approvals needed
        )
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the assigned task"""
        action = task.get("action")
        params = task.get("params", {})
        
        if not action:
            raise ValueError("Task missing required 'action' field")
            
        # Validate params
        validation = self._validate_params(action, params)
        if not validation["valid"]:
            raise ValueError(f"Invalid parameters: {validation.get('error')}")
            
        result = await self._execute_action(action, params)
        
        return {
            "status": "success",
            "action": action,
            "data": result,
            "agent_id": self.agent_id,
            "timestamp": "2024-01-31T12:00:00" # Simplified timestamp
        }
    
    def _get_allowed_actions(self) -> List[str]:
        """Actions this agent can perform"""
        return [
            "get_weather_forecast",
            "get_crop_advice",
            "get_pest_management",
            "get_market_insights",
            "send_notification"
        ]
    
    async def _execute_action(self, action: str, params: Dict) -> Any:
        """Execute advisory actions"""
        
        if action == "get_weather_forecast":
            return await self._get_weather_forecast(params)
        
        elif action == "get_crop_advice":
            return await self._get_crop_advice(params)
        
        elif action == "get_pest_management":
            return await self._get_pest_management(params)
        
        elif action == "get_market_insights":
            return await self._get_market_insights(params)
        
        elif action == "send_notification":
            return await self._send_notification(params)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _get_weather_forecast(self, params: Dict) -> Dict:
        """Get weather forecast for location"""
        location = params.get("location")
        days = params.get("days", 7)
        
        # TODO: Integrate with real weather API
        return {
            "location": location,
            "forecast": [
                {
                    "date": "2025-12-03",
                    "temp_high": 32,
                    "temp_low": 24,
                    "humidity": 75,
                    "precipitation": 20,
                    "conditions": "Partly cloudy"
                }
            ],
            "alerts": [
                "Heavy rain expected in 3 days - consider harvesting early"
            ]
        }
    
    async def _get_crop_advice(self, params: Dict) -> Dict:
        """Get crop-specific advice"""
        crop = params.get("crop")
        location = params.get("location")
        growth_stage = params.get("growth_stage", "unknown")
        
        # TODO: Integrate with AI model
        advice = {
            "crop": crop,
            "location": location,
            "growth_stage": growth_stage,
            "recommendations": [
                f"Monitor soil moisture for {crop}",
                "Apply organic fertilizer during early morning",
                "Check for pest activity daily"
            ],
            "optimal_harvest_window": "2-3 weeks",
            "expected_yield": "Estimate based on current conditions"
        }
        
        return advice
    
    async def _get_pest_management(self, params: Dict) -> Dict:
        """Get pest management advice"""
        crop = params.get("crop")
        pest_type = params.get("pest_type", "general")
        
        return {
            "crop": crop,
            "pest_type": pest_type,
            "prevention": [
                "Use integrated pest management",
                "Encourage beneficial insects",
                "Maintain proper spacing between plants"
            ],
            "treatment": [
                "Apply neem oil spray in early morning",
                "Remove affected leaves",
                "Consider biological controls"
            ],
            "monitoring": "Check plants every 2-3 days"
        }
    
    async def _get_market_insights(self, params: Dict) -> Dict:
        """Get market price insights"""
        crop = params.get("crop")
        region = params.get("region")
        
        # TODO: Integrate with market data API
        return {
            "crop": crop,
            "region": region,
            "current_price": 45.50,
            "currency": "USD",
            "trend": "increasing",
            "forecast_7days": 48.00,
            "recommendation": "Good time to sell - prices trending up"
        }
    
    async def _send_notification(self, params: Dict) -> Dict:
        """Send notification to user"""
        user_id = params.get("user_id")
        message = params.get("message")
        priority = params.get("priority", "normal")
        
        # TODO: Integrate with notification service
        self.logger.info(f"Notification sent to user {user_id}: {message}")
        
        return {
            "sent": True,
            "user_id": user_id,
            "message": message,
            "priority": priority,
            "delivery_method": "push"
        }
    
    def _validate_params(self, action: str, params: Dict) -> Dict:
        """Validate parameters for each action"""
        
        if action == "get_weather_forecast":
            if "location" not in params:
                return {"valid": False, "error": "location is required"}
        
        elif action == "get_crop_advice":
            if "crop" not in params or "location" not in params:
                return {"valid": False, "error": "crop and location are required"}
        
        elif action == "send_notification":
            if "user_id" not in params or "message" not in params:
                return {"valid": False, "error": "user_id and message are required"}
            
            # Security: Limit message length
            if len(params["message"]) > 500:
                return {"valid": False, "error": "message too long (max 500 chars)"}
        
        return {"valid": True}
