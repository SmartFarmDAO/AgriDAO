# AgriDAO API Documentation

Welcome to the AgriDAO API! This RESTful API allows you to integrate with the AgriDAO platform programmatically.

## 🚀 Getting Started

### Base URL
```
Production:  https://api.agridao.com/v1
Staging:     https://staging-api.agridao.com/v1
Development: http://localhost:8000/v1
```

### Quick Start
```bash
# Get your API key from the dashboard
export AGRIDAO_API_KEY="your_api_key_here"

# Make your first request
curl -H "Authorization: Bearer $AGRIDAO_API_KEY" \
     https://api.agridao.com/v1/products
```

## 🔐 Authentication

AgriDAO uses JWT-based authentication. See our [Authentication Guide](./authentication.md) for detailed instructions.

### Authentication Methods
- **JWT Tokens** - For user-authenticated requests
- **API Keys** - For server-to-server integration
- **OAuth 2.0** - For third-party applications

## 📚 API Reference

### Core Endpoints

#### Products
- `GET /products` - List all products
- `GET /products/{id}` - Get product details
- `POST /products` - Create a new product (farmers only)
- `PUT /products/{id}` - Update product (farmers only)
- `DELETE /products/{id}` - Delete product (farmers only)

#### Orders
- `GET /orders` - List user's orders
- `GET /orders/{id}` - Get order details
- `POST /orders` - Create a new order
- `PUT /orders/{id}` - Update order status
- `POST /orders/{id}/cancel` - Cancel an order

#### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `GET /users/{id}` - Get public user profile

### Detailed Documentation
- **[Endpoints Reference](./endpoints.md)** - Complete endpoint documentation
- **[Authentication](./authentication.md)** - Security and authentication
- **[Webhooks](./webhooks.md)** - Real-time event notifications
- **[Rate Limiting](./rate-limiting.md)** - Usage limits and best practices
- **[Error Handling](./error-handling.md)** - Error codes and troubleshooting

## 🔧 SDKs and Tools

### Official SDKs
- **JavaScript/Node.js** - [agridao-js](https://npm.im/@agridao/sdk)
- **Python** - [agridao-python](https://pypi.org/project/agridao/)
- **Go** - [agridao-go](https://github.com/agridao/go-sdk)
- **PHP** - [agridao-php](https://packagist.org/packages/agridao/sdk)

### Tools
- **[Postman Collection](./postman-collection.json)** - Import API endpoints
- **[OpenAPI Spec](./openapi.yaml)** - API specification file
- **[Insomnia Collection](./insomnia.json)** - Alternative API client

## 📋 Examples

### Common Use Cases
- **[Basic Integration](./examples/basic-integration.md)** - Getting started examples
- **[E-commerce Integration](./examples/ecommerce.md)** - Integrate with existing stores
- **[Mobile App Integration](./examples/mobile.md)** - Building mobile apps
- **[Analytics Integration](./examples/analytics.md)** - Tracking and reporting

### Code Examples
```javascript
// JavaScript SDK example
import { AgriDAO } from '@agridao/sdk';

const client = new AgriDAO({
  apiKey: 'your_api_key',
  environment: 'production' // or 'staging', 'development'
});

// Get products
const products = await client.products.list({
  category: 'vegetables',
  limit: 10
});

// Create an order
const order = await client.orders.create({
  items: [
    { productId: '123', quantity: 2 },
    { productId: '456', quantity: 1 }
  ],
  shippingAddress: {
    street: '123 Farm Road',
    city: 'Farmville',
    state: 'CA',
    zipCode: '90210'
  }
});
```

## 🚨 Important Notes

### Rate Limits
- **Free Tier**: 100 requests per hour
- **Pro Tier**: 1,000 requests per hour
- **Enterprise**: Custom limits

### Versioning
- Current version: **v1**
- All endpoints are versioned
- Breaking changes will result in new versions
- Deprecated versions supported for 12 months

### Support
- 📖 **Documentation**: This guide and [GitHub Wiki](https://github.com/SmartFarmDAO/AgriDAO/wiki)
- 💬 **Developer Discord**: [#api-support channel](https://discord.gg/agridao)
- 📧 **Email Support**: [api-support@agridao.com](mailto:api-support@agridao.com)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/SmartFarmDAO/AgriDAO/issues)

### Status Page
Monitor API status and uptime: [https://status.agridao.com](https://status.agridao.com)

---

**Ready to build?** Start with our [Quick Start Guide](./quick-start.md) or explore the [complete endpoint reference](./endpoints.md)!