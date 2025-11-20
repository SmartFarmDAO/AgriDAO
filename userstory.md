# AgriDAO - System-Wide User Stories

## Document Information
- **Project:** AgriDAO - Agricultural Marketplace Platform
- **Version:** 1.0
- **Last Updated:** November 20, 2025
- **Status:** Production Ready (67% Complete)

---

## Table of Contents
1. [Authentication & User Management](#1-authentication--user-management)
2. [Farmer Features](#2-farmer-features)
3. [Buyer Features](#3-buyer-features)
4. [Admin Features](#4-admin-features)
5. [Marketplace Features](#5-marketplace-features)
6. [Order Management](#6-order-management)
7. [Payment & Finance](#7-payment--finance)
8. [Analytics & Reporting](#8-analytics--reporting)
9. [Security & Privacy](#9-security--privacy)
10. [Mobile & PWA](#10-mobile--pwa)
11. [Future Features](#11-future-features)

---

## 1. Authentication & User Management

### US-1.1: Email OTP Authentication ✅
**As a** user  
**I want to** sign in using my email with a one-time password  
**So that** I can securely access the platform without remembering complex passwords

**Acceptance Criteria:**
- User enters email address
- System sends 6-digit OTP code to email
- User enters OTP code within 5 minutes
- System creates secure session with JWT tokens
- User is redirected to appropriate dashboard based on role

**Status:** ✅ Implemented

---

### US-1.2: Role-Based Access Control ✅
**As a** platform administrator  
**I want to** assign different roles (Buyer, Farmer, Admin) to users  
**So that** each user has appropriate access to features

**Acceptance Criteria:**
- System supports three roles: BUYER, FARMER, ADMIN
- Each role has specific permissions
- Protected routes enforce role-based access
- Unauthorized access attempts are blocked with 403 error

**Status:** ✅ Implemented

---

### US-1.3: Session Management ✅
**As a** user  
**I want** my session to be managed securely  
**So that** my account remains protected

**Acceptance Criteria:**
- Sessions expire after inactivity
- Refresh tokens allow seamless re-authentication
- User can logout from current device
- User can logout from all devices
- Revoked tokens are blacklisted

**Status:** ✅ Implemented

---

## 2. Farmer Features

### US-2.1: Farmer Profile Creation ✅
**As a** new farmer  
**I want to** create my farmer profile  
**So that** I can start selling products on the platform

**Acceptance Criteria:**
- User can register as a farmer with name, location, contact info
- System links farmer profile to user account via email
- User role is automatically upgraded to FARMER
- Profile is visible to buyers

**Status:** ✅ Implemented

---

### US-2.2: Product Listing Management ✅
**As a** farmer  
**I want to** create, update, and delete product listings  
**So that** I can manage my inventory effectively

**Acceptance Criteria:**
- Farmer can add new products with name, description, price, quantity
- Farmer can upload product images
- Farmer can update product details
- Farmer can mark products as active/inactive
- Farmer can delete products (if no active orders)

**Status:** ✅ Implemented

---

### US-2.3: Inventory Management ✅
**As a** farmer  
**I want to** track and update my product inventory  
**So that** buyers see accurate stock availability

**Acceptance Criteria:**
- System tracks quantity available for each product
- Inventory automatically decreases when orders are placed
- Farmer receives alerts when stock is low
- Products automatically marked as out-of-stock when quantity reaches zero

**Status:** ✅ Implemented

---

### US-2.4: Order Fulfillment ✅
**As a** farmer  
**I want to** view and manage orders for my products  
**So that** I can fulfill customer orders efficiently

**Acceptance Criteria:**
- Farmer sees all orders for their products
- Farmer can update order status (pending → confirmed → fulfilled)
- Farmer can add tracking information
- Buyers are notified of status changes

**Status:** ✅ Implemented

---

### US-2.5: Farmer Dashboard ✅
**As a** farmer  
**I want** a dashboard showing my products and orders  
**So that** I can manage my business at a glance

**Acceptance Criteria:**
- Dashboard shows total products, active listings, orders
- Quick access to add new products
- Recent orders displayed
- Product performance metrics

**Status:** ✅ Implemented

---

## 3. Buyer Features

### US-3.1: Product Browsing ✅
**As a** buyer  
**I want to** browse available products  
**So that** I can find items I want to purchase

**Acceptance Criteria:**
- Buyer can view all active products
- Products display name, price, image, farmer info
- Products can be filtered by category
- Products can be searched by name
- Out-of-stock products are clearly marked

**Status:** ✅ Implemented

---

### US-3.2: Shopping Cart ✅
**As a** buyer  
**I want to** add products to a shopping cart  
**So that** I can purchase multiple items at once

**Acceptance Criteria:**
- Buyer can add products to cart
- Buyer can adjust quantities in cart
- Buyer can remove items from cart
- Cart persists across browser sessions
- Cart shows total price

**Status:** ✅ Implemented

---

### US-3.3: Checkout & Payment ✅
**As a** buyer  
**I want to** securely checkout and pay for my order  
**So that** I can complete my purchase

**Acceptance Criteria:**
- Buyer proceeds to checkout from cart
- System validates inventory availability
- Integration with Stripe for payment processing
- Buyer receives order confirmation email
- Order is created in system upon successful payment

**Status:** ✅ Implemented

---

### US-3.4: Order Tracking ✅
**As a** buyer  
**I want to** track my orders  
**So that** I know when to expect delivery

**Acceptance Criteria:**
- Buyer can view all their orders
- Order status is clearly displayed (pending, confirmed, fulfilled)
- Buyer receives notifications on status changes
- Buyer can view order details and items

**Status:** ✅ Implemented

---

### US-3.5: Order History ✅
**As a** buyer  
**I want to** view my past orders  
**So that** I can reorder or reference previous purchases

**Acceptance Criteria:**
- Buyer can access complete order history
- Orders are sorted by date (newest first)
- Each order shows items, total, status, date
- Buyer can view detailed order information

**Status:** ✅ Implemented

---

## 4. Admin Features

### US-4.1: User Management ✅
**As an** admin  
**I want to** manage all users on the platform  
**So that** I can maintain platform integrity

**Acceptance Criteria:**
- Admin can view all users
- Admin can update user roles (BUYER, FARMER, ADMIN)
- Admin can suspend/activate user accounts
- Admin can delete users (with safeguards)
- Admin cannot delete themselves

**Status:** ✅ Implemented

---

### US-4.2: Product Moderation ✅
**As an** admin  
**I want to** moderate product listings  
**So that** I can ensure quality and compliance

**Acceptance Criteria:**
- Admin can view all products
- Admin can edit any product
- Admin can activate/deactivate products
- Admin can delete inappropriate products

**Status:** ✅ Implemented

---

### US-4.3: Order Management ✅
**As an** admin  
**I want to** oversee all orders  
**So that** I can resolve issues and monitor platform activity

**Acceptance Criteria:**
- Admin can view all orders across the platform
- Admin can update order status
- Admin can cancel orders if needed
- Admin can view order details and history

**Status:** ✅ Implemented

---

### US-4.4: Platform Analytics ✅
**As an** admin  
**I want to** view platform-wide analytics  
**So that** I can make informed business decisions

**Acceptance Criteria:**
- Dashboard shows total users, products, orders, revenue
- Charts display trends over time
- Top products and farmers are highlighted
- Real-time metrics are available

**Status:** ✅ Implemented

---

### US-4.5: Dispute Resolution ✅
**As an** admin  
**I want to** manage disputes between buyers and farmers  
**So that** I can ensure fair resolution

**Acceptance Criteria:**
- Admin can view all disputes
- Admin can filter disputes by status/priority
- Admin can update dispute status
- Admin can add resolution notes
- Admin can assign disputes to team members

**Status:** ✅ Implemented

---

## 5. Marketplace Features

### US-5.1: Product Search ✅
**As a** user  
**I want to** search for products  
**So that** I can quickly find what I need

**Acceptance Criteria:**
- Search bar available on marketplace page
- Search works on product name and description
- Results update in real-time
- No results message displayed when appropriate

**Status:** ✅ Implemented

---

### US-5.2: Product Categories ✅
**As a** user  
**I want to** filter products by category  
**So that** I can browse specific types of products

**Acceptance Criteria:**
- Products are organized into categories
- Category filter available on marketplace
- Multiple categories supported (Vegetables, Fruits, Grains, etc.)
- Category counts displayed

**Status:** ✅ Implemented

---

### US-5.3: Product Details ✅
**As a** user  
**I want to** view detailed product information  
**So that** I can make informed purchase decisions

**Acceptance Criteria:**
- Product page shows all details (name, description, price, quantity)
- Product images are displayed
- Farmer information is visible
- Stock availability is clear
- Add to cart button is prominent

**Status:** ✅ Implemented

---

### US-5.4: Product Images ✅
**As a** farmer  
**I want to** upload multiple images for my products  
**So that** buyers can see what they're purchasing

**Acceptance Criteria:**
- Farmer can upload up to 5 images per product
- Images are optimized and resized automatically
- Primary image is displayed in listings
- All images viewable in product details
- Image preview available during upload

**Status:** ✅ Implemented

---

## 6. Order Management

### US-6.1: Order Creation ✅
**As a** buyer  
**I want** orders to be created automatically after payment  
**So that** my purchase is recorded

**Acceptance Criteria:**
- Order created upon successful Stripe payment
- Order includes all cart items
- Order status set to "pending"
- Order ID generated and displayed
- Confirmation email sent

**Status:** ✅ Implemented

---

### US-6.2: Order Status Updates ✅
**As a** farmer or admin  
**I want to** update order status  
**So that** buyers are informed of progress

**Acceptance Criteria:**
- Status can be updated: pending → confirmed → fulfilled
- Buyer receives notification on each status change
- Status history is tracked
- Only authorized users can update status

**Status:** ✅ Implemented

---

### US-6.3: Order Notifications ✅
**As a** user  
**I want to** receive notifications about my orders  
**So that** I stay informed

**Acceptance Criteria:**
- Email notifications sent on order creation
- Notifications sent on status changes
- Notifications include order details
- Notification preferences can be managed

**Status:** ✅ Implemented

---

### US-6.4: Order Cancellation ✅
**As a** buyer or admin  
**I want to** cancel orders when necessary  
**So that** I can handle changes or issues

**Acceptance Criteria:**
- Buyer can cancel pending orders
- Admin can cancel any order
- Inventory is restored upon cancellation
- Refund is processed if payment was made
- All parties are notified

**Status:** ✅ Implemented

---

## 7. Payment & Finance

### US-7.1: Stripe Integration ✅
**As a** buyer  
**I want to** pay securely using Stripe  
**So that** my payment information is protected

**Acceptance Criteria:**
- Stripe checkout session created for orders
- Multiple payment methods supported (card, digital wallets)
- Payment processed securely
- Webhook handles payment confirmation
- Failed payments handled gracefully

**Status:** ✅ Implemented

---

### US-7.2: Platform Fee ✅
**As a** platform operator  
**I want to** collect a platform fee on transactions  
**So that** the platform is sustainable

**Acceptance Criteria:**
- Platform fee (10%) calculated on each order
- Fee clearly displayed in order summary
- Fee collected during payment
- Fee tracked in analytics

**Status:** ✅ Implemented

---

### US-7.3: Funding Requests 🚧
**As a** farmer  
**I want to** request funding for my farm  
**So that** I can grow my business

**Acceptance Criteria:**
- Farmer can create funding request with details
- Request shows amount needed, purpose, timeline
- Buyers can contribute to funding requests
- Progress tracked and displayed
- Notifications sent when funded

**Status:** 🚧 Partially Implemented

---

## 8. Analytics & Reporting

### US-8.1: Admin Analytics Dashboard ✅
**As an** admin  
**I want** comprehensive analytics  
**So that** I can monitor platform health

**Acceptance Criteria:**
- Total users, products, orders displayed
- Revenue metrics calculated
- Growth trends visualized
- Top performers highlighted
- Real-time data updates

**Status:** ✅ Implemented

---

### US-8.2: Farmer Performance Metrics ✅
**As a** farmer  
**I want to** see my sales performance  
**So that** I can optimize my business

**Acceptance Criteria:**
- Total sales and revenue displayed
- Best-selling products identified
- Order fulfillment rate calculated
- Customer feedback aggregated
- Trends over time visualized

**Status:** ✅ Implemented

---

### US-8.3: Buyer Purchase History ✅
**As a** buyer  
**I want to** view my purchase analytics  
**So that** I can track my spending

**Acceptance Criteria:**
- Total orders and spending displayed
- Favorite products identified
- Purchase frequency calculated
- Spending trends visualized
- Export capability for records

**Status:** ✅ Implemented

---

## 9. Security & Privacy

### US-9.1: Data Encryption ✅
**As a** user  
**I want** my data to be encrypted  
**So that** my information is secure

**Acceptance Criteria:**
- Passwords hashed with bcrypt
- JWT tokens signed and verified
- HTTPS enforced in production
- Sensitive data encrypted at rest
- Secure headers implemented

**Status:** ✅ Implemented

---

### US-9.2: GDPR Compliance ✅
**As a** user  
**I want** my privacy rights respected  
**So that** I have control over my data

**Acceptance Criteria:**
- User can request data export
- User can request data deletion
- Privacy policy available
- Cookie consent implemented
- Data processing logged

**Status:** ✅ Implemented

---

### US-9.3: Rate Limiting ✅
**As a** platform operator  
**I want** rate limiting on API endpoints  
**So that** the platform is protected from abuse

**Acceptance Criteria:**
- Rate limits enforced per IP/user
- Different limits for different endpoints
- 429 error returned when limit exceeded
- Redis used for distributed rate limiting
- Admin endpoints have stricter limits

**Status:** ✅ Implemented

---

### US-9.4: Security Monitoring ✅
**As a** security engineer  
**I want** security events monitored  
**So that** threats can be detected early

**Acceptance Criteria:**
- Failed login attempts tracked
- Suspicious activity logged
- Security alerts generated
- Audit trail maintained
- Incident response procedures documented

**Status:** ✅ Implemented

---

## 10. Mobile & PWA

### US-10.1: Progressive Web App ✅
**As a** mobile user  
**I want** the platform to work as a PWA  
**So that** I can install it on my device

**Acceptance Criteria:**
- Service worker registered
- Offline functionality available
- Install prompt displayed
- App manifest configured
- Icons and splash screens provided

**Status:** ✅ Implemented

---

### US-10.2: Responsive Design ✅
**As a** user  
**I want** the platform to work on any device  
**So that** I can access it anywhere

**Acceptance Criteria:**
- Mobile-first design approach
- Responsive layouts for all screen sizes
- Touch-friendly interface elements
- Optimized images for mobile
- Fast loading on slow connections

**Status:** ✅ Implemented

---

### US-10.3: Push Notifications ✅
**As a** user  
**I want** push notifications  
**So that** I stay updated on important events

**Acceptance Criteria:**
- User can enable push notifications
- Notifications sent for order updates
- Notifications sent for new messages
- User can manage notification preferences
- Notifications work on mobile and desktop

**Status:** ✅ Implemented

---

## 11. Future Features

### US-11.1: AI Recommendations 🔮
**As a** buyer  
**I want** personalized product recommendations  
**So that** I discover products I'll like

**Status:** 🔮 Planned

---

### US-11.2: Supply Chain Tracking 🔮
**As a** user  
**I want** complete supply chain transparency  
**So that** I can verify product origin and quality

**Status:** 🔮 Planned

---

### US-11.3: Blockchain Integration 🔮
**As a** user  
**I want** blockchain-based features  
**So that** I have transparency and decentralized options

**Status:** 🔮 Planned

---

### US-11.4: Multi-Language Support 🔮
**As an** international user  
**I want** the platform in my language  
**So that** I can use it comfortably

**Status:** 🔮 Planned

---

### US-11.5: Social Features 🔮
**As a** user  
**I want** to connect with other users  
**So that** I can share knowledge and build community

**Status:** 🔮 Planned

---

## Legend

- ✅ **Implemented** - Feature is complete and in production
- 🚧 **Partially Implemented** - Feature is partially complete
- 🔮 **Planned** - Feature is planned for future development
- ❌ **Not Started** - Feature has not been started

---

## Summary Statistics

- **Total User Stories:** 45
- **Implemented:** 38 (84%)
- **Partially Implemented:** 1 (2%)
- **Planned:** 6 (14%)

---

## Related Documents

- [Requirements Document](docs/project/requirements.md)
- [API Documentation](docs/api/)
- [Architecture Overview](docs/architecture/)
- [Deployment Guide](docs/deployment/)

---

**Last Updated:** November 20, 2025  
**Document Owner:** AgriDAO Development Team
