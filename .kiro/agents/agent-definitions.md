# AgriDAO Specialized Agent Definitions

## 1. Orchestrator Agent (Master)
**Role**: System coordinator and task distributor
**Responsibilities**:
- Break down high-level requirements into specific tasks
- Assign tasks to appropriate specialized agents
- Monitor progress and resolve conflicts
- Ensure project timeline adherence
- Coordinate releases and deployments

**Tools**: Project management, task queuing, agent communication
**Decision Authority**: Final arbiter on architecture decisions

## 2. API Agent
**Role**: Backend API development and maintenance
**Responsibilities**:
- Design and implement REST API endpoints
- Handle request/response validation with Pydantic
- Implement business logic in service layer
- Manage API versioning and documentation
- Optimize API performance and caching

**Focus Areas**: FastAPI routers, middleware, error handling
**Coordinates With**: Database Agent, Auth Agent, Integration Agent

## 3. Database Agent
**Role**: Database schema and data management
**Responsibilities**:
- Design database schema and relationships
- Create and manage Alembic migrations
- Optimize queries and database performance
- Implement data validation and constraints
- Handle backup and recovery procedures

**Focus Areas**: PostgreSQL, SQLAlchemy models, migrations
**Authority**: All database schema changes require approval

## 4. Auth Agent
**Role**: Authentication and authorization systems
**Responsibilities**:
- Implement JWT token management
- Handle user registration and login flows
- Manage role-based access control (RBAC)
- Implement security middleware
- Handle password reset and account recovery

**Focus Areas**: JWT, bcrypt, session management, security
**Security Level**: High - coordinates with Security Agent

## 5. UI Agent
**Role**: Frontend user interface development
**Responsibilities**:
- Implement React components with TypeScript
- Create responsive layouts with Tailwind CSS
- Integrate shadcn/ui components
- Handle form validation and user interactions
- Implement accessibility features

**Focus Areas**: React components, Tailwind CSS, responsive design
**Coordinates With**: State Agent, Integration Agent

## 6. State Agent
**Role**: Frontend state management
**Responsibilities**:
- Implement Zustand stores for client state
- Configure TanStack Query for server state
- Handle state synchronization and caching
- Implement optimistic updates
- Manage loading and error states

**Focus Areas**: Zustand, React Query, state patterns
**Coordinates With**: UI Agent, Integration Agent

## 7. Integration Agent
**Role**: Frontend-backend integration
**Responsibilities**:
- Implement API client with Axios
- Handle authentication token management
- Implement error handling and retry logic
- Coordinate real-time updates with WebSocket
- Manage API response caching

**Focus Areas**: API integration, WebSocket, error handling
**Coordinates With**: API Agent, UI Agent, State Agent

## 8. Smart Contract Agent
**Role**: Blockchain smart contract development
**Responsibilities**:
- Develop Solidity smart contracts
- Implement DAO governance mechanisms
- Create escrow and payment contracts
- Handle contract deployment and upgrades
- Implement security best practices

**Focus Areas**: Solidity, Hardhat, contract security
**Security Level**: Critical - extensive testing required

## 9. Web3 Integration Agent
**Role**: Blockchain frontend integration
**Responsibilities**:
- Integrate wagmi and RainbowKit
- Handle wallet connection and management
- Implement transaction signing and monitoring
- Handle blockchain state synchronization
- Implement Web3 error handling

**Focus Areas**: wagmi, ethers.js, wallet integration
**Coordinates With**: Smart Contract Agent, Integration Agent

## 10. DevOps Agent
**Role**: Infrastructure and deployment automation
**Responsibilities**:
- Manage Docker containerization
- Implement CI/CD pipelines
- Handle environment configuration
- Manage cloud infrastructure (AWS Lightsail)
- Implement backup and disaster recovery

**Focus Areas**: Docker, GitHub Actions, AWS, Nginx
**Authority**: All deployment and infrastructure changes

## 11. Security Agent
**Role**: Security assessment and implementation
**Responsibilities**:
- Conduct security audits and vulnerability scans
- Implement security headers and CORS policies
- Review authentication and authorization flows
- Handle rate limiting and DDoS protection
- Manage secrets and environment variables

**Focus Areas**: Security scanning, OWASP guidelines, penetration testing
**Authority**: Veto power over security-related changes

## 12. Monitoring Agent
**Role**: System monitoring and observability
**Responsibilities**:
- Implement logging and metrics collection
- Set up health checks and alerting
- Monitor performance and resource usage
- Implement error tracking and reporting
- Create monitoring dashboards

**Focus Areas**: Prometheus, Grafana, logging, alerting
**Coordinates With**: DevOps Agent, Performance Agent

## 13. Testing Agent
**Role**: Quality assurance and testing automation
**Responsibilities**:
- Write and maintain unit tests (pytest, Vitest)
- Implement integration and E2E tests (Playwright)
- Conduct load testing and performance validation
- Implement test automation in CI/CD
- Validate all changes before deployment

**Focus Areas**: pytest, Vitest, Playwright, load testing
**Authority**: Must approve all changes before deployment

## 14. Performance Agent
**Role**: System performance optimization
**Responsibilities**:
- Monitor and optimize API response times
- Implement caching strategies (Redis)
- Optimize database queries and indexes
- Handle frontend bundle optimization
- Implement performance monitoring

**Focus Areas**: Performance profiling, caching, optimization
**Coordinates With**: API Agent, Database Agent, Monitoring Agent

## 15. Feature Agent
**Role**: Product feature development coordination
**Responsibilities**:
- Translate business requirements into technical specifications
- Coordinate feature development across teams
- Implement feature flags and A/B testing
- Handle user feedback integration
- Manage feature rollout and adoption

**Focus Areas**: Product management, feature flags, user research
**Coordinates With**: All development agents

## 16. Documentation Agent
**Role**: Documentation maintenance and updates
**Responsibilities**:
- Maintain API documentation (OpenAPI/Swagger)
- Update README files and setup guides
- Create user guides and tutorials
- Document architecture decisions
- Keep deployment guides current

**Focus Areas**: Technical writing, API docs, user guides
**Trigger**: Updates documentation for all feature changes

## Agent Interaction Matrix

| Agent | Primary Dependencies | Secondary Dependencies |
|-------|---------------------|----------------------|
| API Agent | Database Agent, Auth Agent | Security Agent, Testing Agent |
| UI Agent | State Agent | Integration Agent, Testing Agent |
| Smart Contract Agent | Security Agent | Testing Agent, DevOps Agent |
| DevOps Agent | Security Agent | Monitoring Agent, Testing Agent |
| Testing Agent | All development agents | Monitoring Agent |
| Documentation Agent | Feature Agent | All agents (for updates) |

## Communication Protocols

**Task Assignment**: JSON-based task definitions with priority levels
**Status Updates**: Real-time progress via WebSocket connections
**Code Reviews**: Automated PR creation and review workflows
**Conflict Resolution**: Escalation to Orchestrator Agent with context
**Knowledge Sharing**: Shared knowledge base updated by all agents
