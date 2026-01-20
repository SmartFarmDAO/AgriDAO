from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..agents.dev_orchestrator import dev_fleet

router = APIRouter(prefix="/dev", tags=["development"])

@router.post("/develop-feature")
async def develop_feature(feature_spec: Dict[str, Any]):
    """Develop a complete feature using specialized agents"""
    try:
        result = await dev_fleet.develop_feature(feature_spec)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workflow/{workflow_type}")
async def run_workflow(workflow_type: str, params: Dict[str, Any] = None):
    """Run predefined development workflows"""
    try:
        result = await dev_fleet.run_development_workflow(workflow_type, params or {})
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/status")
async def get_dev_agents_status():
    """Get status of all development agents"""
    status = {}
    for agent_id, agent in dev_fleet.agents.items():
        status[agent_id] = {
            "status": agent.status.value,
            "current_task": agent.current_task,
            "specialization": {
                "backend_dev": "FastAPI/Python backend development",
                "frontend_dev": "React/TypeScript frontend development", 
                "database_dev": "Database operations and migrations"
            }.get(agent_id, "Unknown")
        }
    return {"agents": status}

@router.post("/quick-crud")
async def create_quick_crud(entity_name: str, fields: list = None):
    """Quick CRUD generation for AgriDAO entities"""
    if not fields:
        fields = [
            {"name": "name", "type": "String"},
            {"name": "description", "type": "Text"},
            {"name": "created_at", "type": "DateTime"}
        ]
    
    try:
        result = await dev_fleet.run_development_workflow("full_stack_crud", {
            "entity": entity_name,
            "fields": fields
        })
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
