from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from ..agents.orchestrator import fleet

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/orchestrate")
async def orchestrate_agents(workflow_data: Dict[str, Any]):
    """Orchestrate multi-agent workflow for agricultural insights"""
    try:
        result = await fleet.orchestrate_workflow(workflow_data)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_fleet_status():
    """Get current status of all agents in the fleet"""
    status = {}
    for agent_id, agent in fleet.agents.items():
        status[agent_id] = {
            "status": agent.status.value,
            "current_task": agent.current_task
        }
    return {"agents": status}
