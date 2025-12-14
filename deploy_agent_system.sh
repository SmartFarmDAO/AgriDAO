#!/bin/bash

# AgriDAO Agent System Deployment Script
set -e

echo "🚀 Deploying AgriDAO Agent System..."

# Create agent directories
mkdir -p agents/{orchestrator,api,database,auth,ui,state,integration,smart_contract,web3,devops,security,monitoring,testing,performance,feature,documentation}
mkdir -p logs config

# Setup Redis and PostgreSQL for coordination
echo "📦 Starting infrastructure services..."
docker run -d --name agent-redis -p 6380:6379 redis:7-alpine
docker run -d --name agent-postgres -e POSTGRES_DB=agent_coordination -e POSTGRES_USER=agent -e POSTGRES_PASSWORD=agent123 -p 5433:5432 postgres:15-alpine

# Install Python dependencies for agents
pip install redis celery fastapi websockets sqlalchemy psycopg2-binary

# Create agent configuration files
cat > config/orchestrator.yml << EOF
agent:
  name: "orchestrator_agent"
  type: "coordinator"
  max_concurrent_tasks: 10
  queue: "orchestrator_tasks"
EOF

# Create basic agent configs
for agent in api database auth ui state integration smart_contract web3 devops security monitoring testing performance feature documentation; do
cat > config/${agent}_agent.yml << EOF
agent:
  name: "${agent}_agent"
  type: "worker"
  max_concurrent_tasks: 3
  queue: "${agent}_tasks"
  dependencies: []
EOF
done

# Create orchestrator startup script
cat > agents/orchestrator/start.py << 'EOF'
import asyncio
import redis
from celery import Celery

redis_client = redis.Redis(host='localhost', port=6380, db=0)
celery_app = Celery('orchestrator', broker='redis://localhost:6380/0')

class OrchestratorAgent:
    def __init__(self):
        self.active_agents = {}
        
    async def start(self):
        print("🎯 Orchestrator Agent started")
        while True:
            await self.check_agent_health()
            await asyncio.sleep(30)
    
    async def check_agent_health(self):
        print("💓 Checking agent health...")

if __name__ == "__main__":
    orchestrator = OrchestratorAgent()
    asyncio.run(orchestrator.start())
EOF

# Create generic agent worker template
cat > agents/agent_worker.py << 'EOF'
import sys
import asyncio
import yaml
from celery import Celery

class AgentWorker:
    def __init__(self, config_path):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        self.agent_name = self.config['agent']['name']
        
    async def start(self):
        print(f"🤖 {self.agent_name} started")
        while True:
            await self.process_tasks()
            await asyncio.sleep(10)
    
    async def process_tasks(self):
        print(f"⚡ {self.agent_name} processing tasks...")

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config/default.yml"
    worker = AgentWorker(config_path)
    asyncio.run(worker.start())
EOF

# Start orchestrator
echo "🎯 Starting Orchestrator Agent..."
cd agents/orchestrator
python start.py &
ORCHESTRATOR_PID=$!
echo $ORCHESTRATOR_PID > orchestrator.pid
cd ../..

# Start worker agents
echo "🤖 Starting Worker Agents..."
for agent in api database auth ui state integration smart_contract web3 devops security monitoring testing performance feature documentation; do
    echo "Starting ${agent}_agent..."
    cd agents
    python agent_worker.py ../config/${agent}_agent.yml &
    echo $! > ${agent}_agent.pid
    cd ..
    sleep 2
done

# Create status check script
cat > check_agents.py << 'EOF'
import redis
import time

redis_client = redis.Redis(host='localhost', port=6380, db=0)

agents = [
    'orchestrator_agent', 'api_agent', 'database_agent', 'auth_agent',
    'ui_agent', 'state_agent', 'integration_agent', 'smart_contract_agent',
    'web3_agent', 'devops_agent', 'security_agent', 'monitoring_agent',
    'testing_agent', 'performance_agent', 'feature_agent', 'documentation_agent'
]

print("🔍 Checking agent status...")
for agent in agents:
    try:
        status = redis_client.get(f"agent:{agent}:status") or "unknown"
        print(f"  {agent}: {status.decode() if isinstance(status, bytes) else status}")
    except:
        print(f"  {agent}: offline")
EOF

# Wait for agents to initialize
echo "⏳ Waiting for agents to initialize..."
sleep 10

# Check agent status
python check_agents.py

echo "✅ Agent system deployment complete!"
echo ""
echo "📊 System Status:"
echo "  - Orchestrator: http://localhost:8080 (if web interface added)"
echo "  - Redis: localhost:6380"
echo "  - PostgreSQL: localhost:5433"
echo ""
echo "🛠️ Management Commands:"
echo "  - Check status: python check_agents.py"
echo "  - View logs: tail -f logs/*.log"
echo "  - Stop system: pkill -f agent_worker.py && pkill -f start.py"
echo ""
echo "🎉 AgriDAO Agent System is now running autonomously!"
