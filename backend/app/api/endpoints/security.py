"""
Security audit and incident response API endpoints.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, get_current_admin_user
from app.core.security_audit import security_auditor, incident_response_manager
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger("security_api")
router = APIRouter(prefix="/security", tags=["security"])


@router.get("/summary", response_model=dict)
async def get_security_summary(
    current_user: User = Depends(get_current_admin_user)
):
    """Get comprehensive security summary."""
    try:
        summary = security_auditor.get_security_summary()
        logger.info("Security summary retrieved", user_id=current_user.id)
        return summary
    except Exception as e:
        logger.error(f"Error retrieving security summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve security summary")


@router.post("/events", response_model=dict)
async def log_security_event(
    event_type: str = Query(..., description="Type of security event"),
    severity: str = Query(..., description="Severity level (low, medium, high, critical)"),
    source_ip: str = Query(..., description="Source IP address"),
    description: str = Query(..., description="Event description"),
    user_id: Optional[str] = Query(None, description="User ID if applicable"),
    details: Optional[dict] = Query(None, description="Additional event details"),
    current_user: User = Depends(get_current_admin_user)
):
    """Log a security event."""
    try:
        from app.core.security_audit import SecurityEvent
        
        event = SecurityEvent(
            event_id=f"EVT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{hash(source_ip) % 10000:04d}",
            timestamp=datetime.utcnow(),
            event_type=event_type,
            severity=severity,
            source_ip=source_ip,
            user_id=user_id,
            description=description,
            details=details or {}
        )
        
        await security_auditor.log_security_event(event)
        
        logger.info(
            "Security event logged",
            event_id=event.event_id,
            event_type=event_type,
            severity=severity,
            user_id=current_user.id
        )
        
        return {
            "event_id": event.event_id,
            "status": "logged",
            "message": "Security event successfully logged"
        }
    except Exception as e:
        logger.error(f"Error logging security event: {e}")
        raise HTTPException(status_code=500, detail="Failed to log security event")


@router.get("/events", response_model=dict)
async def get_security_events(
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of events to return"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security events with filtering."""
    try:
        events = security_auditor.events
        
        # Apply filters
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        if severity:
            events = [e for e in events if e.severity.value == severity]
        
        if start_date:
            events = [e for e in events if e.timestamp >= start_date]
        
        if end_date:
            events = [e for e in events if e.timestamp <= end_date]
        
        # Limit results
        events = events[-limit:]
        
        logger.info(
            "Security events retrieved",
            user_id=current_user.id,
            events_count=len(events)
        )
        
        return {
            "events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "event_type": e.event_type,
                    "severity": e.severity.value,
                    "source_ip": e.source_ip,
                    "user_id": e.user_id,
                    "description": e.description,
                    "details": e.details
                }
                for e in events
            ],
            "total": len(events)
        }
    except Exception as e:
        logger.error(f"Error retrieving security events: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve security events")


@router.get("/incidents", response_model=dict)
async def get_security_incidents(
    status: Optional[str] = Query(None, description="Filter by incident status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security incidents."""
    try:
        incidents = security_auditor.incidents
        
        # Apply filters
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        if severity:
            incidents = [i for i in incidents if i.severity.value == severity]
        
        logger.info(
            "Security incidents retrieved",
            user_id=current_user.id,
            incidents_count=len(incidents)
        )
        
        return {
            "incidents": [
                {
                    "incident_id": i.incident_id,
                    "created_at": i.created_at.isoformat(),
                    "incident_type": i.incident_type.value,
                    "severity": i.severity.value,
                    "title": i.title,
                    "description": i.description,
                    "affected_users": len(i.affected_users),
                    "status": i.status,
                    "response_actions": i.response_actions
                }
                for i in incidents
            ],
            "total": len(incidents)
        }
    except Exception as e:
        logger.error(f"Error retrieving security incidents: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve security incidents")


@router.post("/incidents", response_model=dict)
async def create_security_incident(
    incident_type: str = Query(..., description="Type of security incident"),
    severity: str = Query(..., description="Severity level (low, medium, high, critical)"),
    title: str = Query(..., description="Incident title"),
    description: str = Query(..., description="Incident description"),
    affected_users: List[str] = Query([], description="List of affected user IDs"),
    evidence: Optional[dict] = Query(None, description="Incident evidence"),
    current_user: User = Depends(get_current_admin_user)
):
    """Create a security incident."""
    try:
        from app.core.security_audit import IncidentType, SeverityLevel
        
        incident = await security_auditor.create_incident(
            incident_type=IncidentType(incident_type),
            severity=SeverityLevel(severity),
            title=title,
            description=description,
            affected_users=affected_users,
            evidence=evidence or {}
        )
        
        logger.info(
            "Security incident created",
            incident_id=incident.incident_id,
            incident_type=incident_type,
            severity=severity,
            user_id=current_user.id
        )
        
        return {
            "incident_id": incident.incident_id,
            "status": "created",
            "message": "Security incident successfully created"
        }
    except Exception as e:
        logger.error(f"Error creating security incident: {e}")
        raise HTTPException(status_code=500, detail="Failed to create security incident")


@router.get("/incidents/{incident_id}/report", response_model=dict)
async def get_incident_report(
    incident_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Get detailed incident report."""
    try:
        report = await incident_response_manager.generate_incident_report(incident_id)
        
        if "error" in report:
            raise HTTPException(status_code=404, detail=report["error"])
        
        logger.info(
            "Incident report retrieved",
            incident_id=incident_id,
            user_id=current_user.id
        )
        
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving incident report: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve incident report")


@router.post("/incidents/{incident_id}/respond", response_model=dict)
async def execute_incident_response(
    incident_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Execute incident response for a security incident."""
    try:
        incident = next((i for i in security_auditor.incidents if i.incident_id == incident_id), None)
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        response_plan = await incident_response_manager.execute_incident_response(incident)
        
        logger.info(
            "Incident response executed",
            incident_id=incident_id,
            user_id=current_user.id,
            actions_count=len(response_plan.get("immediate_actions", []))
        )
        
        return {
            "incident_id": incident_id,
            "response_plan": response_plan,
            "status": "response_executed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing incident response: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute incident response")


@router.get("/vulnerabilities", response_model=dict)
async def get_vulnerabilities(
    status: Optional[str] = Query(None, description="Filter by vulnerability status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    category: Optional[str] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_admin_user)
):
    """Get security vulnerabilities."""
    try:
        vulnerabilities = security_auditor.vulnerabilities
        
        # Apply filters
        if status:
            vulnerabilities = [v for v in vulnerabilities if v.status == status]
        
        if severity:
            vulnerabilities = [v for v in vulnerabilities if v.severity.value == severity]
        
        if category:
            vulnerabilities = [v for v in vulnerabilities if v.category == category]
        
        logger.info(
            "Vulnerabilities retrieved",
            user_id=current_user.id,
            vulnerabilities_count=len(vulnerabilities)
        )
        
        return {
            "vulnerabilities": [
                {
                    "vuln_id": v.vuln_id,
                    "discovered_at": v.discovered_at.isoformat(),
                    "severity": v.severity.value,
                    "category": v.category,
                    "description": v.description,
                    "affected_components": v.affected_components,
                    "remediation": v.remediation,
                    "status": v.status
                }
                for v in vulnerabilities
            ],
            "total": len(vulnerabilities)
        }
    except Exception as e:
        logger.error(f"Error retrieving vulnerabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve vulnerabilities")


@router.post("/vulnerabilities/scan", response_model=dict)
async def scan_vulnerabilities(
    current_user: User = Depends(get_current_admin_user)
):
    """Trigger vulnerability scan."""
    try:
        vulnerabilities = await security_auditor.scan_vulnerabilities()
        
        logger.info(
            "Vulnerability scan triggered",
            user_id=current_user.id,
            vulnerabilities_found=len(vulnerabilities)
        )
        
        return {
            "scan_id": f"SCAN-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": [
                {
                    "vuln_id": v.vuln_id,
                    "severity": v.severity.value,
                    "category": v.category,
                    "description": v.description
                }
                for v in vulnerabilities
            ],
            "status": "scan_completed"
        }
    except Exception as e:
        logger.error(f"Error scanning vulnerabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to scan vulnerabilities")


@router.get("/audit-report", response_model=dict)
async def generate_audit_report(
    current_user: User = Depends(get_current_admin_user)
):
    """Generate comprehensive security audit report."""
    try:
        report = await security_auditor.generate_audit_report()
        
        logger.info(
            "Security audit report generated",
            report_id=report["report_id"],
            user_id=current_user.id
        )
        
        return report
    except Exception as e:
        logger.error(f"Error generating audit report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audit report")


@router.put("/vulnerabilities/{vuln_id}/status", response_model=dict)
async def update_vulnerability_status(
    vuln_id: str,
    status: str = Query(..., description="New vulnerability status"),
    current_user: User = Depends(get_current_admin_user)
):
    """Update vulnerability status."""
    try:
        vulnerability = next((v for v in security_auditor.vulnerabilities if v.vuln_id == vuln_id), None)
        
        if not vulnerability:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
        
        vulnerability.status = status
        
        logger.info(
            "Vulnerability status updated",
            vuln_id=vuln_id,
            new_status=status,
            user_id=current_user.id
        )
        
        return {
            "vuln_id": vuln_id,
            "status": status,
            "message": "Vulnerability status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vulnerability status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update vulnerability status")


@router.put("/incidents/{incident_id}/status", response_model=dict)
async def update_incident_status(
    incident_id: str,
    status: str = Query(..., description="New incident status"),
    current_user: User = Depends(get_current_admin_user)
):
    """Update incident status."""
    try:
        incident = next((i for i in security_auditor.incidents if i.incident_id == incident_id), None)
        
        if not incident:
            raise HTTPException(status_code=404, detail="Incident not found")
        
        incident.status = status
        
        logger.info(
            "Incident status updated",
            incident_id=incident_id,
            new_status=status,
            user_id=current_user.id
        )
        
        return {
            "incident_id": incident_id,
            "status": status,
            "message": "Incident status updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating incident status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update incident status")