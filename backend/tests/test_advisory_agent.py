"""
Tests for Advisory Agent
"""
import pytest
from app.agents.advisory_agent import AdvisoryAgent
from app.agents.base import ActionStatus

@pytest.mark.asyncio
async def test_advisory_agent_weather_forecast():
    """Test weather forecast action"""
    agent = AdvisoryAgent()
    
    result = await agent.execute(
        action="get_weather_forecast",
        params={"location": "Dhaka, Bangladesh", "days": 7}
    )
    
    assert result["status"] == ActionStatus.SUCCESS
    assert "forecast" in result["result"]
    assert result["result"]["location"] == "Dhaka, Bangladesh"

@pytest.mark.asyncio
async def test_advisory_agent_crop_advice():
    """Test crop advice action"""
    agent = AdvisoryAgent()
    
    result = await agent.execute(
        action="get_crop_advice",
        params={
            "crop": "rice",
            "location": "Dhaka",
            "growth_stage": "flowering"
        }
    )
    
    assert result["status"] == ActionStatus.SUCCESS
    assert "recommendations" in result["result"]
    assert result["result"]["crop"] == "rice"

@pytest.mark.asyncio
async def test_advisory_agent_rate_limiting():
    """Test rate limiting works"""
    agent = AdvisoryAgent(agent_id="test_agent")
    agent.max_actions_per_minute = 3  # Set low limit for testing
    
    # Execute 3 actions - should succeed
    for i in range(3):
        result = await agent.execute(
            action="get_weather_forecast",
            params={"location": "Dhaka"}
        )
        assert result["status"] == ActionStatus.SUCCESS
    
    # 4th action should be rate limited
    result = await agent.execute(
        action="get_weather_forecast",
        params={"location": "Dhaka"}
    )
    assert result["status"] == ActionStatus.FAILED
    assert "rate_limit_exceeded" in result["error"]["code"]

@pytest.mark.asyncio
async def test_advisory_agent_permission_denied():
    """Test permission check works"""
    agent = AdvisoryAgent()
    
    result = await agent.execute(
        action="unauthorized_action",
        params={}
    )
    
    assert result["status"] == ActionStatus.FAILED
    assert "permission_denied" in result["error"]["code"]

@pytest.mark.asyncio
async def test_advisory_agent_invalid_params():
    """Test parameter validation"""
    agent = AdvisoryAgent()
    
    # Missing required parameter
    result = await agent.execute(
        action="get_crop_advice",
        params={"crop": "rice"}  # Missing location
    )
    
    assert result["status"] == ActionStatus.FAILED
    assert "invalid_parameters" in result["error"]["code"]

@pytest.mark.asyncio
async def test_advisory_agent_notification_length_limit():
    """Test notification message length limit"""
    agent = AdvisoryAgent()
    
    long_message = "x" * 501  # Exceeds 500 char limit
    
    result = await agent.execute(
        action="send_notification",
        params={
            "user_id": "user123",
            "message": long_message
        }
    )
    
    assert result["status"] == ActionStatus.FAILED
    assert "message too long" in result["error"]["message"]

@pytest.mark.asyncio
async def test_advisory_agent_stats():
    """Test agent statistics"""
    agent = AdvisoryAgent()
    
    # Execute some actions
    await agent.execute(
        action="get_weather_forecast",
        params={"location": "Dhaka"}
    )
    await agent.execute(
        action="get_crop_advice",
        params={"crop": "rice", "location": "Dhaka"}
    )
    
    stats = agent.get_stats()
    
    assert stats["total_actions"] == 2
    assert stats["successful_actions"] == 2
    assert stats["success_rate"] == 1.0
    assert stats["agent_type"] == "advisory"
