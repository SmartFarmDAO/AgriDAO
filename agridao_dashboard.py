#!/usr/bin/env python3
import redis
import json
import time
from datetime import datetime
from collections import defaultdict

class AgriDAODashboard:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6380, db=0, decode_responses=True)
        
    def get_task_summary(self):
        """Get comprehensive task summary"""
        
        agents = [
            'api_agent', 'database_agent', 'auth_agent', 'ui_agent', 
            'security_agent', 'testing_agent', 'monitoring_agent', 'devops_agent',
            'smart_contract_agent', 'web3_agent', 'performance_agent', 'integration_agent',
            'documentation_agent', 'feature_agent', 'state_agent'
        ]
        
        summary = {
            'total_tasks': 0,
            'by_agent': {},
            'by_priority': defaultdict(int),
            'by_status': defaultdict(int),
            'critical_tasks': [],
            'recent_tasks': []
        }
        
        for agent in agents:
            queue_name = f"agent:{agent}:tasks"
            task_count = self.redis_client.llen(queue_name)
            
            if task_count > 0:
                summary['by_agent'][agent] = {
                    'total': task_count,
                    'tasks': []
                }
                
                # Get task details
                tasks = self.redis_client.lrange(queue_name, 0, -1)
                for task_json in tasks:
                    try:
                        task = json.loads(task_json)
                        summary['by_agent'][agent]['tasks'].append(task)
                        summary['total_tasks'] += 1
                        summary['by_priority'][task.get('priority', 'medium')] += 1
                        summary['by_status'][task.get('status', 'pending')] += 1
                        
                        if task.get('priority') == 'critical':
                            summary['critical_tasks'].append({
                                'agent': agent,
                                'task': task.get('task'),
                                'id': task.get('id')
                            })
                            
                        summary['recent_tasks'].append({
                            'agent': agent,
                            'task': task.get('task'),
                            'priority': task.get('priority'),
                            'timestamp': task.get('timestamp')
                        })
                    except json.JSONDecodeError:
                        continue
        
        # Sort recent tasks by timestamp
        summary['recent_tasks'].sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        summary['recent_tasks'] = summary['recent_tasks'][:10]  # Last 10 tasks
        
        return summary
    
    def display_dashboard(self):
        """Display comprehensive AgriDAO task dashboard"""
        
        print("🚀 AgriDAO Production Readiness Dashboard")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        summary = self.get_task_summary()
        
        # Overall Status
        print(f"\n📊 Overall Status")
        print(f"   Total Tasks: {summary['total_tasks']}")
        print(f"   🔴 Critical: {summary['by_priority']['critical']}")
        print(f"   🟡 High:     {summary['by_priority']['high']}")
        print(f"   🟢 Medium:   {summary['by_priority']['medium']}")
        
        # Agent Status
        print(f"\n🤖 Agent Task Distribution")
        print("-" * 40)
        
        for agent, data in summary['by_agent'].items():
            agent_name = agent.replace('_agent', '').title()
            task_count = data['total']
            
            # Get priority breakdown for this agent
            priorities = defaultdict(int)
            for task in data['tasks']:
                priorities[task.get('priority', 'medium')] += 1
            
            priority_str = f"C:{priorities['critical']} H:{priorities['high']} M:{priorities['medium']}"
            print(f"   {agent_name:15} | {task_count:2} tasks | {priority_str}")
        
        # Critical Tasks Focus
        if summary['critical_tasks']:
            print(f"\n🔴 Critical Tasks (Immediate Action Required)")
            print("-" * 50)
            for task in summary['critical_tasks']:
                print(f"   • {task['agent']}: {task['task']}")
        
        # Recent Task Activity
        print(f"\n📋 Recent Task Queue Activity")
        print("-" * 40)
        for task in summary['recent_tasks'][:5]:
            priority_emoji = {"critical": "🔴", "high": "🟡", "medium": "🟢"}.get(task['priority'], "⚪")
            agent_name = task['agent'].replace('_agent', '')
            print(f"   {priority_emoji} {agent_name}: {task['task']}")
        
        # Production Readiness Checklist
        print(f"\n✅ Production Readiness Checklist")
        print("-" * 40)
        
        checklist = {
            "🔒 Security Hardening": ["security_agent", "auth_agent"],
            "📊 Monitoring & Observability": ["monitoring_agent"],
            "💾 Database & Backups": ["database_agent"],
            "🧪 Testing & Quality": ["testing_agent"],
            "🚀 DevOps & Deployment": ["devops_agent"],
            "🌐 API & Performance": ["api_agent", "performance_agent"],
            "💻 Frontend & UX": ["ui_agent", "state_agent"],
            "⛓️  Blockchain Integration": ["smart_contract_agent", "web3_agent"],
            "🔗 Third-party Integrations": ["integration_agent"],
            "📚 Documentation": ["documentation_agent"],
            "✨ Feature Enhancements": ["feature_agent"]
        }
        
        for category, agents in checklist.items():
            total_tasks = sum(summary['by_agent'].get(agent, {}).get('total', 0) for agent in agents)
            status = "🟢 Ready" if total_tasks == 0 else f"🟡 {total_tasks} tasks pending"
            print(f"   {category:25} | {status}")
        
        # Next Actions
        print(f"\n🎯 Recommended Next Actions")
        print("-" * 30)
        
        if summary['by_priority']['critical'] > 0:
            print(f"   1. 🔴 Address {summary['by_priority']['critical']} critical security/infrastructure tasks")
        if summary['by_priority']['high'] > 0:
            print(f"   2. 🟡 Complete {summary['by_priority']['high']} high-priority tasks")
        if summary['by_priority']['medium'] > 0:
            print(f"   3. 🟢 Work on {summary['by_priority']['medium']} medium-priority enhancements")
        
        print(f"\n📈 Progress Tracking")
        print(f"   Current: 55% → Target: 95% production ready")
        print(f"   Estimated: 6-8 weeks to production launch")
        
        return summary
    
    def monitor_continuous(self, interval=30):
        """Continuously monitor agent progress"""
        
        print("🔄 Starting continuous monitoring (Ctrl+C to stop)")
        
        try:
            while True:
                self.display_dashboard()
                print(f"\n⏳ Next update in {interval} seconds...")
                print("=" * 60)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped")

if __name__ == "__main__":
    dashboard = AgriDAODashboard()
    
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        dashboard.monitor_continuous()
    else:
        dashboard.display_dashboard()
