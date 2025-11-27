# Funding Feature Guide

## Overview

The AgriDAO Funding Feature provides interest-free, community-driven financing for farmers. This ethical financing model allows farmers to request funding for agricultural needs while enabling community members to support local agriculture.

## Features

### For Farmers

#### Creating a Funding Request

1. Navigate to **Finance** page from the dashboard
2. Click on **Request Funding** tab
3. Fill in the required information:
   - **Purpose**: Brief description of what you need funding for
   - **Amount Needed**: Total funding amount required (in USD)
   - **Description**: Detailed explanation of how funds will be used
   - **Category**: Select from Seeds & Supplies, Equipment, Infrastructure, Emergency, or Education
   - **Timeline**: Number of days to reach funding goal

4. Click **Submit Funding Request**

#### Tracking Your Request

- View real-time progress on the Browse Requests tab
- Receive notifications at funding milestones (25%, 50%, 75%, 100%)
- Monitor days remaining until deadline
- See list of contributors (if enabled)

### For Donors/Supporters

#### Making a Donation

1. Browse available funding requests on the **Finance** page
2. Select a request that aligns with your values
3. Choose a quick amount ($50, $100, $250, $500, $1000) or enter a custom amount
4. Click **Donate** to complete the contribution
5. Receive confirmation and impact updates

#### Tracking Impact

- View total contributions made
- See funded projects and their outcomes
- Access transparency reports
- Monitor community impact metrics

## Ethical Funding Principles

### Interest-Free
- No interest charges or hidden fees
- 100% of donations go to farmers
- Platform fee covers operational costs only

### Community-Driven
- Funded by fellow farmers and supporters
- Democratic approval process
- Local community prioritization

### Transparent
- All transactions recorded on blockchain
- Public funding progress tracking
- Regular impact reports

### Accountable
- Farmers provide progress updates
- Milestone-based fund release
- Community feedback mechanism

## API Endpoints

### List Funding Requests
```http
GET /finance/requests
```

**Response:**
```json
[
  {
    "id": 1,
    "farmer_name": "John Doe",
    "purpose": "Organic Seeds Purchase",
    "amount_needed": 2500.0,
    "amount_raised": 1250.0,
    "days_left": 15,
    "category": "Seeds & Supplies",
    "location": "California",
    "description": "Need funding for organic vegetable seeds...",
    "status": "Active",
    "created_at": "2025-01-15T10:00:00Z"
  }
]
```

### Create Funding Request
```http
POST /finance/requests
```

**Request Body:**
```json
{
  "farmer_name": "Jane Smith",
  "purpose": "Farm Equipment",
  "amount_needed": 5000.0,
  "days_left": 30,
  "category": "Equipment",
  "location": "Oregon",
  "description": "Need a new irrigation system..."
}
```

### Donate to Request
```http
POST /finance/requests/{request_id}/donate
```

**Request Body:**
```json
{
  "amount": 250.0
}
```

**Response:**
```json
{
  "id": 1,
  "amount_raised": 1500.0,
  "status": "Active"
}
```

### Get Finance Metrics
```http
GET /finance/metrics
```

**Response:**
```json
{
  "gmv": 125000.50,
  "fee_revenue": 12500.05,
  "orders_total": 450,
  "orders_paid": 425,
  "take_rate": 0.10
}
```

## Notification System

### Funding Milestones

Farmers receive automatic notifications when their funding request reaches:

- **25% funded**: "📈 25% Funded! Your funding request is making progress..."
- **50% funded**: "📈 50% Funded! You're halfway to your goal..."
- **75% funded**: "📈 75% Funded! Almost there..."
- **100% funded**: "🎉 Funding Goal Reached! Your request has been fully funded..."

### Email Notifications

- Funding request created
- Donation received
- Milestone reached
- Funding goal completed
- Progress update reminders

## Best Practices

### For Farmers

1. **Be Specific**: Clearly explain what you need and why
2. **Set Realistic Goals**: Request amounts that match actual needs
3. **Provide Updates**: Keep donors informed of progress
4. **Show Gratitude**: Thank your supporters
5. **Share Results**: Report on how funds were used

### For Donors

1. **Research Requests**: Read descriptions carefully
2. **Start Small**: Begin with smaller donations
3. **Diversify**: Support multiple farmers
4. **Stay Engaged**: Follow up on funded projects
5. **Share Stories**: Help spread awareness

## Security & Compliance

- All transactions are encrypted
- PCI DSS compliant payment processing
- Blockchain verification for transparency
- Regular security audits
- GDPR compliant data handling

## Troubleshooting

### Common Issues

**Q: My funding request isn't showing up**
- Check that all required fields are filled
- Verify your farmer profile is complete
- Contact support if issue persists

**Q: Donation failed**
- Verify payment method is valid
- Check internet connection
- Try a different amount
- Contact support with error message

**Q: How long until I receive funds?**
- Funds are released when goal is reached
- Processing takes 3-5 business days
- Milestone-based releases available for large amounts

## Support

For questions or issues:
- Email: support@agridao.com
- Documentation: https://docs.agridao.com
- Community Forum: https://forum.agridao.com

## Future Enhancements

- Recurring donations
- Matching fund campaigns
- Impact scoring system
- Video progress updates
- Multi-currency support
- Mobile app integration
