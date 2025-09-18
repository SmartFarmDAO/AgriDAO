# AgriDAO Integration Testing Guide

## Overview
This guide provides comprehensive integration testing procedures for the AgriDAO marketplace platform, covering all major system components and user flows.

## Test Environment Setup

### Prerequisites
- Node.js 18+ installed
- All dependencies installed (`npm install`)
- Backend services running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- PostgreSQL database configured
- Redis cache configured
- Firebase configuration for push notifications
- Cloud storage configured (AWS S3, Google Cloud Storage, or Azure Blob)

### Environment Variables
```bash
# Backend (.env)
DATABASE_URL=postgresql://user:password@localhost:5432/agridao
REDIS_URL=redis://localhost:6379
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY=your-private-key
STORAGE_PROVIDER=aws|gcp|azure
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_REGION=us-east-1

# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=your-app-id
```

## Integration Test Suites

### 1. Authentication Flow Tests

#### Test 1.1: Complete Registration Flow
```bash
npm run test:e2e -- --grep "Authentication"
```

**Steps:**
1. Navigate to registration page
2. Fill valid user details (farmer role)
3. Submit registration form
4. Verify email confirmation
5. Login with new credentials
6. Verify dashboard access

**Expected Results:**
- User successfully registered
- Email verification sent
- JWT token generated
- User redirected to role-specific dashboard

#### Test 1.2: Multi-Role Authentication
**Test Users:**
- Farmer: `farmer@test.com / Test123!@#`
- Buyer: `buyer@test.com / Test123!@#`
- Admin: `admin@test.com / Test123!@#`

**Verification:**
- Role-based access control
- Permission enforcement
- Dashboard customization per role

### 2. Marketplace Integration Tests

#### Test 2.1: Product Lifecycle
```bash
npm run test:e2e -- --grep "Marketplace"
```

**Farmer Actions:**
1. Create new product listing
2. Upload product images
3. Set pricing and inventory
4. Publish to marketplace
5. Update product details
6. Manage inventory levels

**Buyer Actions:**
1. Browse marketplace
2. Search and filter products
3. View product details
4. Add to cart
5. Save favorites
6. Compare products

#### Test 2.2: Search and Discovery
**Test Queries:**
- Basic search: "tomatoes", "organic"
- Category filters: "vegetables", "fruits", "grains"
- Price range: $0-$10, $10-$50, $50+
- Location-based: "within 50 miles"
- Quality certifications: "organic", "non-GMO"

### 3. Transaction Flow Tests

#### Test 3.1: Complete Purchase Flow
**Steps:**
1. Buyer adds products to cart
2. Proceed to checkout
3. Enter shipping information
4. Select payment method
5. Place order
6. Receive order confirmation
7. Track order status

**Payment Methods:**
- Credit card (Stripe)
- PayPal
- Bank transfer
- Digital wallet

#### Test 3.2: Order Management
**Farmer View:**
- Receive new order notifications
- Confirm order acceptance
- Update order status
- Generate shipping labels
- Upload tracking information

**Buyer View:**
- Receive order confirmation
- Track order progress
- Receive delivery notifications
- Rate and review products

### 4. Real-time Features

#### Test 4.1: Push Notifications
**Test Scenarios:**
- New order notifications
- Price change alerts
- Inventory low warnings
- Delivery updates
- System announcements

**Platforms:**
- Web push notifications
- iOS push notifications
- Android push notifications

#### Test 4.2: Live Updates
**Tests:**
- Product availability changes
- Price updates
- New product listings
- Order status changes
- Chat messages

### 5. Offline Functionality

#### Test 5.1: Offline Product Browsing
1. Navigate to marketplace
2. Disconnect internet
3. Browse cached products
4. Add items to cart
5. Reconnect internet
6. Verify cart synchronization

#### Test 5.2: Offline Order Creation
1. Add products to cart offline
2. Fill checkout information
3. Submit order when online
4. Verify order processing

### 6. File Storage Integration

#### Test 6.1: Image Upload and Processing
**Test Cases:**
- Upload product images (JPEG, PNG, WebP)
- Image size validation (max 10MB)
- Multiple image uploads
- Image compression and optimization
- CDN delivery verification

**Storage Providers:**
- AWS S3
- Google Cloud Storage
- Azure Blob Storage

#### Test 6.2: File Management
- User profile photos
- Product documentation
- Certification documents
- Invoice downloads
- Backup and recovery

### 7. Database Integration

#### Test 7.1: Data Consistency
**Tests:**
- User profile updates
- Product inventory changes
- Order status updates
- Transaction records
- Audit trail maintenance

#### Test 7.2: Concurrent Operations
**Scenarios:**
- Multiple users updating same product
- Simultaneous order placements
- Inventory race conditions
- Database transaction integrity

### 8. API Integration

#### Test 8.1: RESTful API Endpoints
**Critical Endpoints:**
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/products`
- `POST /api/products`
- `POST /api/orders`
- `GET /api/orders/:id`
- `POST /api/upload`
- `GET /api/notifications`

#### Test 8.2: Error Handling
**Test Cases:**
- Invalid authentication tokens
- Rate limiting (429 responses)
- Validation errors (400 responses)
- Server errors (500 responses)
- Network timeouts

### 9. Mobile Integration

#### Test 9.1: Responsive Design
**Devices:**
- iPhone SE (375px)
- iPhone 12 (390px)
- iPad (768px)
- Desktop (1440px)

**Orientations:**
- Portrait
- Landscape

#### Test 9.2: Touch Interactions
**Gestures:**
- Swipe navigation
- Pinch-to-zoom images
- Pull-to-refresh
- Long press actions
- Touch-friendly buttons

### 10. Performance Testing

#### Test 10.1: Load Testing
```bash
# Run load tests
npm run test:load

# Run performance tests
npm run test:performance
```

**Metrics:**
- Page load times < 3 seconds
- API response times < 500ms
- Image loading optimization
- Database query performance
- CDN effectiveness

#### Test 10.2: Stress Testing
**Scenarios:**
- 1000 concurrent users
- 10000 product listings
- 100 transactions per minute
- 1000 search queries per minute

### 11. Security Testing

#### Test 11.1: Authentication Security
```bash
npm run test:security
```

**Tests:**
- SQL injection prevention
- XSS protection
- CSRF token validation
- Rate limiting enforcement
- Password complexity requirements

#### Test 11.2: Authorization Testing
- Role-based access control
- Permission inheritance
- API endpoint security
- Data privacy compliance

### 12. Cross-Browser Testing

#### Test 12.1: Browser Compatibility
**Browsers:**
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile Safari (iOS)
- Chrome Mobile (Android)

#### Test 12.2: Progressive Enhancement
- JavaScript disabled fallback
- CSS grid/flexbox fallbacks
- Image lazy loading
- Service worker functionality

## Test Execution Commands

### Run All Tests
```bash
# Start development servers
npm run dev

# Run all E2E tests
npm run test:e2e

# Run specific test suites
npm run test:e2e -- --grep "Authentication"
npm run test:e2e -- --grep "Marketplace"
npm run test:e2e -- --grep "Security"

# Run performance tests
npm run test:performance

# Run load tests
npm run test:load

# Run security tests
npm run test:security
```

### Mobile Testing
```bash
# Run mobile-specific tests
npm run test:e2e -- --project="Mobile Chrome"
npm run test:e2e -- --project="Mobile Safari"
```

### Debug Mode
```bash
# Run tests in headed mode
npm run test:e2e -- --headed

# Run tests with UI
npm run test:e2e -- --ui

# Run specific test with debug
npm run test:e2e -- --debug --grep "Complete marketplace flow"
```

## Test Data Setup

### Pre-populated Test Data
```sql
-- Users
INSERT INTO users (email, name, role, verified) VALUES
('farmer@test.com', 'Test Farmer', 'farmer', true),
('buyer@test.com', 'Test Buyer', 'buyer', true),
('admin@test.com', 'Test Admin', 'admin', true);

-- Products
INSERT INTO products (name, description, price, quantity, farmer_id, category) VALUES
('Organic Tomatoes', 'Fresh organic tomatoes', 3.99, 100, 1, 'vegetables'),
('Fresh Lettuce', 'Crisp lettuce heads', 2.49, 50, 1, 'vegetables'),
('Farm Eggs', 'Free-range eggs', 4.99, 30, 1, 'dairy');
```

### Test Images
Place test images in `e2e/test-images/`:
- `test-1mb.jpg` (1MB product image)
- `test-5mb.jpg` (5MB product image)
- `test-profile.jpg` (Profile photo)

## Monitoring and Reporting

### Test Results
- HTML reports: `playwright-report/index.html`
- Performance metrics: `performance-results.json`
- Load test reports: `artillery-report.json`

### Continuous Integration
```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run test:e2e
      - run: npm run test:performance
```

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 3000 and 8000 are available
2. **Database connection**: Verify PostgreSQL is running
3. **Storage credentials**: Check cloud storage configuration
4. **Firebase setup**: Verify Firebase project configuration
5. **Test data**: Ensure test users and products exist

### Debug Commands
```bash
# Check service health
curl http://localhost:8000/health

# Verify database connection
psql -h localhost -U postgres -d agridao -c "SELECT 1"

# Check storage access
aws s3 ls your-bucket-name

# Monitor logs
tail -f logs/development.log
```

## Test Coverage Requirements

### Minimum Coverage
- E2E tests: 90% critical user flows
- API tests: 100% endpoint coverage
- Security tests: 100% OWASP Top 10
- Performance tests: All critical paths
- Mobile tests: All responsive breakpoints

### Success Criteria
- All tests pass in CI/CD
- Performance benchmarks met
- Security scan clean
- Accessibility compliance (WCAG 2.1)
- Cross-browser compatibility verified