"""
Dispute resolution service for handling order disputes and customer support.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from sqlmodel import Session, select, and_, or_, func
from fastapi import HTTPException

from ..models import (
    Dispute, DisputeMessage, DisputeStatus, DisputeType,
    Order, User, OrderItem, Product
)
from ..database import engine
from .notification_service import NotificationService


class DisputeService:
    """Service for managing disputes and customer support."""
    
    def __init__(self):
        self.notification_service = NotificationService()
    
    def create_dispute(
        self,
        order_id: int,
        filed_by: int,
        dispute_type: DisputeType,
        subject: str,
        description: str,
        evidence_urls: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a new dispute for an order."""
        
        with Session(engine) as session:
            # Verify order exists and user has access
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Check if user is buyer or has items in the order (farmer)
            user_can_dispute = (
                order.buyer_id == filed_by or
                session.exec(
                    select(OrderItem).where(
                        and_(
                            OrderItem.order_id == order_id,
                            OrderItem.farmer_id == filed_by
                        )
                    )
                ).first() is not None
            )
            
            if not user_can_dispute:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Check if dispute already exists for this order
            existing_dispute = session.exec(
                select(Dispute).where(
                    and_(
                        Dispute.order_id == order_id,
                        Dispute.status.in_([DisputeStatus.OPEN, DisputeStatus.IN_REVIEW])
                    )
                )
            ).first()
            
            if existing_dispute:
                raise HTTPException(
                    status_code=400,
                    detail="An active dispute already exists for this order"
                )
            
            # Create dispute
            dispute = Dispute(
                order_id=order_id,
                filed_by=filed_by,
                dispute_type=dispute_type,
                subject=subject,
                description=description,
                evidence_urls=evidence_urls or [],
                priority=self._calculate_dispute_priority(dispute_type, order)
            )
            
            session.add(dispute)
            session.commit()
            session.refresh(dispute)
            
            # Send notifications
            self._send_dispute_notifications(dispute, "created")
            
            return {
                "id": dispute.id,
                "order_id": order_id,
                "dispute_type": dispute_type,
                "status": dispute.status,
                "subject": subject,
                "priority": dispute.priority,
                "created_at": dispute.created_at.isoformat(),
                "message": "Dispute created successfully"
            }
    
    def add_dispute_message(
        self,
        dispute_id: int,
        sender_id: int,
        message: str,
        is_internal: bool = False,
        attachments: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a message to a dispute."""
        
        with Session(engine) as session:
            dispute = session.get(Dispute, dispute_id)
            if not dispute:
                raise HTTPException(status_code=404, detail="Dispute not found")
            
            # Check permissions
            if not self._user_can_access_dispute(dispute, sender_id, session):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Create message
            dispute_message = DisputeMessage(
                dispute_id=dispute_id,
                sender_id=sender_id,
                message=message,
                is_internal=is_internal,
                attachments=attachments or []
            )
            
            session.add(dispute_message)
            
            # Update dispute status if needed
            if dispute.status == DisputeStatus.OPEN:
                dispute.status = DisputeStatus.IN_REVIEW
                dispute.updated_at = datetime.utcnow()
                session.add(dispute)
            
            session.commit()
            session.refresh(dispute_message)
            
            # Send notifications (except for internal messages)
            if not is_internal:
                self._send_dispute_notifications(dispute, "message_added")
            
            return {
                "id": dispute_message.id,
                "dispute_id": dispute_id,
                "message": "Message added successfully",
                "created_at": dispute_message.created_at.isoformat()
            }
    
    def update_dispute_status(
        self,
        dispute_id: int,
        new_status: DisputeStatus,
        admin_id: int,
        resolution: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update dispute status (admin only)."""
        
        with Session(engine) as session:
            # Verify admin permissions
            admin = session.get(User, admin_id)
            if not admin or admin.role.value != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            dispute = session.get(Dispute, dispute_id)
            if not dispute:
                raise HTTPException(status_code=404, detail="Dispute not found")
            
            old_status = dispute.status
            dispute.status = new_status
            dispute.updated_at = datetime.utcnow()
            
            if new_status == DisputeStatus.RESOLVED and resolution:
                dispute.resolution = resolution
                dispute.resolved_by = admin_id
                dispute.resolved_at = datetime.utcnow()
            elif new_status == DisputeStatus.ESCALATED:
                dispute.escalated_at = datetime.utcnow()
                dispute.priority = min(dispute.priority + 1, 5)  # Increase priority
            
            session.add(dispute)
            session.commit()
            
            # Send notifications
            self._send_dispute_notifications(dispute, "status_updated")
            
            return {
                "id": dispute.id,
                "old_status": old_status,
                "new_status": new_status,
                "resolution": resolution,
                "updated_at": dispute.updated_at.isoformat(),
                "message": f"Dispute status updated to {new_status.value}"
            }
    
    def get_dispute_details(
        self,
        dispute_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Get detailed dispute information."""
        
        with Session(engine) as session:
            dispute = session.get(Dispute, dispute_id)
            if not dispute:
                raise HTTPException(status_code=404, detail="Dispute not found")
            
            # Check permissions
            if not self._user_can_access_dispute(dispute, user_id, session):
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Get order details
            order = session.get(Order, dispute.order_id)
            
            # Get dispute messages (exclude internal if not admin)
            user = session.get(User, user_id)
            is_admin = user and user.role.value == "admin"
            
            messages_query = select(DisputeMessage, User).join(
                User, DisputeMessage.sender_id == User.id
            ).where(DisputeMessage.dispute_id == dispute_id)
            
            if not is_admin:
                messages_query = messages_query.where(DisputeMessage.is_internal == False)
            
            messages_query = messages_query.order_by(DisputeMessage.created_at.asc())
            messages_result = session.exec(messages_query).all()
            
            # Get filed by user info
            filed_by_user = session.get(User, dispute.filed_by)
            resolved_by_user = None
            if dispute.resolved_by:
                resolved_by_user = session.get(User, dispute.resolved_by)
            
            return {
                "id": dispute.id,
                "order_id": dispute.order_id,
                "dispute_type": dispute.dispute_type,
                "status": dispute.status,
                "subject": dispute.subject,
                "description": dispute.description,
                "evidence_urls": dispute.evidence_urls,
                "resolution": dispute.resolution,
                "priority": dispute.priority,
                "filed_by": {
                    "id": filed_by_user.id,
                    "name": filed_by_user.name,
                    "role": filed_by_user.role
                } if filed_by_user else None,
                "resolved_by": {
                    "id": resolved_by_user.id,
                    "name": resolved_by_user.name
                } if resolved_by_user else None,
                "order_info": {
                    "id": order.id,
                    "total": float(order.total),
                    "status": order.status,
                    "created_at": order.created_at.isoformat()
                } if order else None,
                "messages": [
                    {
                        "id": message.id,
                        "sender_name": user.name,
                        "sender_role": user.role,
                        "message": message.message,
                        "is_internal": message.is_internal,
                        "attachments": message.attachments,
                        "created_at": message.created_at.isoformat()
                    }
                    for message, user in messages_result
                ],
                "created_at": dispute.created_at.isoformat(),
                "updated_at": dispute.updated_at.isoformat(),
                "resolved_at": dispute.resolved_at.isoformat() if dispute.resolved_at else None,
                "escalated_at": dispute.escalated_at.isoformat() if dispute.escalated_at else None
            }
    
    def get_user_disputes(
        self,
        user_id: int,
        status_filter: Optional[List[DisputeStatus]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get disputes for a user."""
        
        with Session(engine) as session:
            # Get disputes where user is involved (filed by them or has items in the order)
            query = select(Dispute).where(
                or_(
                    Dispute.filed_by == user_id,
                    Dispute.order_id.in_(
                        select(OrderItem.order_id).where(OrderItem.farmer_id == user_id)
                    ),
                    Dispute.order_id.in_(
                        select(Order.id).where(Order.buyer_id == user_id)
                    )
                )
            )
            
            if status_filter:
                query = query.where(Dispute.status.in_(status_filter))
            
            # Get total count
            total_count = session.exec(
                select(func.count()).select_from(query.subquery())
            ).one()
            
            # Apply pagination and ordering
            query = query.order_by(Dispute.created_at.desc()).offset(offset).limit(limit)
            disputes = session.exec(query).all()
            
            # Format results
            results = []
            for dispute in disputes:
                order = session.get(Order, dispute.order_id)
                filed_by_user = session.get(User, dispute.filed_by)
                
                results.append({
                    "id": dispute.id,
                    "order_id": dispute.order_id,
                    "dispute_type": dispute.dispute_type,
                    "status": dispute.status,
                    "subject": dispute.subject,
                    "priority": dispute.priority,
                    "filed_by_name": filed_by_user.name if filed_by_user else None,
                    "order_total": float(order.total) if order else 0,
                    "created_at": dispute.created_at.isoformat(),
                    "updated_at": dispute.updated_at.isoformat()
                })
            
            return {
                "disputes": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(results) < total_count
            }
    
    def get_admin_disputes(
        self,
        admin_id: int,
        status_filter: Optional[List[DisputeStatus]] = None,
        priority_filter: Optional[List[int]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get all disputes for admin review."""
        
        with Session(engine) as session:
            # Verify admin permissions
            admin = session.get(User, admin_id)
            if not admin or admin.role.value != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")
            
            query = select(Dispute)
            
            if status_filter:
                query = query.where(Dispute.status.in_(status_filter))
            
            if priority_filter:
                query = query.where(Dispute.priority.in_(priority_filter))
            
            # Get total count
            total_count = session.exec(
                select(func.count()).select_from(query.subquery())
            ).one()
            
            # Apply pagination and ordering (high priority first, then by creation date)
            query = query.order_by(
                Dispute.priority.desc(),
                Dispute.created_at.desc()
            ).offset(offset).limit(limit)
            
            disputes = session.exec(query).all()
            
            # Format results with additional admin info
            results = []
            for dispute in disputes:
                order = session.get(Order, dispute.order_id)
                filed_by_user = session.get(User, dispute.filed_by)
                
                # Get message count
                message_count = session.exec(
                    select(func.count()).select_from(
                        select(DisputeMessage).where(DisputeMessage.dispute_id == dispute.id).subquery()
                    )
                ).one()
                
                results.append({
                    "id": dispute.id,
                    "order_id": dispute.order_id,
                    "dispute_type": dispute.dispute_type,
                    "status": dispute.status,
                    "subject": dispute.subject,
                    "priority": dispute.priority,
                    "filed_by": {
                        "id": filed_by_user.id,
                        "name": filed_by_user.name,
                        "role": filed_by_user.role
                    } if filed_by_user else None,
                    "order_total": float(order.total) if order else 0,
                    "message_count": message_count,
                    "days_open": (datetime.utcnow() - dispute.created_at).days,
                    "created_at": dispute.created_at.isoformat(),
                    "updated_at": dispute.updated_at.isoformat()
                })
            
            return {
                "disputes": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(results) < total_count
            }
    
    def auto_escalate_disputes(self) -> Dict[str, Any]:
        """Automatically escalate disputes based on rules (called by scheduler)."""
        
        with Session(engine) as session:
            # Escalate disputes that are open for more than 3 days
            escalation_date = datetime.utcnow() - timedelta(days=3)
            
            disputes_to_escalate = session.exec(
                select(Dispute).where(
                    and_(
                        Dispute.status == DisputeStatus.OPEN,
                        Dispute.created_at <= escalation_date,
                        Dispute.escalated_at.is_(None)
                    )
                )
            ).all()
            
            escalated_count = 0
            for dispute in disputes_to_escalate:
                dispute.status = DisputeStatus.ESCALATED
                dispute.escalated_at = datetime.utcnow()
                dispute.priority = min(dispute.priority + 1, 5)
                dispute.updated_at = datetime.utcnow()
                session.add(dispute)
                escalated_count += 1
                
                # Send escalation notifications
                self._send_dispute_notifications(dispute, "escalated")
            
            session.commit()
            
            return {
                "escalated_count": escalated_count,
                "message": f"Escalated {escalated_count} disputes"
            }
    
    def _calculate_dispute_priority(self, dispute_type: DisputeType, order: Order) -> int:
        """Calculate dispute priority based on type and order value."""
        
        base_priority = {
            DisputeType.ORDER_NOT_RECEIVED: 4,
            DisputeType.DAMAGED_ITEM: 3,
            DisputeType.WRONG_ITEM: 3,
            DisputeType.ITEM_NOT_AS_DESCRIBED: 2,
            DisputeType.QUALITY_ISSUE: 2,
            DisputeType.REFUND_REQUEST: 1,
            DisputeType.OTHER: 1
        }.get(dispute_type, 1)
        
        # Increase priority for high-value orders
        if order.total > 100:
            base_priority = min(base_priority + 1, 5)
        
        return base_priority
    
    def _user_can_access_dispute(self, dispute: Dispute, user_id: int, session: Session) -> bool:
        """Check if user can access dispute."""
        
        # User filed the dispute
        if dispute.filed_by == user_id:
            return True
        
        # User is admin
        user = session.get(User, user_id)
        if user and user.role.value == "admin":
            return True
        
        # User is buyer of the order
        order = session.get(Order, dispute.order_id)
        if order and order.buyer_id == user_id:
            return True
        
        # User is farmer with items in the order
        farmer_items = session.exec(
            select(OrderItem).where(
                and_(
                    OrderItem.order_id == dispute.order_id,
                    OrderItem.farmer_id == user_id
                )
            )
        ).first()
        
        return farmer_items is not None
    
    def _send_dispute_notifications(self, dispute: Dispute, event_type: str) -> None:
        """Send notifications for dispute events."""
        
        # This would integrate with the notification service
        # For now, just a placeholder
        pass