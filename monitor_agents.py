#!/usr/bin/env python3
import redis
import time
import json
from datetime import datetime

def monitor_agents():
    redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
    
    agents = [
        'orchestrator_agent', 'api_agent', 'database_agent', 'auth_agent',
        'ui_agent', 'state_agent', 'integration_agent', 'smart_contract_agent',
        'web3_agent', 'devops_agent', 'security_agent', 'monitoring_agent',
        'testing_agent', 'performance_agent', 'feature_agent', 'documentation_agent'
    ]
    
    print("🔍 AgriDAO Agent System Monitor")
    print("=" * 50)
    
    while True:
        print(f"\n📊 Status at {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 30)
        
        # Check agent processes
        running_agents = 0
        for agent in agents:
            try:
                # Check if agent has a heartbeat
                heartbeat = redis_client.get(f"agent:{agent}:heartbeat")
                status = redis_client.get(f"agent:{agent}:status") or "idle"
                
                if heartbeat:
                    last_seen = datetime.fromtimestamp(float(heartbeat))
                    time_diff = (datetime.now() - last_seen).seconds
                    if time_diff < 30:  # Active within 30 seconds
                        print(f"✅ {agent}: {status} (active)")
                        running_agents += 1
                    else:
                        print(f"⚠️  {agent}: {status} (stale - {time_diff}s ago)")
                else:
                    print(f"❌ {agent}: offline")
            except Exception as e:
                print(f"❌ {agent}: error - {e}")
        
        # Check task queues
        print(f"\n📋 Task Queues:")
        try:
            for agent in agents:
                queue_name = f"agent:{agent}:tasks"
                queue_length = redis_client.llen(queue_name)
                if queue_length > 0:
                    print(f"   {agent}: {queue_length} pending tasks")
        except Exception as e:
            print(f"   Error checking queues: {e}")
        
        # Check infrastructure
        print(f"\n🏗️  Infrastructure:")
        try:
            redis_info = redis_client.info()
            print(f"   Redis: Connected ({redis_info['connected_clients']} clients)")
        except:
            print("   Redis: Disconnected")
        
        print(f"\n📈 Summary: {running_agents}/{len(agents)} agents active")
        print("Press Ctrl+C to exit...")
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        monitor_agents()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped")
