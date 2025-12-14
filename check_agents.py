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
