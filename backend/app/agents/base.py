"""
Base Agent Class with Security Controls
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from enum import Enum

class AgentType(str, Enum):
    ADVISORY = "advisory"
    MARKET = "market"
    FINANCE = "finance"
    SUPPLY_CHAIN = "supply_chain"

class ActionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"
    DENIED = "denied"

class BaseAgent(ABC):
    """Base class for all autonomous agents with security controls"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        max_actions_per_minute: int = 10,
        requires_approval_threshold: Optional[Dict] = None
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.max_actions_per_minute = max_actions_per_minute
        self.requires_approval_threshold = requires_approval_threshold or {}
        self.logger = logging.getLogger(f"agent.{agent_type.value}")
        self.action_history: List[Dict] = []
        
    async def execute(
        self,
        action: str,
        params: Dict[str, Any],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute an action with full security checks
        
        Security layers:
        1. Permission check
        2. Rate limiting
        3. Parameter validation
        4. Approval workflow (if needed)
        5. Execution
        6. Audit logging
        """
        
        execution_id = self._generate_execution_id()
        
        try:
            # Layer 1: Check permissions
            if not self._has_permission(action):
                return self._error_response(
                    execution_id,
                    "permission_denied",
                    f"Agent {self.agent_id} lacks permission for action: {action}"
                )
            
            # Layer 2: Rate limiting
            if not await self._check_rate_limit():
                return self._error_response(
                    execution_id,
                    "rate_limit_exceeded",
                    f"Rate limit of {self.max_actions_per_minute}/min exceeded"
                )
            
            # Layer 3: Validate parameters
            validation_result = self._validate_params(action, params)
            if not validation_result["valid"]:
                return self._error_response(
                    execution_id,
                    "invalid_parameters",
                    validation_result["error"]
                )
            
            # Layer 4: Check if approval required
            if self._requires_approval(action, params):
                return await self._request_approval(
                    execution_id,
                    action,
                    params,
                    user_context
                )
            
            # Layer 5: Execute action
            result = await self._execute_action(action, params)
            
            # Layer 6: Audit log
            await self._audit_log(
                execution_id=execution_id,
                action=action,
                params=params,
                result=result,
                status=ActionStatus.SUCCESS,
                user_context=user_context
            )
            
            return {
                "execution_id": execution_id,
                "status": ActionStatus.SUCCESS,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Action failed: {action}", exc_info=True)
            
            await self._audit_log(
                execution_id=execution_id,
                action=action,
                params=params,
                error=str(e),
                status=ActionStatus.FAILED,
                user_context=user_context
            )
            
            return self._error_response(
                execution_id,
                "execution_failed",
                str(e)
            )
    
    @abstractmethod
    async def _execute_action(self, action: str, params: Dict) -> Any:
        """Implement in subclass - actual action execution"""
        pass
    
    @abstractmethod
    def _get_allowed_actions(self) -> List[str]:
        """Implement in subclass - list of allowed actions"""
        pass
    
    def _has_permission(self, action: str) -> bool:
        """Check if agent has permission for this action"""
        return action in self._get_allowed_actions()
    
    async def _check_rate_limit(self) -> bool:
        """Check if agent is within rate limits"""
        # Count actions in last minute
        one_minute_ago = datetime.utcnow().timestamp() - 60
        recent_actions = [
            a for a in self.action_history
            if a["timestamp"] > one_minute_ago
        ]
        
        if len(recent_actions) >= self.max_actions_per_minute:
            self.logger.warning(
                f"Rate limit exceeded: {len(recent_actions)}/{self.max_actions_per_minute}"
            )
            return False
        
        return True
    
    def _validate_params(self, action: str, params: Dict) -> Dict:
        """Validate action parameters"""
        # Basic validation - override in subclass for specific rules
        if not isinstance(params, dict):
            return {"valid": False, "error": "Parameters must be a dictionary"}
        
        return {"valid": True}
    
    def _requires_approval(self, action: str, params: Dict) -> bool:
        """Check if action requires human approval"""
        if action not in self.requires_approval_threshold:
            return False
        
        threshold_func = self.requires_approval_threshold[action]
        return threshold_func(params)
    
    async def _request_approval(
        self,
        execution_id: str,
        action: str,
        params: Dict,
        user_context: Optional[Dict]
    ) -> Dict:
        """Create approval request for human review"""
        # In production, this would create a record in database
        # and notify admins via email/Slack
        
        approval_request = {
            "execution_id": execution_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "action": action,
            "params": params,
            "user_context": user_context,
            "requested_at": datetime.utcnow().isoformat(),
            "status": "pending"
        }
        
        self.logger.info(f"Approval requested: {execution_id}")
        
        return {
            "execution_id": execution_id,
            "status": ActionStatus.PENDING_APPROVAL,
            "message": "This action requires human approval",
            "approval_request": approval_request
        }
    
    async def _audit_log(
        self,
        execution_id: str,
        action: str,
        params: Dict,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        status: ActionStatus = ActionStatus.SUCCESS,
        user_context: Optional[Dict] = None
    ):
        """Log action to audit trail"""
        log_entry = {
            "execution_id": execution_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "action": action,
            "params": params,
            "result": result,
            "error": error,
            "status": status.value,
            "user_context": user_context,
            "timestamp": datetime.utcnow().timestamp()
        }
        
        # Store in memory (in production: database + blockchain)
        self.action_history.append(log_entry)
        
        # Log to file/CloudWatch
        self.logger.info(
            f"Action logged: {action} - {status.value}",
            extra=log_entry
        )
    
    def _generate_execution_id(self) -> str:
        """Generate unique execution ID"""
        import uuid
        return f"{self.agent_type.value}_{uuid.uuid4().hex[:12]}"
    
    def _error_response(
        self,
        execution_id: str,
        error_code: str,
        message: str
    ) -> Dict:
        """Standard error response"""
        return {
            "execution_id": execution_id,
            "status": ActionStatus.FAILED,
            "error": {
                "code": error_code,
                "message": message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        total_actions = len(self.action_history)
        if total_actions == 0:
            return {
                "total_actions": 0,
                "success_rate": 0,
                "average_response_time": 0
            }
        
        successful = sum(
            1 for a in self.action_history
            if a["status"] == ActionStatus.SUCCESS.value
        )
        
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "total_actions": total_actions,
            "successful_actions": successful,
            "failed_actions": total_actions - successful,
            "success_rate": successful / total_actions,
            "actions_last_hour": self._count_recent_actions(3600),
            "actions_last_minute": self._count_recent_actions(60)
        }
    
    def _count_recent_actions(self, seconds: int) -> int:
        """Count actions in last N seconds"""
        cutoff = datetime.utcnow().timestamp() - seconds
        return sum(
            1 for a in self.action_history
            if a["timestamp"] > cutoff
        )
