# Funding Feature - Quick Reference

## For Developers

### Backend API

```python
# List all funding requests
GET /finance/requests

# Create funding request
POST /finance/requests
{
  "farmer_name": "John Doe",
  "purpose": "Seeds",
  "amount_needed": 1000.0,
  "days_left": 30,
  "category": "Seeds & Supplies",
  "location": "California",
  "description": "Need organic seeds..."
}

# Donate to request
POST /finance/requests/{id}/donate
{
  "amount": 250.0
}

# Get finance metrics
GET /finance/metrics
```

### Frontend Usage

```typescript
import { createFundingRequest, donateToRequest, listFundingRequests } from "@/lib/api";

// Create request
const request = await createFundingRequest({
  purpose: "Equipment",
  amount_needed: 5000,
  description: "Need irrigation system",
  category: "Equipment",
  days_left: 45
});

// Make donation
const updated = await donateToRequest(requestId, 250);

// List requests
const requests = await listFundingRequests();
```

### Database Model

```python
class FundingRequest(SQLModel, table=True):
    id: Optional[int]
    farmer_name: str
    purpose: str
    amount_needed: float
    amount_raised: float = 0.0
    days_left: int
    category: Optional[str]
    location: Optional[str]
    description: Optional[str]
    status: Optional[str]
    created_at: datetime
```

### Notification Milestones

```python
milestones = [25, 50, 75, 100]  # Percentage thresholds

# Notifications sent at:
# 25% - "📈 25% Funded!"
# 50% - "📈 50% Funded!"
# 75% - "📈 75% Funded!"
# 100% - "🎉 Funding Goal Reached!" + status = "Funded"
```

## For Users

### Creating a Request (Farmers)

1. Go to **Finance** page
2. Click **Request Funding** tab
3. Fill in:
   - Purpose (what you need)
   - Amount (in USD)
   - Description (detailed explanation)
   - Category (dropdown)
   - Timeline (days)
4. Click **Submit**

### Making a Donation (Supporters)

1. Go to **Finance** page
2. Browse requests
3. Click quick amount or enter custom
4. Click **Donate**
5. Confirm payment

### Categories

- Seeds & Supplies
- Equipment
- Infrastructure
- Emergency
- Education

## Testing

```bash
# Run funding tests
cd backend
pytest tests/test_funding.py -v

# Test specific function
pytest tests/test_funding.py::test_create_funding_request -v
```

## Common Issues

**Q: Donation fails**
- Check amount is positive
- Verify request exists
- Check authentication

**Q: Request not showing**
- Verify all required fields
- Check farmer profile exists
- Refresh page

**Q: Notifications not received**
- Check notification settings
- Verify email is correct
- Check spam folder

## Quick Commands

```bash
# Check funding requests in DB
docker exec -it agridao-db psql -U postgres -d agridb -c "SELECT * FROM fundingrequest;"

# Check recent donations
docker exec -it agridao-db psql -U postgres -d agridb -c "SELECT id, purpose, amount_raised, amount_needed FROM fundingrequest ORDER BY created_at DESC LIMIT 10;"

# Reset test data
docker exec -it agridao-db psql -U postgres -d agridb -c "DELETE FROM fundingrequest WHERE farmer_name LIKE 'Test%';"
```

## Links

- [Full Documentation](./funding-feature.md)
- [API Reference](../api/README.md)
- [User Stories](../project/userstory.md)
- [Implementation Report](../reports/FUNDING_FEATURE_IMPLEMENTATION.md)
