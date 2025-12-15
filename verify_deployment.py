#!/usr/bin/env python3
import redis
import json
import time
from datetime import datetime

def dispatch_verification_tasks():
    """Dispatch comprehensive verification tasks to agents"""
    
    redis_client = redis.Redis(host='localhost', port=6380, db=0)
    
    verification_tasks = [
        {
            "agent": "devops_agent",
            "task": "verify_infrastructure_health",
            "priority": "critical",
            "data": {
                "server_ip": "54.251.65.124",
                "check_services": ["docker", "nginx", "postgres", "redis"],
                "verify_ports": [80, 443, 5432, 6379],
                "check_disk_space": True,
                "check_memory": True
            }
        },
        {
            "agent": "api_agent", 
            "task": "verify_api_endpoints",
            "priority": "critical",
            "data": {
                "base_url": "http://54.251.65.124/api",
                "endpoints_to_test": [
                    "/health",
                    "/docs", 
                    "/auth/register",
                    "/products",
                    "/users/me"
                ],
                "check_response_times": True,
                "verify_cors": True
            }
        },
        {
            "agent": "database_agent",
            "task": "verify_database_integrity", 
            "priority": "critical",
            "data": {
                "check_connections": True,
                "verify_migrations": True,
                "test_crud_operations": True,
                "check_indexes": True,
                "verify_backup_system": True
            }
        },
        {
            "agent": "security_agent",
            "task": "verify_security_measures",
            "priority": "critical", 
            "data": {
                "check_ssl_status": True,
                "verify_security_headers": True,
                "test_authentication": True,
                "check_cors_policy": True,
                "scan_vulnerabilities": True
            }
        },
        {
            "agent": "frontend_agent",
            "task": "verify_frontend_functionality",
            "priority": "high",
            "data": {
                "base_url": "http://54.251.65.124",
                "check_pages": [
                    "/",
                    "/login", 
                    "/register",
                    "/marketplace",
                    "/dashboard"
                ],
                "verify_responsive_design": True,
                "check_api_integration": True
            }
        },
        {
            "agent": "monitoring_agent",
            "task": "verify_system_monitoring",
            "priority": "high",
            "data": {
                "check_container_health": True,
                "verify_log_collection": True,
                "test_alerting": False,
                "monitor_performance": True,
                "check_resource_usage": True
            }
        },
        {
            "agent": "testing_agent",
            "task": "run_integration_tests",
            "priority": "high",
            "data": {
                "test_user_registration": True,
                "test_product_listing": True,
                "test_marketplace_flow": True,
                "test_authentication_flow": True,
                "verify_data_persistence": True
            }
        },
        {
            "agent": "performance_agent",
            "task": "verify_performance_metrics",
            "priority": "medium",
            "data": {
                "measure_response_times": True,
                "check_database_performance": True,
                "verify_caching": True,
                "test_concurrent_users": 10,
                "check_memory_usage": True
            }
        }
    ]
    
    print("🔍 AgriDAO Deployment Verification")
    print("=" * 40)
    print(f"📊 Dispatching {len(verification_tasks)} verification tasks...")
    
    dispatched = 0
    for task in verification_tasks:
        task_data = {
            "id": f"verify_{int(time.time())}_{task['agent']}",
            "timestamp": datetime.now().isoformat(),
            "task": task["task"],
            "priority": task["priority"], 
            "data": task["data"],
            "status": "pending",
            "verification_type": "deployment_check",
            "server": "54.251.65.124"
        }
        
        queue_name = f"agent:{task['agent']}:tasks"
        redis_client.lpush(queue_name, json.dumps(task_data))
        
        priority_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟢"}.get(task['priority'], "⚪")
        print(f"   {priority_emoji} {task['agent']}: {task['task']}")
        dispatched += 1
    
    print(f"\n✅ Dispatched {dispatched} verification tasks")
    print(f"🎯 Target: Comprehensive deployment verification")
    print(f"🌐 Server: 54.251.65.124")
    print(f"📋 Use 'python agridao_dashboard.py' to monitor progress")
    
    return dispatched

if __name__ == "__main__":
    dispatch_verification_tasks()
