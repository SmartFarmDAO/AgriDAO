# New Features Quick Reference

**Last Updated:** November 27, 2025

Quick guide to the newly implemented features: Social Community, Supply Chain Tracking, and Blockchain Integration.

## 🌐 Social Features

### Access
- **URL:** `/community`
- **Role:** All authenticated users

### Features

#### Create Post
```
1. Navigate to /community
2. Type your message in the text area
3. Click "Post" button
4. Post appears at top of feed
```

#### Like Post
```
1. Click the ❤️ icon on any post
2. Like count increases
3. Click again to unlike
```

#### Comment on Post
```
1. Click 💬 icon to expand comments
2. Type your comment
3. Click "Comment" button
4. Comment appears in thread
```

### API Endpoints
```bash
# List posts
GET /social/posts?limit=20

# Create post
POST /social/posts
{
  "content": "Great harvest this season!",
  "image_url": "https://..."
}

# Get comments
GET /social/posts/{post_id}/comments

# Add comment
POST /social/posts/{post_id}/comments
{
  "content": "Congratulations!"
}

# Like post
POST /social/posts/{post_id}/like

# Unlike post
DELETE /social/posts/{post_id}/like
```

## 📦 Supply Chain Tracking

### Access
- **URL:** `/supply-chain`
- **Role:** All authenticated users

### Features

#### Track New Product
```
1. Navigate to /supply-chain
2. Click "Track New Product"
3. Fill in:
   - Product Name
   - Origin Location
   - Current Location
   - Notes (optional)
4. Click "Add Product"
```

#### View Tracking
```
1. Click on any product in the list
2. View tracking timeline on right panel
3. See origin → current location journey
4. Read notes and timestamps
```

#### Update Location
```
Use API to add tracking events:
POST /supplychain/assets/{asset_id}/track
{
  "location": "Distribution Center",
  "status": "In Transit",
  "notes": "Arrived at warehouse"
}
```

### API Endpoints
```bash
# List all tracked assets
GET /supplychain/assets

# Create new asset
POST /supplychain/assets
{
  "name": "Organic Tomatoes",
  "origin": "Farm A, District X",
  "current_location": "Farm A",
  "notes": "Harvested today"
}

# Get asset details
GET /supplychain/assets/{asset_id}

# Update asset
PUT /supplychain/assets/{asset_id}
{
  "current_location": "Market B"
}

# Add tracking event
POST /supplychain/assets/{asset_id}/track
{
  "asset_id": 1,
  "location": "Warehouse C",
  "status": "Stored",
  "notes": "Temperature controlled"
}
```

## ⛓️ Blockchain Integration

### Access
- **URL:** `/blockchain`
- **Role:** All authenticated users

### Features

#### View Transactions
```
1. Navigate to /blockchain
2. See transaction history
3. View transaction details:
   - From/To addresses
   - Amount
   - Hash
   - Status
   - Timestamp
```

#### Create Transaction
```
1. Click "New Transaction"
2. Enter:
   - Recipient Address
   - Amount
3. Click "Send Transaction"
4. Transaction appears with hash
5. Status updates to "confirmed"
```

#### View Statistics
```
Dashboard shows:
- Total Transactions
- Total Value
- Active Users
- Last Block Time
```

### API Endpoints
```bash
# Get transactions
GET /blockchain/transactions?limit=20

# Create transaction
POST /blockchain/transactions
{
  "type": "payment",
  "amount": 150.00,
  "from_address": "0x1234...5678",
  "to_address": "0xabcd...efgh"
}

# Get statistics
GET /blockchain/stats

# Get transaction by hash
GET /blockchain/transactions/{tx_hash}
```

### Transaction Hash
Each transaction gets a unique SHA-256 hash:
```
Example: 0xa3f5d8c2e1b4f7a9
```

## 🔗 Integration Examples

### Link Supply Chain to Blockchain
```python
# When product moves, record on blockchain
asset = create_asset(name="Tomatoes", origin="Farm A")
tx = create_transaction(
    type="provenance",
    amount=0,
    from_address=asset.origin,
    to_address=asset.current_location
)
```

### Social Post about Product
```python
# Farmer shares harvest update
post = create_post(
    content=f"Just harvested {product.name}! Track it: /supply-chain/assets/{asset.id}",
    image_url=product.images[0]
)
```

### Community Funding Request
```python
# Share funding request in community
funding = create_funding_request(...)
post = create_post(
    content=f"Need support for {funding.purpose}. Check /finance",
    image_url=funding.image
)
```

## 🎯 Use Cases

### For Farmers
1. **Social:** Share farming tips and success stories
2. **Supply Chain:** Track products from harvest to delivery
3. **Blockchain:** Transparent payment records

### For Buyers
1. **Social:** Ask questions and share recipes
2. **Supply Chain:** Verify product origin and freshness
3. **Blockchain:** Verify payment authenticity

### For Admins
1. **Social:** Monitor community health
2. **Supply Chain:** Audit product provenance
3. **Blockchain:** Track platform transactions

## 🚀 Quick Start Commands

### Start Backend
```bash
cd backend
docker-compose up
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Access Features
```
Community:      http://localhost:5173/community
Supply Chain:   http://localhost:5173/supply-chain
Blockchain:     http://localhost:5173/blockchain
```

## 📊 Testing

### Test Social Features
```bash
# Create test post
curl -X POST http://localhost:8000/social/posts \
  -H "Content-Type: application/json" \
  -d '{"content": "Test post"}'

# Like post
curl -X POST http://localhost:8000/social/posts/1/like
```

### Test Supply Chain
```bash
# Create asset
curl -X POST http://localhost:8000/supplychain/assets \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "origin": "Farm A",
    "current_location": "Farm A"
  }'
```

### Test Blockchain
```bash
# Create transaction
curl -X POST http://localhost:8000/blockchain/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "amount": 100,
    "from_address": "0x123",
    "to_address": "0xabc"
  }'
```

## 🔐 Security Notes

- All endpoints require authentication (except viewing)
- User IDs are tracked for all actions
- Blockchain hashes are cryptographically secure
- Supply chain updates are timestamped
- Social posts can be moderated by admins

## 📱 Mobile Support

All features are fully responsive:
- Touch-friendly interfaces
- Mobile-optimized layouts
- Fast loading on slow connections
- PWA support for offline access

## 🌍 Multi-Language

All new features support 4 languages:
- English
- Bengali (বাংলা)
- Spanish (Español)
- French (Français)

Use language switcher in header to change.

## 💡 Tips

1. **Social:** Post regularly to build community
2. **Supply Chain:** Update locations in real-time
3. **Blockchain:** Save transaction hashes for records
4. **Integration:** Link features together for best experience

## 🆘 Troubleshooting

### Posts not showing?
- Check authentication
- Refresh the page
- Verify backend is running

### Supply chain not updating?
- Check API endpoint
- Verify asset ID is correct
- Check network connection

### Blockchain transactions failing?
- Verify address format
- Check amount is positive
- Ensure backend is running

## 📚 Related Documentation

- [Social Features Implementation](../reports/SOCIAL_FEATURES_IMPLEMENTATION.md)
- [Supply Chain Implementation](../reports/SUPPLY_CHAIN_IMPLEMENTATION.md)
- [Blockchain Implementation](../reports/BLOCKCHAIN_IMPLEMENTATION.md)
- [100% Completion Report](../reports/PLATFORM_100_PERCENT_COMPLETE.md)

---

**Need Help?** Check the full documentation or contact the development team.
