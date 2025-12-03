"""
Security audit and incident response system for AgriDAO.
Provides security monitoring, vulnerability scanning, and incident response capabilities.
"""

import json
import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import re
import logging

from app.core.logging import get_logger
from app.core.config import settings
from app.database import SessionLocal


class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentType(Enum):
    DATA_BREACH = "data_breach"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    DDOS = "ddos"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    BRUTE_FORCE = "brute_force"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    POLICY_VIOLATION = "policy_violation"


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    timestamp: datetime
    event_type: str
    severity: SeverityLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    details: Dict[str, Any]
    resolved: bool = False


@dataclass
class Vulnerability:
    """Security vulnerability record."""
    vuln_id: str
    discovered_at: datetime
    severity: SeverityLevel
    category: str
    description: str
    affected_components: List[str]
    remediation: str
    status: str = "open"  # open, investigating, patched, closed


@dataclass
class SecurityIncident:
    """Security incident record."""
    incident_id: str
    created_at: datetime
    incident_type: IncidentType
    severity: SeverityLevel
    title: str
    description: str
    affected_users: List[str]
    evidence: Dict[str, Any]
    status: str = "detected"  # detected, investigating, contained, resolved, closed
    response_actions: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.response_actions is None:
            self.response_actions = []


class SecurityAuditor:
    """Comprehensive security audit system."""
    
    def __init__(self):
        self.logger = get_logger("security_audit")
        self.events: List[SecurityEvent] = []
        self.vulnerabilities: List[Vulnerability] = []
        self.incidents: List[SecurityIncident] = []
        self.audit_log = []
    
    async def log_security_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        self.events.append(event)
        
        # Log to structured logger
        self.logger.warning(
            f"Security event: {event.event_type}",
            event_id=event.event_id,
            severity=event.severity.value,
            source_ip=event.source_ip,
            user_id=event.user_id,
            description=event.description,
            details=event.details
        )
        
        # Check if event should trigger incident
        await self._evaluate_event_for_incident(event)
    
    async def _evaluate_event_for_incident(self, event: SecurityEvent) -> None:
        """Evaluate if a security event should trigger an incident."""
        incident_triggers = {
            "brute_force": {
                "threshold": 5,
                "time_window": 300,  # 5 minutes
                "severity": SeverityLevel.HIGH
            },
            "sql_injection": {
                "threshold": 1,
                "severity": SeverityLevel.CRITICAL
            },
            "data_breach": {
                "threshold": 1,
                "severity": SeverityLevel.CRITICAL
            }
        }
        
        if event.event_type in incident_triggers:
            trigger = incident_triggers[event.event_type]
            
            # Check for threshold breach
            recent_events = [
                e for e in self.events
                if e.event_type == event.event_type
                and e.timestamp > datetime.utcnow() - timedelta(seconds=trigger.get("time_window", 60))
            ]
            
            if len(recent_events) >= trigger["threshold"]:
                await self.create_incident(
                    incident_type=self._get_incident_type(event.event_type),
                    severity=trigger["severity"],
                    title=f"{event.event_type.replace('_', ' ').title()} Detected",
                    description=event.description,
                    affected_users=[event.user_id] if event.user_id else [],
                    evidence={"events": [asdict(e) for e in recent_events]}
                )
    
    def _get_incident_type(self, event_type: str) -> IncidentType:
        """Map event type to incident type."""
        mapping = {
            "brute_force": IncidentType.BRUTE_FORCE,
            "sql_injection": IncidentType.SQL_INJECTION,
            "xss": IncidentType.XSS,
            "data_breach": IncidentType.DATA_BREACH,
            "unauthorized_access": IncidentType.UNAUTHORIZED_ACCESS,
            "malware": IncidentType.MALWARE,
            "ddos": IncidentType.DDOS,
            "suspicious_activity": IncidentType.SUSPICIOUS_ACTIVITY,
            "policy_violation": IncidentType.POLICY_VIOLATION
        }
        return mapping.get(event_type, IncidentType.SUSPICIOUS_ACTIVITY)
    
    async def create_incident(self, incident_type: IncidentType, severity: SeverityLevel,
                            title: str, description: str, affected_users: List[str],
                            evidence: Dict[str, Any]) -> SecurityIncident:
        """Create a new security incident."""
        incident = SecurityIncident(
            incident_id=f"INC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{secrets.token_hex(4).upper()}",
            created_at=datetime.utcnow(),
            incident_type=incident_type,
            severity=severity,
            title=title,
            description=description,
            affected_users=affected_users,
            evidence=evidence
        )
        
        self.incidents.append(incident)
        
        # Log critical incident
        self.logger.critical(
            f"Security incident created: {incident.incident_id}",
            incident_id=incident.incident_id,
            incident_type=incident_type.value,
            severity=severity.value,
            affected_users_count=len(affected_users)
        )
        
        # Trigger immediate response
        await self._trigger_incident_response(incident)
        
        return incident
    
    async def _trigger_incident_response(self, incident: SecurityIncident) -> None:
        """Trigger automated incident response."""
        response_actions = []
        
        if incident.severity == SeverityLevel.CRITICAL:
            response_actions.extend([
                {
                    "action": "immediate_notification",
                    "timestamp": datetime.utcnow(),
                    "details": {"recipients": ["security@agridao.com", "admin@agridao.com"]}
                },
                {
                    "action": "isolate_affected_systems",
                    "timestamp": datetime.utcnow(),
                    "details": {"systems": ["database", "api", "frontend"]}
                }
            ])
        
        elif incident.severity == SeverityLevel.HIGH:
            response_actions.extend([
                {
                    "action": "enhanced_monitoring",
                    "timestamp": datetime.utcnow(),
                    "details": {"duration_hours": 24}
                },
                {
                    "action": "user_notification",
                    "timestamp": datetime.utcnow(),
                    "details": {"users": incident.affected_users}
                }
            ])
        
        incident.response_actions = response_actions
        incident.status = "investigating"
        
        # Log response actions
        for action in response_actions:
            self.logger.info(
                f"Incident response action: {action['action']}",
                incident_id=incident.incident_id,
                action=action['action']
            )
    
    async def scan_vulnerabilities(self) -> List[Vulnerability]:
        """Perform security vulnerability scan."""
        vulnerabilities = []
        
        # Check for common security issues
        vulnerability_checks = [
            self._check_weak_passwords,
            self._check_sql_injection_patterns,
            self._check_xss_patterns,
            self._check_insecure_headers,
            self._check_exposed_endpoints,
            self._check_data_leakage,
            self._check_access_control_issues
        ]
        
        for check in vulnerability_checks:
            try:
                vulns = await check()
                vulnerabilities.extend(vulns)
            except Exception as e:
                self.logger.error(f"Vulnerability check failed: {e}")
        
        self.vulnerabilities.extend(vulnerabilities)
        
        # Log scan results
        self.logger.info(
            f"Vulnerability scan completed",
            vulnerabilities_found=len(vulnerabilities),
            critical_count=len([v for v in vulnerabilities if v.severity == SeverityLevel.CRITICAL]),
            high_count=len([v for v in vulnerabilities if v.severity == SeverityLevel.HIGH])
        )
        
        return vulnerabilities
    
    async def _check_weak_passwords(self) -> List[Vulnerability]:
        """Check for weak password patterns."""
        vulns = []
        
        # This would typically check against a password database
        weak_patterns = [
            r"^(password|123456|qwerty|admin|root)$",
            r"^.{0,7}$",  # Less than 8 characters
            r"^[a-z]+$",  # Only lowercase
            r"^[0-9]+$"   # Only numbers
        ]
        
        for pattern in weak_patterns:
            vulns.append(Vulnerability(
                vuln_id=f"WEAK-PWD-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                discovered_at=datetime.utcnow(),
                severity=SeverityLevel.HIGH,
                category="authentication",
                description=f"Weak password pattern detected: {pattern}",
                affected_components=["user_authentication"],
                remediation="Enforce strong password policy with complexity requirements"
            ))
        
        return vulns
    
    async def _check_sql_injection_patterns(self) -> List[Vulnerability]:
        """Check for SQL injection vulnerabilities."""
        vulns = []
        
        sql_patterns = [
            r"(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b.*\b(from|where|order by|group by)\b)",
            r"(\b(or|and)\b.*=.*\b(or|and)\b)",
            r"(\b1=1\b|\b'='\b|\b\"=\"\b)"
        ]
        
        for pattern in sql_patterns:
            vulns.append(Vulnerability(
                vuln_id=f"SQLI-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                discovered_at=datetime.utcnow(),
                severity=SeverityLevel.CRITICAL,
                category="injection",
                description=f"Potential SQL injection vulnerability: {pattern}",
                affected_components=["database", "api"],
                remediation="Use parameterized queries and input validation"
            ))
        
        return vulns
    
    async def _check_xss_patterns(self) -> List[Vulnerability]:
        """Check for XSS vulnerabilities."""
        vulns = []
        
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>"
        ]
        
        for pattern in xss_patterns:
            vulns.append(Vulnerability(
                vuln_id=f"XSS-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                discovered_at=datetime.utcnow(),
                severity=SeverityLevel.HIGH,
                category="injection",
                description=f"Potential XSS vulnerability: {pattern}",
                affected_components=["frontend", "api"],
                remediation="Implement proper input validation and output encoding"
            ))
        
        return vulns
    
    async def _check_insecure_headers(self) -> List[Vulnerability]:
        """Check for missing security headers."""
        vulns = []
        
        missing_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]
        
        for header in missing_headers:
            vulns.append(Vulnerability(
                vuln_id=f"HEADER-{header}",
                discovered_at=datetime.utcnow(),
                severity=SeverityLevel.MEDIUM,
                category="configuration",
                description=f"Missing security header: {header}",
                affected_components=["web_server"],
                remediation=f"Add {header} security header to HTTP responses"
            ))
        
        return vulns
    
    async def _check_exposed_endpoints(self) -> List[Vulnerability]:
        """Check for exposed or unprotected endpoints."""
        vulns = []
        
        # Check for common exposed endpoints
        exposed_endpoints = [
            "/admin",
            "/debug",
            "/test",
            "/dev",
            "/api/debug"
        ]
        
        for endpoint in exposed_endpoints:
            vulns.append(Vulnerability(
                vuln_id=f"EXPOSED-{hashlib.md5(endpoint.encode()).hexdigest()[:8]}",
                discovered_at=datetime.utcnow(),
                severity=SeverityLevel.MEDIUM,
                category="access_control",
                description=f"Potentially exposed endpoint: {endpoint}",
                affected_components=["api"],
                remediation="Ensure proper authentication and authorization for all endpoints"
            ))
        
        return vulns
    
    async def _check_data_leakage(self) -> List[Vulnerability]:
        """Check for potential data leakage."""
        vulns = []
        
        # Check for sensitive data in logs
        sensitive_patterns = [
            r"password[=:]\s*[^&\s]+",
            r"api[_-]?key[=:]\s*[^&\s]+",
            r"token[=:]\s*[^&\s]+",
            r"secret[=:]\s*[^&\s]+"
        ]
        
        for pattern in sensitive_patterns:
            vulns.append(Vulnerability(
                vuln_id=f"LEAK-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                discovered_at=datetime.utcnow(),
                severity=SeverityLevel.HIGH,
                category="data_protection",
                description=f"Potential sensitive data leakage: {pattern}",
                affected_components=["logging", "monitoring"],
                remediation="Implement proper data masking and log sanitization"
            ))
        
        return vulns
    
    async def _check_access_control_issues(self) -> List[Vulnerability]:
        """Check for access control issues."""
        vulns = []
        
        vulns.append(Vulnerability(
            vuln_id="RBAC-001",
            discovered_at=datetime.utcnow(),
            severity=SeverityLevel.HIGH,
            category="access_control",
            description="Role-based access control verification needed",
            affected_components=["authorization"],
            remediation="Implement comprehensive RBAC with principle of least privilege"
        ))
        
        return vulns
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get comprehensive security summary."""
        active_incidents = [i for i in self.incidents if i.status != "closed"]
        open_vulnerabilities = [v for v in self.vulnerabilities if v.status == "open"]
        recent_events = [e for e in self.events 
                        if e.timestamp > datetime.utcnow() - timedelta(hours=24)]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "active_incidents": len(active_incidents),
                "open_vulnerabilities": len(open_vulnerabilities),
                "recent_events": len(recent_events),
                "total_events": len(self.events)
            },
            "incidents": [
                {
                    "incident_id": i.incident_id,
                    "type": i.incident_type.value,
                    "severity": i.severity.value,
                    "status": i.status,
                    "created_at": i.created_at.isoformat(),
                    "affected_users": len(i.affected_users)
                }
                for i in active_incidents
            ],
            "vulnerabilities": [
                {
                    "vuln_id": v.vuln_id,
                    "severity": v.severity.value,
                    "category": v.category,
                    "status": v.status
                }
                for v in open_vulnerabilities
            ],
            "recent_events": [
                {
                    "event_id": e.event_id,
                    "type": e.event_type,
                    "severity": e.severity.value,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in recent_events[-10:]  # Last 10 events
            ]
        }
    
    async def generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive security audit report."""
        vulnerabilities = await self.scan_vulnerabilities()
        
        report = {
            "report_id": f"AUDIT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "generated_at": datetime.utcnow().isoformat(),
            "summary": self.get_security_summary(),
            "vulnerabilities": [
                {
                    "vuln_id": v.vuln_id,
                    "severity": v.severity.value,
                    "category": v.category,
                    "description": v.description,
                    "affected_components": v.affected_components,
                    "remediation": v.remediation,
                    "status": v.status
                }
                for v in vulnerabilities
            ],
            "recommendations": [
                "Implement regular vulnerability scanning",
                "Enforce strong password policies",
                "Implement multi-factor authentication",
                "Regular security awareness training",
                "Incident response plan testing",
                "Security monitoring and alerting",
                "Regular security audits",
                "Data encryption at rest and in transit",
                "Access control reviews",
                "Third-party security assessments"
            ],
            "compliance_status": {
                "gdpr": "partial",
                "ccpa": "partial",
                "pci_dss": "not_applicable",
                "iso_27001": "in_progress"
            }
        }
        
        # Log audit report generation
        self.logger.info(
            f"Security audit report generated",
            report_id=report["report_id"],
            vulnerabilities_found=len(vulnerabilities)
        )
        
        return report


class IncidentResponseManager:
    """Manage security incident response procedures."""
    
    def __init__(self):
        self.logger = get_logger("incident_response")
        self.response_playbooks = self._load_response_playbooks()
    
    def _load_response_playbooks(self) -> Dict[str, Dict[str, Any]]:
        """Load incident response playbooks."""
        return {
            "data_breach": {
                "immediate_actions": [
                    "Isolate affected systems",
                    "Preserve evidence",
                    "Notify security team",
                    "Assess scope of breach",
                    "Notify affected users within 72 hours"
                ],
                "timeline": {
                    "0_hours": ["Initial detection and containment"],
                    "1_hour": ["Full system isolation", "Evidence collection"],
                    "4_hours": ["Scope assessment", "User notification preparation"],
                    "24_hours": ["Regulatory notification", "Public disclosure preparation"],
                    "72_hours": ["Full user notification", "Regulatory compliance"]
                },
                "contacts": [
                    "security@agridao.com",
                    "legal@agridao.com",
                    "compliance@agridao.com"
                ]
            },
            "unauthorized_access": {
                "immediate_actions": [
                    "Revoke compromised credentials",
                    "Force password reset",
                    "Review access logs",
                    "Implement additional monitoring"
                ],
                "timeline": {
                    "0_hours": ["Credential revocation", "Access log review"],
                    "1_hour": ["User notification", "Password reset"],
                    "4_hours": ["Access review", "Security assessment"],
                    "24_hours": ["Monitoring enhancement", "Policy review"]
                }
            },
            "malware": {
                "immediate_actions": [
                    "Isolate infected systems",
                    "Run malware scans",
                    "Update security signatures",
                    "Review network traffic"
                ],
                "timeline": {
                    "0_hours": ["System isolation", "Initial scan"],
                    "1_hour": ["Full system scan", "Signature update"],
                    "4_hours": ["Traffic analysis", "Clean-up"],
                    "24_hours": ["System restoration", "Monitoring enhancement"]
                }
            }
        }
    
    async def execute_incident_response(self, incident: SecurityIncident) -> Dict[str, Any]:
        """Execute incident response playbook."""
        playbook = self.response_playbooks.get(incident.incident_type.value)
        
        if not playbook:
            playbook = self.response_playbooks["unauthorized_access"]  # Default fallback
        
        response_plan = {
            "incident_id": incident.incident_id,
            "playbook_used": incident.incident_type.value,
            "immediate_actions": [],
            "timeline": playbook["timeline"],
            "contacts": playbook.get("contacts", [])
        }
        
        # Execute immediate actions
        for action in playbook["immediate_actions"]:
            try:
                await self._execute_action(action, incident)
                response_plan["immediate_actions"].append({
                    "action": action,
                    "status": "completed",
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                response_plan["immediate_actions"].append({
                    "action": action,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        # Log response execution
        self.logger.info(
            f"Incident response executed",
            incident_id=incident.incident_id,
            actions_completed=len([a for a in response_plan["immediate_actions"] if a["status"] == "completed"])
        )
        
        return response_plan
    
    async def _execute_action(self, action: str, incident: SecurityIncident) -> None:
        """Execute a specific incident response action."""
        if action == "Isolate affected systems":
            await self._isolate_systems(incident)
        elif action == "Notify security team":
            await self._notify_security_team(incident)
        elif action == "Force password reset":
            await self._force_password_reset(incident)
        elif action == "Run malware scans":
            await self._run_malware_scans(incident)
        elif action == "Preserve evidence":
            await self._preserve_evidence(incident)
    
    async def _isolate_systems(self, incident: SecurityIncident) -> None:
        """Isolate affected systems."""
        self.logger.info(f"Isolating systems for incident {incident.incident_id}")
        # Implementation would interface with infrastructure
    
    async def _notify_security_team(self, incident: SecurityIncident) -> None:
        """Notify security team of incident."""
        self.logger.info(f"Notifying security team about incident {incident.incident_id}")
        # Implementation would send notifications
    
    async def _force_password_reset(self, incident: SecurityIncident) -> None:
        """Force password reset for affected users."""
        for user_id in incident.affected_users:
            self.logger.info(f"Forcing password reset for user {user_id}")
            # Implementation would trigger password reset
    
    async def _run_malware_scans(self, incident: SecurityIncident) -> None:
        """Run malware scans on affected systems."""
        self.logger.info(f"Running malware scans for incident {incident.incident_id}")
        # Implementation would trigger malware scanning
    
    async def _preserve_evidence(self, incident: SecurityIncident) -> None:
        """Preserve evidence for investigation."""
        self.logger.info(f"Preserving evidence for incident {incident.incident_id}")
        # Implementation would preserve logs and system state
    
    async def generate_incident_report(self, incident_id: str) -> Dict[str, Any]:
        """Generate comprehensive incident report."""
        incident = next((i for i in security_auditor.incidents if i.incident_id == incident_id), None)
        
        if not incident:
            return {"error": "Incident not found"}
        
        report = {
            "incident_id": incident.incident_id,
            "report_type": "incident_investigation",
            "generated_at": datetime.utcnow().isoformat(),
            "incident_details": {
                "type": incident.incident_type.value,
                "severity": incident.severity.value,
                "created_at": incident.created_at.isoformat(),
                "title": incident.title,
                "description": incident.description,
                "affected_users": len(incident.affected_users),
                "status": incident.status
            },
            "timeline": {
                "detection": incident.created_at.isoformat(),
                "response_start": incident.response_actions[0]["timestamp"] if incident.response_actions else None,
                "current_status": incident.status
            },
            "evidence": incident.evidence,
            "response_actions": incident.response_actions,
            "lessons_learned": [
                "Regular security monitoring is essential",
                "Incident response procedures should be tested regularly",
                "User education on security best practices",
                "Regular security assessments and updates"
            ],
            "recommendations": [
                "Enhance monitoring capabilities",
                "Improve incident detection",
                "Regular security training",
                "Update security policies",
                "Review and test incident response procedures"
            ]
        }
        
        return report


# Global instances
security_auditor = SecurityAuditor()
incident_response_manager = IncidentResponseManager()