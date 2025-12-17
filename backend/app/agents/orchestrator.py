from typing import Dict, List, Any, Optional
import asyncio
import uuid
from .base import BaseAgent, AgentStatus
from .implementations import MarketAnalysisAgent, WeatherAgent, SupplyChainAgent

class AgentFleet:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, Any] = {}
        
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent
        
    def get_available_agents(self) -> List[BaseAgent]:
        return [agent for agent in self.agents.values() 
                if agent.status == AgentStatus.IDLE]
    
    async def submit_task(self, task_type: str, data: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "data": data
        }
        await self.task_queue.put(task)
        return task_id
    
    async def orchestrate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordinated multi-agent workflow"""
        tasks = []
        
        # Submit parallel tasks
        market_task_id = await self.submit_task("market_analysis", workflow_data)
        weather_task_id = await self.submit_task("weather", workflow_data)
        supply_task_id = await self.submit_task("supply_chain", workflow_data)
        
        # Process tasks concurrently
        await asyncio.gather(
            self._process_single_task(market_task_id),
            self._process_single_task(weather_task_id),
            self._process_single_task(supply_task_id)
        )
        
        # Combine results
        return {
            "workflow_id": str(uuid.uuid4()),
            "market_analysis": self.results.get(market_task_id),
            "weather_data": self.results.get(weather_task_id),
            "supply_chain": self.results.get(supply_task_id)
        }
    
    async def _process_single_task(self, task_id: str):
        # Find task in queue and process
        task = await self.task_queue.get()
        agent = self._select_agent(task["task_type"])
        
        if agent:
            result = await agent.process_task(task)
            self.results[task_id] = result
    
    def _select_agent(self, task_type: str) -> Optional[BaseAgent]:
        agent_mapping = {
            "market_analysis": MarketAnalysisAgent,
            "weather": WeatherAgent,
            "supply_chain": SupplyChainAgent
        }
        
        # Find available agent of correct type
        for agent in self.get_available_agents():
            if isinstance(agent, agent_mapping.get(task_type, type(None))):
                return agent
        return None

# Global fleet instance
fleet = AgentFleet()

# Initialize agents
fleet.register_agent(MarketAnalysisAgent("market_agent_1"))
fleet.register_agent(WeatherAgent("weather_agent_1"))
fleet.register_agent(SupplyChainAgent("supply_agent_1"))
