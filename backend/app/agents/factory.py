"""
Agent Factory - Creates and manages the AgriDAO agent fleet
"""
from typing import Dict, List
from .base import BaseAgent, AgentType
from .advisory_agent import AdvisoryAgent

class AgentFactory:
    """Factory to create and manage all AgriDAO agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
    
    def create_agent_fleet(self) -> Dict[str, BaseAgent]:
        """Create all agents defined in the agent definitions"""
        
        # Create advisory agent (already exists)
        advisory = AdvisoryAgent()
        self.agents[advisory.agent_id] = advisory
        
        # Create other agents (simplified versions)
        agent_configs = [
            {"id": "api_agent", "type": AgentType.ADVISORY, "actions": ["create_endpoint", "update_api"]},
            {"id": "database_agent", "type": AgentType.ADVISORY, "actions": ["create_migration", "optimize_query"]},
            {"id": "ui_agent", "type": AgentType.ADVISORY, "actions": ["create_component", "update_styles"]},
            {"id": "devops_agent", "type": AgentType.ADVISORY, "actions": ["deploy", "monitor"]},
            {"id": "security_agent", "type": AgentType.ADVISORY, "actions": ["audit", "scan_vulnerabilities"]},
        ]
        
        for config in agent_configs:
            agent = self._create_simple_agent(config)
            self.agents[agent.agent_id] = agent
        
        return self.agents
    
    def _create_simple_agent(self, config: Dict) -> BaseAgent:
        """Create a simple agent with basic functionality"""
        
        class SimpleAgent(BaseAgent):
            def __init__(self, agent_id: str, agent_type: AgentType, allowed_actions: List[str]):
                super().__init__(agent_id, agent_type)
                self.allowed_actions = allowed_actions
            
            async def _execute_action(self, action: str, params: Dict):
                return {"action": action, "params": params, "status": "completed"}
            
            def _get_allowed_actions(self) -> List[str]:
                return self.allowed_actions
        
        return SimpleAgent(
            config["id"], 
            config["type"], 
            config["actions"]
        )
    
    def get_agent(self, agent_id: str) -> BaseAgent:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all agent IDs"""
        return list(self.agents.keys())
