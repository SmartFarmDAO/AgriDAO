#!/usr/bin/env python3
import redis
import json
import time
from datetime import datetime

def dispatch_sample_tasks():
    redis_client = redis.Redis(host='localhost', port=6380, db=0)
    
    # Sample tasks for different agents
    tasks = [
        {
            "agent": "api_agent",
            "task": "health_check",
            "data": {"endpoint": "/api/health", "method": "GET"}
        },
        {
            "agent": "database_agent", 
            "task": "check_connections",
            "data": {"database": "agridao_db"}
        },
        {
            "agent": "ui_agent",
            "task": "validate_components",
            "data": {"components": ["LoginForm", "ProductCard"]}
        },
        {
            "agent": "security_agent",
            "task": "scan_vulnerabilities", 
            "data": {"scope": "authentication"}
        },
        {
            "agent": "monitoring_agent",
            "task": "collect_metrics",
            "data": {"metrics": ["cpu", "memory", "response_time"]}
        }
    ]
    
    print("🚀 Dispatching sample tasks to agents...")
    
    for task in tasks:
        task_data = {
            "id": f"task_{int(time.time())}_{task['agent']}",
            "timestamp": datetime.now().isoformat(),
            "task": task["task"],
            "data": task["data"],
            "status": "pending"
        }
        
        queue_name = f"agent:{task['agent']}:tasks"
        redis_client.lpush(queue_name, json.dumps(task_data))
        print(f"   ✅ Sent '{task['task']}' to {task['agent']}")
    
    print(f"\n📊 Dispatched {len(tasks)} tasks")
    print("Use 'python monitor_agents.py' to see agent activity")

if __name__ == "__main__":
    dispatch_sample_tasks()
