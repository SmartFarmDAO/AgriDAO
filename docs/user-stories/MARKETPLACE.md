# Marketplace User Stories

## Epic: AgriMarketplace - Direct Farmer-to-Consumer Platform

### User Story 1: Browse Products as Guest
**As a** visitor  
**I want to** browse available products without logging in  
**So that** I can see what's available before creating an account

**Acceptance Criteria:**
- [ ] Can view all active products on marketplace page
- [ ] Can see product name, price, quantity available, and category
- [ ] Can search products by name
- [ ] Can filter products by category
- [ ] Products show farmer information
- [ ] No authentication required for browsing

**Test Steps:**
1. Navigate to `/marketplace` without logging in
2. Verify products are displayed
3. Search for "tomato" - should filter results
4. Click on a product card - should show details

---

### User Story 2: Add Products to Cart
**As a** buyer  
**I want to** add products to my shopping cart  
**So that** I can purchase multiple items at once

**Acceptance Criteria:**
- [ ] Can add products to cart with quantity selector
- [ ] Cart persists in localStorage
- [ ] Cart shows total items count
- [ ] Can view cart contents in drawer/modal
- [ ] Can adjust quantities in cart
- [ ] Can remove items from cart
- [ ] Cart shows subtotal and platform fee

**Test Steps:**
1. Click "Add to Cart" on a product
2. Verify cart icon shows item count
3. Open cart drawer
4. Increase/decrease quantity
5. Remove an item
6. Refresh page - cart should persist

---

### User Story 3: Search and Filter Products
**As a** buyer  
**I want to** search and filter products  
**So that** I can quickly find what I need

**Acceptance Criteria:**
- [ ] Search bar filters products by name in real-time
- [ ] Can filter by category (Vegetables, Grains, Dairy & Eggs, etc.)
- [ ] Search is case-insensitive
- [ ] Shows "No products found" when search has no results
- [ ] Can clear search to show all products

**Test Steps:**
1. Type "rice" in search bar
2. Verify only rice products show
3. Select "Vegetables" category filter
4. Verify only vegetables show
5. Clear search - all products return

---

### User Story 4: Checkout Process
**As a** logged-in buyer  
**I want to** checkout and pay for my cart items  
**So that** I can complete my purchase

**Acceptance Criteria:**
- [ ] Must be logged in to checkout
- [ ] Redirects to login if not authenticated
- [ ] Shows order summary with all items
- [ ] Calculates platform fee (8-10%)
- [ ] Shows total amount
- [ ] Integrates with payment gateway (Stripe)
- [ ] Creates order record after successful payment

**Test Steps:**
1. Add items to cart
2. Click "Checkout"
3. If not logged in, should redirect to `/auth`
4. After login, proceed to checkout
5. Verify order summary is correct
6. Complete payment (test mode)
7. Verify order confirmation

---

### User Story 5: List Products as Farmer
**As a** farmer  
**I want to** list my products on the marketplace  
**So that** buyers can purchase directly from me

**Acceptance Criteria:**
- [ ] Must have farmer role
- [ ] Must complete farmer onboarding first
- [ ] Can create product with: name, description, category, price, quantity
- [ ] Can upload product images
- [ ] Can set min/max order quantities
- [ ] Can add harvest and expiry dates
- [ ] Product appears immediately on marketplace

**Test Steps:**
1. Login as farmer
2. Navigate to "Add Product" page
3. Fill in product details
4. Upload image
5. Submit form
6. Verify product appears in marketplace
7. Verify product shows farmer's name

---

### User Story 6: Manage Product Inventory
**As a** farmer  
**I want to** manage my product inventory  
**So that** I can update availability and pricing

**Acceptance Criteria:**
- [ ] Can view all my listed products
- [ ] Can edit product details
- [ ] Can update quantity available
- [ ] Can change price
- [ ] Can mark product as out of stock
- [ ] Can delete products
- [ ] Changes reflect immediately on marketplace

**Test Steps:**
1. Login as farmer
2. Go to "My Products" dashboard
3. Edit a product's price
4. Update quantity to 0
5. Verify product shows "Out of Stock" on marketplace
6. Delete a product
7. Verify it's removed from marketplace

---

### User Story 7: View Order History
**As a** buyer  
**I want to** view my past orders  
**So that** I can track purchases and reorder

**Acceptance Criteria:**
- [ ] Can view list of all orders
- [ ] Shows order date, items, total, and status
- [ ] Can view order details
- [ ] Can track order status (pending, confirmed, shipped, delivered)
- [ ] Can download invoice
- [ ] Can reorder from past orders

**Test Steps:**
1. Login as buyer
2. Navigate to "Orders" page
3. Verify past orders are listed
4. Click on an order
5. Verify order details are correct
6. Check order status
7. Click "Reorder" - items added to cart

---

### User Story 8: Receive and Fulfill Orders
**As a** farmer  
**I want to** receive and manage orders  
**So that** I can fulfill customer purchases

**Acceptance Criteria:**
- [ ] Receive notification when order placed
- [ ] Can view all orders for my products
- [ ] Can update order status
- [ ] Can mark orders as shipped
- [ ] Can add tracking information
- [ ] Can communicate with buyer
- [ ] Can view order analytics

**Test Steps:**
1. Login as farmer
2. Navigate to "Orders" dashboard
3. Verify new orders appear
4. Click on an order
5. Update status to "Confirmed"
6. Add tracking number
7. Mark as "Shipped"
8. Verify buyer sees updated status

---

### User Story 9: Rate and Review Products
**As a** buyer  
**I want to** rate and review products I've purchased  
**So that** I can help other buyers make informed decisions

**Acceptance Criteria:**
- [ ] Can only review purchased products
- [ ] Can rate 1-5 stars
- [ ] Can write text review
- [ ] Can upload photos with review
- [ ] Reviews appear on product page
- [ ] Can edit/delete my reviews
- [ ] Farmer can respond to reviews

**Test Steps:**
1. Login as buyer with completed order
2. Navigate to order history
3. Click "Write Review" on delivered order
4. Rate product 5 stars
5. Write review text
6. Upload photo
7. Submit review
8. Verify review appears on product page

---

### User Story 10: View Farmer Profile
**As a** buyer  
**I want to** view farmer profiles  
**So that** I can learn about the source of my food

**Acceptance Criteria:**
- [ ] Can click on farmer name to view profile
- [ ] Shows farm location on map
- [ ] Shows farm size and certifications
- [ ] Lists all products from this farmer
- [ ] Shows farmer rating and reviews
- [ ] Shows farming practices (organic, etc.)
- [ ] Can follow/favorite farmers

**Test Steps:**
1. Click on farmer name on product card
2. Verify farmer profile page loads
3. Check farm location is displayed
4. Verify all farmer's products are listed
5. Check certifications are shown
6. Click "Follow" button
7. Verify farmer added to favorites

---

## Technical Requirements

### API Endpoints Needed
- `GET /marketplace/products` - List all products ✅
- `POST /marketplace/products` - Create product (farmer only) ✅
- `GET /marketplace/products/{id}` - Get product details ✅
- `PUT /marketplace/products/{id}` - Update product (farmer only)
- `DELETE /marketplace/products/{id}` - Delete product (farmer only)
- `POST /cart/add` - Add to cart
- `GET /cart` - Get cart contents
- `POST /checkout` - Create checkout session
- `GET /orders` - List user orders
- `GET /orders/{id}` - Get order details
- `PUT /orders/{id}/status` - Update order status (farmer only)
- `POST /reviews` - Create review
- `GET /farmers/{id}` - Get farmer profile

### Database Tables Needed
- ✅ `product` - Product listings
- ✅ `farmer` - Farmer profiles
- ✅ `user` - User accounts
- ✅ `order` - Orders
- ✅ `orderitem` - Order line items
- ⚠️ `cart` - Shopping cart (using localStorage currently)
- ⚠️ `review` - Product reviews
- ⚠️ `farmer_certification` - Farmer certifications

### Frontend Components Needed
- ✅ `Marketplace.tsx` - Main marketplace page
- ⚠️ `ProductDetail.tsx` - Individual product page
- ⚠️ `AddProduct.tsx` - Farmer product creation form
- ⚠️ `MyProducts.tsx` - Farmer product management
- ⚠️ `Orders.tsx` - Order history
- ⚠️ `OrderDetail.tsx` - Order details page
- ⚠️ `FarmerProfile.tsx` - Farmer profile page
- ⚠️ `Checkout.tsx` - Checkout flow

---

## Testing Checklist

### Functional Testing
- [ ] Products load correctly on marketplace
- [ ] Search filters products in real-time
- [ ] Category filters work
- [ ] Add to cart functionality works
- [ ] Cart persists across page refreshes
- [ ] Quantity adjustments work in cart
- [ ] Remove from cart works
- [ ] Checkout requires authentication
- [ ] Payment integration works (test mode)
- [ ] Orders are created successfully
- [ ] Farmers can list products
- [ ] Farmers can edit their products
- [ ] Order status updates work
- [ ] Reviews can be submitted
- [ ] Farmer profiles display correctly

### Security Testing
- [ ] Non-farmers cannot create products
- [ ] Users can only edit their own products
- [ ] Authentication required for checkout
- [ ] Payment data is secure
- [ ] SQL injection prevention
- [ ] XSS prevention in product descriptions
- [ ] CSRF protection on forms

### Performance Testing
- [ ] Marketplace loads in < 2 seconds
- [ ] Search responds in < 500ms
- [ ] Cart operations are instant
- [ ] Image loading is optimized
- [ ] Pagination for large product lists
- [ ] Database queries are optimized

### Mobile Testing
- [ ] Responsive design on mobile
- [ ] Touch-friendly cart controls
- [ ] Mobile checkout flow works
- [ ] Images display correctly on mobile
- [ ] Search works on mobile keyboards

---

## Current Status

✅ **Completed:**
- Product listing API
- Marketplace frontend with search
- Shopping cart (localStorage)
- Sample products added
- Basic authentication

⚠️ **In Progress:**
- Checkout flow
- Order management
- Product creation UI for farmers

❌ **Not Started:**
- Reviews and ratings
- Farmer profiles
- Product images upload
- Payment integration
- Order tracking
- Notifications
