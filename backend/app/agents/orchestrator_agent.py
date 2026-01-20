"""
Orchestrator Agent - Master coordinator for all AgriDAO agents
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging
from .base import BaseAgent, AgentType, ActionStatus

class OrchestratorAgent(BaseAgent):
    """
    Master agent that coordinates all other specialized agents
    Breaks down complex tasks and assigns them to appropriate agents
    """
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator_001",
            agent_type=AgentType.ADVISORY,  # Using existing enum
            max_actions_per_minute=50,
            requires_approval_threshold={
                "deploy_to_production": lambda params: True,
                "modify_database_schema": lambda params: True,
                "update_smart_contracts": lambda params: True
            }
        )
        self.registered_agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict] = []
        self.active_tasks: Dict[str, Dict] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent with the orchestrator"""
        self.registered_agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_id} ({agent.agent_type})")
    
    async def _execute_action(self, action: str, params: Dict) -> Any:
        """Execute orchestrator actions"""
        if action == "coordinate_task":
            return await self._coordinate_task(params)
        elif action == "assign_task":
            return await self._assign_task(params)
        elif action == "monitor_progress":
            return await self._monitor_progress(params)
        elif action == "resolve_conflict":
            return await self._resolve_conflict(params)
        elif action == "get_system_status":
            return await self._get_system_status()
        else:
            raise ValueError(f"Unknown action: {action}")
    
    def _get_allowed_actions(self) -> List[str]:
        return [
            "coordinate_task",
            "assign_task", 
            "monitor_progress",
            "resolve_conflict",
            "get_system_status",
            "deploy_to_production",
            "emergency_stop"
        ]
    
    async def _coordinate_task(self, params: Dict) -> Dict:
        """Break down high-level task into subtasks and coordinate execution"""
        task_description = params.get("description")
        priority = params.get("priority", "medium")
        deadline = params.get("deadline")
        
        # Analyze task and break it down
        subtasks = self._analyze_and_decompose(task_description)
        
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        coordination_plan = {
            "task_id": task_id,
            "description": task_description,
            "priority": priority,
            "deadline": deadline,
            "subtasks": subtasks,
            "status": "planned",
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.active_tasks[task_id] = coordination_plan
        
        # Start executing subtasks
        await self._execute_coordination_plan(coordination_plan)
        
        return coordination_plan
    
    def _analyze_and_decompose(self, description: str) -> List[Dict]:
        """Analyze task description and break into subtasks"""
        subtasks = []
        
        # Simple keyword-based task decomposition
        if "api" in description.lower():
            subtasks.append({
                "type": "api_development",
                "agent_type": "api",
                "description": "Implement API endpoints",
                "dependencies": []
            })
        
        if "database" in description.lower() or "schema" in description.lower():
            subtasks.append({
                "type": "database_work", 
                "agent_type": "database",
                "description": "Handle database changes",
                "dependencies": []
            })
        
        if "frontend" in description.lower() or "ui" in description.lower():
            subtasks.append({
                "type": "ui_development",
                "agent_type": "ui", 
                "description": "Implement UI components",
                "dependencies": ["api_development"]
            })
        
        if "smart contract" in description.lower() or "blockchain" in description.lower():
            subtasks.append({
                "type": "smart_contract",
                "agent_type": "smart_contract",
                "description": "Develop smart contracts",
                "dependencies": []
            })
        
        if "deploy" in description.lower():
            subtasks.append({
                "type": "deployment",
                "agent_type": "devops",
                "description": "Handle deployment",
                "dependencies": ["api_development", "ui_development"]
            })
        
        return subtasks
    
    async def _execute_coordination_plan(self, plan: Dict):
        """Execute the coordination plan by assigning tasks to agents"""
        for subtask in plan["subtasks"]:
            # Check dependencies
            if self._dependencies_met(subtask, plan):
                await self._assign_subtask(subtask, plan["task_id"])
    
    def _dependencies_met(self, subtask: Dict, plan: Dict) -> bool:
        """Check if subtask dependencies are completed"""
        for dep in subtask.get("dependencies", []):
            # Check if dependency subtask is completed
            dep_completed = any(
                st.get("status") == "completed" 
                for st in plan["subtasks"] 
                if st["type"] == dep
            )
            if not dep_completed:
                return False
        return True
    
    async def _assign_subtask(self, subtask: Dict, parent_task_id: str):
        """Assign subtask to appropriate agent"""
        agent_type = subtask["agent_type"]
        
        # Find appropriate agent (simplified - in reality would be more sophisticated)
        target_agent = None
        for agent in self.registered_agents.values():
            if agent_type in agent.agent_id.lower():
                target_agent = agent
                break
        
        if target_agent:
            try:
                result = await target_agent.execute(
                    action="handle_subtask",
                    params={
                        "subtask": subtask,
                        "parent_task_id": parent_task_id
                    }
                )
                subtask["status"] = "assigned"
                subtask["assigned_to"] = target_agent.agent_id
                subtask["result"] = result
            except Exception as e:
                self.logger.error(f"Failed to assign subtask: {e}")
                subtask["status"] = "failed"
                subtask["error"] = str(e)
        else:
            self.logger.warning(f"No agent found for type: {agent_type}")
            subtask["status"] = "no_agent_available"
    
    async def _assign_task(self, params: Dict) -> Dict:
        """Directly assign a task to a specific agent"""
        agent_id = params.get("agent_id")
        task = params.get("task")
        
        if agent_id not in self.registered_agents:
            raise ValueError(f"Agent not found: {agent_id}")
        
        agent = self.registered_agents[agent_id]
        result = await agent.execute(
            action=task.get("action"),
            params=task.get("params", {})
        )
        
        return {
            "agent_id": agent_id,
            "task": task,
            "result": result,
            "assigned_at": datetime.utcnow().isoformat()
        }
    
    async def _monitor_progress(self, params: Dict) -> Dict:
        """Monitor progress of all active tasks"""
        task_id = params.get("task_id")
        
        if task_id and task_id in self.active_tasks:
            return self.active_tasks[task_id]
        
        # Return all active tasks
        return {
            "active_tasks": len(self.active_tasks),
            "tasks": list(self.active_tasks.values()),
            "agent_stats": {
                agent_id: agent.get_stats()
                for agent_id, agent in self.registered_agents.items()
            }
        }
    
    async def _resolve_conflict(self, params: Dict) -> Dict:
        """Resolve conflicts between agents"""
        conflict_type = params.get("type")
        involved_agents = params.get("agents", [])
        context = params.get("context", {})
        
        resolution = {
            "conflict_id": f"conflict_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "type": conflict_type,
            "involved_agents": involved_agents,
            "context": context,
            "resolution": "escalated_to_human",  # Default resolution
            "resolved_at": datetime.utcnow().isoformat()
        }
        
        # Simple conflict resolution logic
        if conflict_type == "resource_conflict":
            resolution["resolution"] = "sequential_execution"
        elif conflict_type == "priority_conflict":
            resolution["resolution"] = "highest_priority_wins"
        
        return resolution
    
    async def _get_system_status(self) -> Dict:
        """Get overall system status"""
        return {
            "orchestrator_status": "active",
            "registered_agents": len(self.registered_agents),
            "active_tasks": len(self.active_tasks),
            "task_queue_size": len(self.task_queue),
            "agents": {
                agent_id: {
                    "status": "active",
                    "stats": agent.get_stats()
                }
                for agent_id, agent in self.registered_agents.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
