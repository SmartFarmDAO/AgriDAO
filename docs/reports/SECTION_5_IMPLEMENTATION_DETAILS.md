# Section 5: Implementation - Detailed Content

## 5.1 Technology Stack (Enhanced)

### Frontend Technologies

**Core Framework:**
- **React 18.2.0**: Concurrent rendering, automatic batching, transitions API
- **TypeScript 5.0**: Strict type checking, enhanced IDE support
- **Vite 5.0**: Lightning-fast HMR (<50ms), optimized production builds

**State Management:**
- **Zustand 4.4**: Lightweight (1KB), no boilerplate, TypeScript-first
- **TanStack Query 5.0**: Server state caching, automatic refetching
- **React Hook Form 7.48**: Performant forms with minimal re-renders

**UI & Styling:**
- **Tailwind CSS 3.4**: Utility-first, custom design system
- **Radix UI**: Accessible primitives (WCAG 2.1 AA compliant)
- **Framer Motion 10**: Smooth animations, gesture support
- **Lucide React**: 1000+ optimized icons

**PWA & Offline:**
- **Workbox 7.0**: Service worker generation and caching strategies
- **IndexedDB**: Local database (Dexie.js wrapper)
- **Background Sync API**: Queue offline transactions

### Backend Technologies

**Core Framework:**
- **FastAPI 0.104**: Async support, automatic OpenAPI docs
- **Python 3.11**: 25% faster than 3.10, improved error messages
- **Uvicorn**: ASGI server with WebSocket support

**Database & Caching:**
- **PostgreSQL 14**: ACID compliance, JSON support, full-text search
- **SQLModel**: Type-safe ORM combining SQLAlchemy + Pydantic
- **Redis 7.0**: Sub-millisecond latency, pub/sub messaging
- **Alembic**: Database migrations with version control

**Security & Authentication:**
- **JWT (PyJWT)**: Stateless authentication with refresh tokens
- **Passlib + Bcrypt**: Password hashing (cost factor 12)
- **Python-JOSE**: JWT encoding/decoding
- **OTP (PyOTP)**: Time-based one-time passwords

**Blockchain Integration:**
- **Web3.py 6.0**: Ethereum interaction library
- **Ethers.js 6.0**: Frontend wallet integration
- **Hardhat**: Smart contract development and testing
- **OpenZeppelin Contracts**: Audited contract libraries

### DevOps & Infrastructure

**Containerization:**
- **Docker 24.0**: Multi-stage builds, layer caching
- **Docker Compose**: Local development orchestration
- **Kubernetes**: Production orchestration (planned)

**CI/CD:**
- **GitHub Actions**: Automated testing and deployment
- **SonarQube**: Code quality and security analysis
- **Snyk**: Dependency vulnerability scanning

**Monitoring & Logging:**
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization dashboards
- **ELK Stack**: Centralized logging (Elasticsearch, Logstash, Kibana)
- **Sentry**: Error tracking and performance monitoring

**Cloud Services:**
- **AWS S3**: Object storage for images/documents
- **AWS CloudFront**: CDN for static assets
- **AWS RDS**: Managed PostgreSQL
- **AWS ElastiCache**: Managed Redis

## 5.2 Core Modules Implementation (Detailed)

### 5.2.1 Authentication Module

**Implementation Details:**

```typescript
// Frontend: Auth Hook
export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = secureStorage.get('access_token');
    if (token) {
      validateToken(token).then(setUser);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, code: string) => {
    const response = await verifyOtp(email, code);
    secureStorage.set('access_token', response.access_token);
    setUser(response.user);
  };

  return { user, login, logout, isLoading };
};
```

**Backend: JWT Implementation**

```python
# Token generation with refresh token
def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=30)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def create_refresh_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**Security Features:**
- ✅ JWT with 30-minute expiry
- ✅ Refresh tokens (7-day expiry)
- ✅ Token blacklisting on logout
- ✅ Rate limiting (5 attempts per 15 minutes)
- ✅ OTP verification (6-digit, 5-minute expiry)

### 5.2.2 Product Management Module

**Database Schema:**

```sql
CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    quantity_available INTEGER DEFAULT 0,
    unit VARCHAR(50) DEFAULT 'piece',
    farmer_id INTEGER REFERENCES farmer(id),
    status VARCHAR(20) DEFAULT 'ACTIVE',
    images JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_product_farmer ON product(farmer_id);
CREATE INDEX idx_product_category ON product(category);
CREATE INDEX idx_product_status ON product(status);
```

**API Endpoints:**

```python
@router.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    # Validate user is farmer
    if current_user.role != UserRole.FARMER:
        raise HTTPException(403, "Only farmers can create products")
    
    # Create product
    db_product = Product(**product.dict(), farmer_id=current_user.id)
    session.add(db_product)
    session.commit()
    
    return db_product
```

**Image Upload with Virus Scanning:**

```python
async def upload_product_image(file: UploadFile):
    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(400, "Invalid file type")
    
    # Scan for viruses
    scan_result = await virus_scanner.scan(file.file)
    if not scan_result.is_clean:
        raise HTTPException(400, "File contains malware")
    
    # Optimize image
    optimized = await image_optimizer.optimize(file.file)
    
    # Upload to S3
    s3_key = f"products/{uuid4()}.jpg"
    await s3_client.upload(optimized, s3_key)
    
    return f"https://cdn.agridao.com/{s3_key}"
```

### 5.2.3 Order Management Module

**State Machine Implementation:**

```python
class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderStateMachine:
    TRANSITIONS = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
        OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
        OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: []
    }
    
    @staticmethod
    def can_transition(from_status: OrderStatus, to_status: OrderStatus) -> bool:
        return to_status in OrderStateMachine.TRANSITIONS.get(from_status, [])
```

**Order Creation with Transaction:**

```python
@router.post("/orders", response_model=Order)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    async with session.begin():
        # Calculate totals
        subtotal = sum(item.quantity * item.unit_price for item in order_data.items)
        platform_fee = subtotal * 0.05  # 5% platform fee
        total = subtotal + platform_fee
        
        # Create order
        order = Order(
            buyer_id=current_user.id,
            subtotal=subtotal,
            platform_fee=platform_fee,
            total=total,
            status=OrderStatus.PENDING
        )
        session.add(order)
        await session.flush()
        
        # Create order items
        for item_data in order_data.items:
            item = OrderItem(**item_data.dict(), order_id=order.id)
            session.add(item)
            
            # Update product inventory
            product = await session.get(Product, item_data.product_id)
            product.quantity_available -= item_data.quantity
        
        await session.commit()
        return order
```
