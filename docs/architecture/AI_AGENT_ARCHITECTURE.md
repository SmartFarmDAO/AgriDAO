# AI Agent Architecture for AgriDAO

## Overview
This document outlines the architecture for autonomous AI agents in AgriDAO with security-first design principles.

## Agent Types & Autonomy Levels

### 1. **Advisory Agent** (Low Autonomy)
**Purpose:** Provide farming advice, weather alerts, market insights

**Capabilities:**
- Read crop data, weather APIs, market prices
- Generate recommendations
- Send notifications

**Tools Exposed:**
- `get_weather_forecast(location)`
- `get_market_prices(crop, region)`
- `get_crop_health_data(farm_id)`
- `send_notification(user_id, message)`

**Security:**
- Read-only database access
- Rate limiting: 100 requests/minute
- No financial transactions
- Audit logging enabled

---

### 2. **Market Agent** (Medium Autonomy)
**Purpose:** Match buyers with sellers, suggest pricing

**Capabilities:**
- Analyze supply/demand
- Suggest optimal pricing
- Match orders (with approval)
- Negotiate terms (within limits)

**Tools Exposed:**
- `search_products(filters)`
- `suggest_price(product_id, market_data)`
- `create_match_proposal(buyer_id, seller_id, terms)` ⚠️ Requires approval
- `get_historical_prices(crop, timeframe)`

**Security:**
- Cannot execute transactions directly
- All matches require human approval
- Price suggestions capped at ±20% of market average
- Transaction limits: $1000/day per agent
- Multi-signature for high-value matches

---

### 3. **Finance Agent** (High Autonomy - Restricted)
**Purpose:** Manage loan applications, disbursements, repayments

**Capabilities:**
- Assess creditworthiness
- Approve small loans (<$100)
- Schedule repayments
- Flag suspicious activity

**Tools Exposed:**
- `assess_credit_score(farmer_id)`
- `approve_loan(application_id, amount)` ⚠️ Amount limits
- `schedule_repayment(loan_id, schedule)`
- `flag_fraud(transaction_id, reason)`

**Security:**
- Loan approval limits: $100 max without human review
- Multi-factor authentication for disbursements
- Real-time fraud detection
- Immutable audit trail (blockchain)
- Circuit breaker: Auto-disable after 3 failed transactions
- Daily transaction cap: $5000

---

### 4. **Supply Chain Agent** (Medium Autonomy)
**Purpose:** Track products, verify authenticity, update status

**Capabilities:**
- Update shipment status
- Verify product authenticity
- Alert on delays
- Coordinate logistics

**Tools Exposed:**
- `update_shipment_status(shipment_id, status, location)`
- `verify_product_authenticity(product_id, blockchain_hash)`
- `create_alert(shipment_id, issue_type)`
- `coordinate_pickup(order_id, logistics_partner)`

**Security:**
- GPS verification required for location updates
- Blockchain verification for authenticity
- Cannot modify historical records
- Tamper-proof logging

---

## Security Framework

### 1. **Authentication & Authorization**

```python
class AgentPermission:
    agent_id: str
    agent_type: AgentType
    permissions: List[Permission]
    rate_limits: RateLimits
    transaction_limits: TransactionLimits
    approval_required: List[Action]
    
class Permission:
    resource: str  # e.g., "products", "loans"
    actions: List[str]  # ["read", "write", "delete"]
    conditions: Dict  # {"amount": {"max": 100}}
```

### 2. **Rate Limiting**

```python
RATE_LIMITS = {
    "advisory_agent": {
        "api_calls": 100/minute,
        "notifications": 10/minute,
    },
    "market_agent": {
        "api_calls": 50/minute,
        "price_suggestions": 20/minute,
        "match_proposals": 5/minute,
    },
    "finance_agent": {
        "credit_checks": 10/minute,
        "loan_approvals": 2/minute,
        "disbursements": 1/minute,
    }
}
```

### 3. **Transaction Limits**

```python
TRANSACTION_LIMITS = {
    "finance_agent": {
        "single_loan": 100,  # USD
        "daily_total": 5000,
        "monthly_total": 50000,
    },
    "market_agent": {
        "single_transaction": 1000,
        "daily_total": 10000,
    }
}
```

### 4. **Approval Workflows**

```python
APPROVAL_REQUIRED = {
    "finance_agent": {
        "loan_approval": lambda amount: amount > 100,
        "loan_disbursement": lambda amount: amount > 50,
    },
    "market_agent": {
        "match_execution": lambda value: value > 500,
        "price_override": lambda deviation: abs(deviation) > 0.2,
    }
}
```

### 5. **Audit & Monitoring**

```python
class AgentAuditLog:
    timestamp: datetime
    agent_id: str
    action: str
    resource: str
    parameters: Dict
    result: str
    user_affected: Optional[str]
    approval_status: Optional[str]
    risk_score: float
    
# All agent actions logged to:
# 1. PostgreSQL (queryable)
# 2. Blockchain (immutable)
# 3. CloudWatch (monitoring)
```

---

## Implementation Architecture

### Backend Structure

```
backend/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py              # Base agent class
│   │   ├── advisory_agent.py
│   │   ├── market_agent.py
│   │   ├── finance_agent.py
│   │   ├── supply_chain_agent.py
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── weather.py
│   │       ├── market_data.py
│   │       ├── credit_scoring.py
│   │       └── blockchain.py
│   ├── services/
│   │   ├── agent_manager.py     # Orchestration
│   │   ├── permission_service.py
│   │   ├── approval_service.py
│   │   └── audit_service.py
│   └── routers/
│       └── agents.py            # API endpoints
```

### Base Agent Class

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import logging

class BaseAgent(ABC):
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        permissions: AgentPermission,
        audit_service: AuditService
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.permissions = permissions
        self.audit = audit_service
        self.logger = logging.getLogger(f"agent.{agent_type}")
        
    async def execute_action(
        self,
        action: str,
        params: Dict[str, Any],
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Execute action with security checks"""
        
        # 1. Check permissions
        if not self._has_permission(action):
            raise PermissionError(f"Agent lacks permission for {action}")
        
        # 2. Check rate limits
        if not await self._check_rate_limit(action):
            raise RateLimitError(f"Rate limit exceeded for {action}")
        
        # 3. Check transaction limits
        if not self._check_transaction_limits(action, params):
            raise TransactionLimitError(f"Transaction limit exceeded")
        
        # 4. Check if approval required
        if self._requires_approval(action, params):
            return await self._request_approval(action, params, user_context)
        
        # 5. Execute action
        try:
            result = await self._execute(action, params)
            
            # 6. Audit log
            await self.audit.log(
                agent_id=self.agent_id,
                action=action,
                params=params,
                result=result,
                status="success"
            )
            
            return result
            
        except Exception as e:
            # Log failure
            await self.audit.log(
                agent_id=self.agent_id,
                action=action,
                params=params,
                error=str(e),
                status="failed"
            )
            raise
    
    @abstractmethod
    async def _execute(self, action: str, params: Dict) -> Dict:
        """Implement in subclass"""
        pass
    
    def _has_permission(self, action: str) -> bool:
        """Check if agent has permission for action"""
        return action in self.permissions.allowed_actions
    
    async def _check_rate_limit(self, action: str) -> bool:
        """Check rate limits using Redis"""
        # Implementation with Redis
        pass
    
    def _check_transaction_limits(self, action: str, params: Dict) -> bool:
        """Check transaction limits"""
        # Implementation
        pass
    
    def _requires_approval(self, action: str, params: Dict) -> bool:
        """Check if action requires human approval"""
        approval_rules = self.permissions.approval_required.get(action)
        if not approval_rules:
            return False
        return approval_rules(params)
    
    async def _request_approval(
        self,
        action: str,
        params: Dict,
        user_context: Dict
    ) -> Dict:
        """Create approval request"""
        approval_request = await ApprovalService.create_request(
            agent_id=self.agent_id,
            action=action,
            params=params,
            user_context=user_context
        )
        return {
            "status": "pending_approval",
            "approval_id": approval_request.id,
            "message": "Action requires human approval"
        }
```

---

## Security Best Practices

### 1. **Principle of Least Privilege**
- Agents only get minimum permissions needed
- Permissions reviewed quarterly
- Automatic permission expiry after 90 days

### 2. **Defense in Depth**
```
Layer 1: Authentication (API keys, JWT)
Layer 2: Authorization (RBAC)
Layer 3: Rate limiting
Layer 4: Transaction limits
Layer 5: Approval workflows
Layer 6: Audit logging
Layer 7: Anomaly detection
```

### 3. **Circuit Breaker Pattern**
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half_open"
            else:
                raise CircuitBreakerOpen("Agent temporarily disabled")
        
        try:
            result = await func(*args, **kwargs)
            if self.state == "half_open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                await self._notify_admin("Agent circuit breaker opened")
            raise
```

### 4. **Anomaly Detection**
```python
class AnomalyDetector:
    async def detect(self, agent_id: str, action: str, params: Dict):
        # Check for unusual patterns
        patterns = [
            self._check_velocity(agent_id, action),
            self._check_amount_deviation(params),
            self._check_time_pattern(agent_id),
            self._check_geographic_anomaly(params),
        ]
        
        risk_score = sum(patterns) / len(patterns)
        
        if risk_score > 0.7:
            await self._flag_for_review(agent_id, action, risk_score)
            return False
        
        return True
```

### 5. **Encryption**
- All agent API keys encrypted at rest (AES-256)
- TLS 1.3 for all communications
- Sensitive parameters encrypted in audit logs
- Blockchain for immutable audit trail

---

## Monitoring & Alerts

### Metrics to Track
```python
AGENT_METRICS = {
    "actions_per_minute": Gauge,
    "success_rate": Gauge,
    "average_response_time": Histogram,
    "approval_requests": Counter,
    "rate_limit_hits": Counter,
    "transaction_limit_hits": Counter,
    "circuit_breaker_trips": Counter,
    "anomaly_detections": Counter,
}
```

### Alert Thresholds
```python
ALERTS = {
    "high_failure_rate": {
        "condition": "success_rate < 0.9",
        "severity": "warning",
        "action": "notify_admin"
    },
    "circuit_breaker_open": {
        "condition": "circuit_breaker_trips > 0",
        "severity": "critical",
        "action": "disable_agent"
    },
    "anomaly_detected": {
        "condition": "anomaly_detections > 5/hour",
        "severity": "high",
        "action": "require_approval_for_all"
    }
}
```

---

## Rollout Strategy

### Phase 1: Advisory Agent (Month 1-2)
- Low risk, read-only
- Test infrastructure
- Gather user feedback

### Phase 2: Market Agent (Month 3-4)
- Medium risk, approval workflows
- Monitor closely
- Adjust limits based on data

### Phase 3: Supply Chain Agent (Month 5-6)
- Medium risk, blockchain integration
- Verify tamper-proofing

### Phase 4: Finance Agent (Month 7-12)
- High risk, start with $10 limits
- Gradually increase based on performance
- Extensive testing and monitoring

---

## Cost Estimate

### Infrastructure
```
LLM API (OpenAI/Anthropic): $200-500/month
Redis (rate limiting): $15/month
CloudWatch (monitoring): $30/month
Additional compute: $50/month
---
Total: $295-595/month
```

### Development Time
```
Phase 1 (Advisory): 2 weeks
Phase 2 (Market): 3 weeks
Phase 3 (Supply Chain): 3 weeks
Phase 4 (Finance): 4 weeks
Security hardening: 2 weeks
Testing: 2 weeks
---
Total: 16 weeks (4 months)
```

---

## Compliance & Legal

### Data Privacy
- GDPR compliance for EU users
- Data minimization for agent access
- Right to explanation for AI decisions
- Opt-out mechanism for users

### Financial Regulations
- Comply with local lending laws
- KYC/AML for finance agent
- Transaction reporting
- Audit trail retention (7 years)

### Liability
- Clear terms of service
- Agent decisions are recommendations
- Human oversight for critical actions
- Insurance for agent errors

---

## Next Steps

1. **Review & Approve** this architecture
2. **Implement Phase 1** (Advisory Agent)
3. **Security Audit** by external firm
4. **Pilot Program** with 100 users
5. **Iterate** based on feedback
6. **Scale** gradually

---

## Questions to Answer

1. What LLM provider? (OpenAI, Anthropic, self-hosted?)
2. What's acceptable risk tolerance for finance agent?
3. Who approves high-value transactions?
4. What's the escalation process for anomalies?
5. How do we handle agent errors/compensation?

---

**Document Version:** 1.0  
**Last Updated:** 2025-12-03  
**Owner:** Engineering Team  
**Reviewers:** Security, Legal, Product
