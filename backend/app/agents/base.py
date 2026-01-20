from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum
import asyncio
import logging

logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

class AgentType(str, Enum):
    ADVISORY = "advisory"
    MARKET = "market"
    SUPPLY_CHAIN = "supply_chain"
    FINANCE = "finance"
    GOVERNANCE = "governance"

class ActionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class BaseAgent(ABC):
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.status = AgentStatus.IDLE
        self.current_task: Optional[str] = None
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        self.status = AgentStatus.BUSY
        self.current_task = task.get("task_id")
        
        try:
            result = await self.execute(task)
            self.status = AgentStatus.IDLE
            self.current_task = None
            return result
        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error(f"Agent {self.agent_id} failed: {e}")
            raise
