from typing import Dict, Any, List
import asyncio
import os
import subprocess
from .base import BaseAgent

class BackendDevAgent(BaseAgent):
    """Agent specialized in FastAPI/Python backend development"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type")
        
        if task_type == "create_api_endpoint":
            return await self._create_api_endpoint(task["data"])
        elif task_type == "create_model":
            return await self._create_model(task["data"])
        elif task_type == "run_tests":
            return await self._run_tests()
        
        return {"error": "Unknown task type"}
    
    async def _create_api_endpoint(self, data: Dict[str, Any]) -> Dict[str, Any]:
        router_name = data["router"]
        endpoint_name = data["endpoint"]
        method = data.get("method", "GET")
        
        # Generate router code
        router_code = f'''
@router.{method.lower()}("/{endpoint_name}")
async def {endpoint_name}():
    """Generated endpoint for {endpoint_name}"""
    return {{"message": "Hello from {endpoint_name}"}}
'''
        
        return {
            "agent_id": self.agent_id,
            "result": {
                "code_generated": router_code,
                "file_path": f"backend/app/routers/{router_name}.py",
                "status": "success"
            }
        }
    
    async def _create_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        model_name = data["name"]
        fields = data.get("fields", [])
        
        model_code = f'''
class {model_name}(Base):
    __tablename__ = "{model_name.lower()}s"
    
    id = Column(Integer, primary_key=True, index=True)
'''
        
        for field in fields:
            model_code += f'    {field["name"]} = Column({field["type"]})\n'
        
        return {
            "agent_id": self.agent_id,
            "result": {
                "code_generated": model_code,
                "file_path": f"backend/app/models/{model_name.lower()}.py",
                "status": "success"
            }
        }
    
    async def _run_tests(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-v"],
                cwd="backend",
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "agent_id": self.agent_id,
                "result": {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "status": "success" if result.returncode == 0 else "failed"
                }
            }
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "result": {"error": str(e), "status": "error"}
            }

class FrontendDevAgent(BaseAgent):
    """Agent specialized in React/TypeScript frontend development"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type")
        
        if task_type == "create_component":
            return await self._create_component(task["data"])
        elif task_type == "create_page":
            return await self._create_page(task["data"])
        elif task_type == "run_build":
            return await self._run_build()
        
        return {"error": "Unknown task type"}
    
    async def _create_component(self, data: Dict[str, Any]) -> Dict[str, Any]:
        component_name = data["name"]
        props = data.get("props", [])
        
        props_interface = ""
        if props:
            props_interface = f'''
interface {component_name}Props {{
{chr(10).join(f"  {prop['name']}: {prop['type']};" for prop in props)}
}}
'''
        
        component_code = f'''{props_interface}
export function {component_name}({f"{{ {', '.join(prop['name'] for prop in props)} }}: {component_name}Props" if props else ""}) {{
  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold">{component_name}</h2>
      <p>Generated component for AgriDAO</p>
    </div>
  );
}}'''
        
        return {
            "agent_id": self.agent_id,
            "result": {
                "code_generated": component_code,
                "file_path": f"frontend/src/components/{component_name}.tsx",
                "status": "success"
            }
        }
    
    async def _create_page(self, data: Dict[str, Any]) -> Dict[str, Any]:
        page_name = data["name"]
        
        page_code = f'''
import {{ Card, CardContent, CardHeader, CardTitle }} from '@/components/ui/card';

export function {page_name}() {{
  return (
    <div className="container mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>{page_name}</CardTitle>
        </CardHeader>
        <CardContent>
          <p>Generated page for AgriDAO platform</p>
        </CardContent>
      </Card>
    </div>
  );
}}'''
        
        return {
            "agent_id": self.agent_id,
            "result": {
                "code_generated": page_code,
                "file_path": f"frontend/src/pages/{page_name}.tsx",
                "status": "success"
            }
        }
    
    async def _run_build(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd="frontend",
                capture_output=True,
                text=True,
                timeout=60
            )
            return {
                "agent_id": self.agent_id,
                "result": {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "status": "success" if result.returncode == 0 else "failed"
                }
            }
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "result": {"error": str(e), "status": "error"}
            }

class DatabaseDevAgent(BaseAgent):
    """Agent specialized in database operations and migrations"""
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("task_type")
        
        if task_type == "create_migration":
            return await self._create_migration(task["data"])
        elif task_type == "run_migration":
            return await self._run_migration()
        elif task_type == "seed_data":
            return await self._seed_data(task["data"])
        
        return {"error": "Unknown task type"}
    
    async def _create_migration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        description = data["description"]
        
        try:
            result = subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", description],
                cwd="backend",
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "agent_id": self.agent_id,
                "result": {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "status": "success" if result.returncode == 0 else "failed",
                    "note": "Database connection required for migration generation"
                }
            }
        except Exception as e:
            # Generate manual migration template when DB is offline
            migration_template = f'''"""create {description}

Revision ID: manual_revision
Revises: 
Create Date: {data.get("timestamp", "2024-01-01 00:00:00")}

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'manual_revision'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add your upgrade operations here
    pass

def downgrade():
    # Add your downgrade operations here
    pass
'''
            return {
                "agent_id": self.agent_id,
                "result": {
                    "code_generated": migration_template,
                    "file_path": f"backend/alembic/versions/manual_{description.replace(' ', '_')}.py",
                    "status": "offline_template",
                    "note": "Generated template migration (database offline)"
                }
            }
    
    async def _run_migration(self) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd="backend",
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "agent_id": self.agent_id,
                "result": {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "status": "success" if result.returncode == 0 else "failed"
                }
            }
        except Exception as e:
            return {
                "agent_id": self.agent_id,
                "result": {"error": str(e), "status": "error"}
            }
    
    async def _seed_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Generate seed data script
        seed_script = '''
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User

def seed_users():
    db = SessionLocal()
    try:
        # Add sample users
        users = [
            User(email="farmer@agridao.com", name="Sample Farmer", role="farmer"),
            User(email="buyer@agridao.com", name="Sample Buyer", role="buyer"),
        ]
        for user in users:
            db.add(user)
        db.commit()
        print("Users seeded successfully")
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
'''
        
        return {
            "agent_id": self.agent_id,
            "result": {
                "code_generated": seed_script,
                "file_path": "backend/seed_data.py",
                "status": "success"
            }
        }
