from typing import Dict, Any, List
import asyncio
import uuid
from .dev_agents import BackendDevAgent, FrontendDevAgent, DatabaseDevAgent
from .base import BaseAgent

class AgriDAODevFleet:
    """Development fleet specialized for AgriDAO system development"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: Dict[str, Any] = {}
        
        # Initialize development agents
        self.register_agent(BackendDevAgent("backend_dev"))
        self.register_agent(FrontendDevAgent("frontend_dev"))
        self.register_agent(DatabaseDevAgent("database_dev"))
        
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.agent_id] = agent
    
    async def develop_feature(self, feature_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate full-stack feature development"""
        feature_name = feature_spec["name"]
        components = feature_spec.get("components", [])
        
        tasks = []
        task_ids = []
        
        # Backend tasks
        if "backend" in components:
            backend_spec = feature_spec.get("backend", {})
            if backend_spec.get("api_endpoint"):
                task_id = await self._submit_task("backend_dev", "create_api_endpoint", backend_spec["api_endpoint"])
                task_ids.append(task_id)
            
            if backend_spec.get("model"):
                task_id = await self._submit_task("backend_dev", "create_model", backend_spec["model"])
                task_ids.append(task_id)
        
        # Frontend tasks
        if "frontend" in components:
            frontend_spec = feature_spec.get("frontend", {})
            if frontend_spec.get("component"):
                task_id = await self._submit_task("frontend_dev", "create_component", frontend_spec["component"])
                task_ids.append(task_id)
            
            if frontend_spec.get("page"):
                task_id = await self._submit_task("frontend_dev", "create_page", frontend_spec["page"])
                task_ids.append(task_id)
        
        # Database tasks
        if "database" in components:
            db_spec = feature_spec.get("database", {})
            if db_spec.get("migration"):
                task_id = await self._submit_task("database_dev", "create_migration", db_spec["migration"])
                task_ids.append(task_id)
        
        # Execute all tasks concurrently
        await asyncio.gather(*[self._process_task(task_id) for task_id in task_ids])
        
        # Collect results
        feature_results = {
            "feature_name": feature_name,
            "workflow_id": str(uuid.uuid4()),
            "tasks_completed": len(task_ids),
            "results": {task_id: self.results.get(task_id) for task_id in task_ids}
        }
        
        return feature_results
    
    async def run_development_workflow(self, workflow_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run predefined development workflows"""
        
        if workflow_type == "full_stack_crud":
            return await self._create_full_stack_crud(params or {})
        elif workflow_type == "api_with_frontend":
            return await self._create_api_with_frontend(params or {})
        elif workflow_type == "database_setup":
            return await self._setup_database(params or {})
        elif workflow_type == "run_tests":
            return await self._run_all_tests()
        
        return {"error": f"Unknown workflow type: {workflow_type}"}
    
    async def _create_full_stack_crud(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a complete CRUD feature with backend API, frontend component, and database model"""
        entity_name = params.get("entity", "Product")
        fields = params.get("fields", [{"name": "name", "type": "String"}, {"name": "price", "type": "Float"}])
        
        feature_spec = {
            "name": f"{entity_name} CRUD",
            "components": ["backend", "frontend", "database"],
            "backend": {
                "api_endpoint": {
                    "router": entity_name.lower(),
                    "endpoint": f"create_{entity_name.lower()}",
                    "method": "POST"
                },
                "model": {
                    "name": entity_name,
                    "fields": fields
                }
            },
            "frontend": {
                "component": {
                    "name": f"{entity_name}Form",
                    "props": [{"name": "onSubmit", "type": "() => void"}]
                },
                "page": {
                    "name": f"{entity_name}Management"
                }
            },
            "database": {
                "migration": {
                    "description": f"create {entity_name.lower()} table"
                }
            }
        }
        
        return await self.develop_feature(feature_spec)
    
    async def _create_api_with_frontend(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create API endpoint with corresponding frontend component"""
        api_name = params.get("api_name", "sample_api")
        component_name = params.get("component_name", "SampleComponent")
        
        # Backend API
        backend_task = await self._submit_task("backend_dev", "create_api_endpoint", {
            "router": "api",
            "endpoint": api_name,
            "method": "GET"
        })
        
        # Frontend component
        frontend_task = await self._submit_task("frontend_dev", "create_component", {
            "name": component_name,
            "props": [{"name": "data", "type": "any"}]
        })
        
        # Execute tasks
        await asyncio.gather(
            self._process_task(backend_task),
            self._process_task(frontend_task)
        )
        
        return {
            "workflow_type": "api_with_frontend",
            "backend_result": self.results.get(backend_task),
            "frontend_result": self.results.get(frontend_task)
        }
    
    async def _setup_database(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Setup database with migrations and seed data"""
        migration_desc = params.get("migration_description", "initial setup")
        
        # Create migration
        migration_task = await self._submit_task("database_dev", "create_migration", {
            "description": migration_desc
        })
        
        # Run migration
        run_migration_task = await self._submit_task("database_dev", "run_migration", {})
        
        # Seed data
        seed_task = await self._submit_task("database_dev", "seed_data", {})
        
        # Execute sequentially (migration -> run -> seed)
        await self._process_task(migration_task)
        await self._process_task(run_migration_task)
        await self._process_task(seed_task)
        
        return {
            "workflow_type": "database_setup",
            "migration_result": self.results.get(migration_task),
            "run_result": self.results.get(run_migration_task),
            "seed_result": self.results.get(seed_task)
        }
    
    async def _run_all_tests(self) -> Dict[str, Any]:
        """Run tests for both backend and frontend"""
        backend_test_task = await self._submit_task("backend_dev", "run_tests", {})
        frontend_test_task = await self._submit_task("frontend_dev", "run_build", {})
        
        await asyncio.gather(
            self._process_task(backend_test_task),
            self._process_task(frontend_test_task)
        )
        
        return {
            "workflow_type": "run_tests",
            "backend_tests": self.results.get(backend_test_task),
            "frontend_build": self.results.get(frontend_test_task)
        }
    
    async def _submit_task(self, agent_id: str, task_type: str, data: Dict[str, Any]) -> str:
        task_id = str(uuid.uuid4())
        task = {
            "task_id": task_id,
            "agent_id": agent_id,
            "task_type": task_type,
            "data": data
        }
        await self.task_queue.put(task)
        return task_id
    
    async def _process_task(self, task_id: str):
        # Find and process the task
        task = await self.task_queue.get()
        agent = self.agents.get(task["agent_id"])
        
        if agent:
            result = await agent.process_task(task)
            self.results[task_id] = result

# Global development fleet instance
dev_fleet = AgriDAODevFleet()
