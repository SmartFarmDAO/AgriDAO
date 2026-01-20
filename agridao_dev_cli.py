#!/usr/bin/env python3
"""
AgriDAO Development CLI - Interface for specialized development agents
Usage: python agridao_dev_cli.py [command] [options]
"""
import asyncio
import json
import sys
import argparse
from backend.app.agents.dev_orchestrator import dev_fleet

async def create_crud(entity_name: str, fields: list = None):
    """Create full-stack CRUD for an entity"""
    print(f"🚀 Creating CRUD for {entity_name}...")
    
    if not fields:
        fields = [
            {"name": "name", "type": "String"},
            {"name": "description", "type": "Text"},
            {"name": "created_at", "type": "DateTime"}
        ]
    
    result = await dev_fleet.run_development_workflow("full_stack_crud", {
        "entity": entity_name,
        "fields": fields
    })
    
    print("✅ CRUD Creation Complete!")
    print(json.dumps(result, indent=2))
    return result

async def create_api_component(api_name: str, component_name: str):
    """Create API endpoint with frontend component"""
    print(f"🔧 Creating API '{api_name}' with component '{component_name}'...")
    
    result = await dev_fleet.run_development_workflow("api_with_frontend", {
        "api_name": api_name,
        "component_name": component_name
    })
    
    print("✅ API + Component Creation Complete!")
    print(json.dumps(result, indent=2))
    return result

async def setup_database(migration_desc: str = "AgriDAO database setup"):
    """Setup database with migrations"""
    print("🗄️ Setting up database...")
    
    result = await dev_fleet.run_development_workflow("database_setup", {
        "migration_description": migration_desc
    })
    
    print("✅ Database Setup Complete!")
    print(json.dumps(result, indent=2))
    return result

async def run_tests():
    """Run all tests"""
    print("🧪 Running tests...")
    
    result = await dev_fleet.run_development_workflow("run_tests")
    
    print("✅ Tests Complete!")
    print(json.dumps(result, indent=2))
    return result

async def develop_custom_feature(feature_spec: dict):
    """Develop custom feature from specification"""
    print(f"🎯 Developing feature: {feature_spec.get('name', 'Custom Feature')}")
    
    result = await dev_fleet.develop_feature(feature_spec)
    
    print("✅ Feature Development Complete!")
    print(json.dumps(result, indent=2))
    return result

async def show_agent_status():
    """Show status of all development agents"""
    print("📊 Development Agent Status:")
    print("=" * 50)
    
    for agent_id, agent in dev_fleet.agents.items():
        specialization = {
            "backend_dev": "FastAPI/Python Backend",
            "frontend_dev": "React/TypeScript Frontend", 
            "database_dev": "Database & Migrations"
        }.get(agent_id, "Unknown")
        
        print(f"🤖 {agent_id}")
        print(f"   Status: {agent.status.value}")
        print(f"   Specialization: {specialization}")
        print(f"   Current Task: {agent.current_task or 'None'}")
        print()

def main():
    parser = argparse.ArgumentParser(description="AgriDAO Development CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # CRUD command
    crud_parser = subparsers.add_parser("crud", help="Create full-stack CRUD")
    crud_parser.add_argument("entity", help="Entity name (e.g., Product, User)")
    crud_parser.add_argument("--fields", help="JSON string of fields", default=None)
    
    # API + Component command
    api_parser = subparsers.add_parser("api-component", help="Create API with frontend component")
    api_parser.add_argument("api_name", help="API endpoint name")
    api_parser.add_argument("component_name", help="React component name")
    
    # Database setup command
    db_parser = subparsers.add_parser("setup-db", help="Setup database")
    db_parser.add_argument("--description", help="Migration description", default="AgriDAO database setup")
    
    # Test command
    subparsers.add_parser("test", help="Run all tests")
    
    # Status command
    subparsers.add_parser("status", help="Show agent status")
    
    # Custom feature command
    feature_parser = subparsers.add_parser("feature", help="Develop custom feature")
    feature_parser.add_argument("spec_file", help="JSON file with feature specification")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run the appropriate command
    if args.command == "crud":
        fields = json.loads(args.fields) if args.fields else None
        asyncio.run(create_crud(args.entity, fields))
    
    elif args.command == "api-component":
        asyncio.run(create_api_component(args.api_name, args.component_name))
    
    elif args.command == "setup-db":
        asyncio.run(setup_database(args.description))
    
    elif args.command == "test":
        asyncio.run(run_tests())
    
    elif args.command == "status":
        asyncio.run(show_agent_status())
    
    elif args.command == "feature":
        try:
            with open(args.spec_file, 'r') as f:
                feature_spec = json.load(f)
            asyncio.run(develop_custom_feature(feature_spec))
        except FileNotFoundError:
            print(f"❌ Feature spec file not found: {args.spec_file}")
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in feature spec file: {args.spec_file}")

if __name__ == "__main__":
    main()
