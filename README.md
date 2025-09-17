# AgriDAO - Decentralized Agricultural Marketplace

A comprehensive blockchain-enabled agricultural marketplace connecting farmers directly with consumers, restaurants, and retailers through smart contracts and decentralized governance.

## 🌾 Project Overview

AgriDAO is a modern agricultural marketplace built with React, TypeScript, and blockchain integration. It enables:
- **Direct Farmer-to-Consumer Sales** - Eliminate intermediaries
- **Smart Contract Escrow** - Secure transaction processing
- **Real-time Market Data** - Live pricing and inventory
- **Mobile-First Design** - Optimized for rural connectivity
- **Offline Capabilities** - Continue working without internet
- **Push Notifications** - Real-time updates on mobile

## 🚀 Features

### Core Marketplace
- **Product Listings** with rich media support
- **Advanced Search & Filtering** by location, category, price, certifications
- **Shopping Cart** with persistent storage
- **Multi-vendor Support** - Compare prices across farmers
- **Rating & Review System** - Build trust through transparency

### Smart Contract Integration
- **Automated Escrow** - Funds held securely until delivery
- **Dispute Resolution** - Decentralized governance for conflicts
- **Reputation System** - Blockchain-verified farmer ratings
- **Token Rewards** - Earn tokens for platform participation

### Mobile & Offline Capabilities
- **Progressive Web App (PWA)** - Install on mobile devices
- **Offline Mode** - Browse and add to cart without internet
- **Push Notifications** - Real-time order updates
- **Touch-Optimized Interface** - Swipe gestures and mobile navigation

### Advanced Features
- **Multi-language Support** - English, Spanish, Hindi, and more
- **Weather Integration** - Crop recommendations based on local weather
- **Logistics Integration** - Shipping and delivery tracking
- **Analytics Dashboard** - Sales insights and market trends
- **API Integration** - Connect with existing farm management systems

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **Tailwind CSS** for responsive styling
- **Zustand** for state management
- **React Query** for data fetching and caching
- **React Hook Form** for form handling
- **Framer Motion** for animations

### Backend
- **FastAPI** (Python) for RESTful APIs
- **PostgreSQL** for primary data storage
- **Redis** for caching and sessions
- **Firebase** for push notifications
- **Cloud Storage** (AWS S3/GCP/Azure) for file storage

### Testing
- **Playwright** for E2E testing
- **Vitest** for unit testing
- **Artillery** for load testing
- **Security testing** with OWASP compliance

### Mobile & PWA
- **Progressive Web App** with service workers
- **Offline-first architecture**
- **Push notification support**
- **Touch gesture handling**
- **Responsive design** for all screen sizes

## 📱 Mobile Optimization

### Responsive Design
- **Mobile-first approach** with breakpoints at 320px, 768px, 1024px
- **Touch-friendly UI** with 44px minimum touch targets
- **Swipe gestures** for navigation and actions
- **Optimized images** with WebP and responsive sizing

### Performance
- **Lazy loading** for images and components
- **Code splitting** for faster initial loads
- **Service worker** for offline functionality
- **Background sync** for pending actions

### Offline Features
- **Local storage** for cart and user preferences
- **Background sync** for orders and updates
- **Offline browsing** of previously viewed products
- **Queue management** for actions performed offline

## 🧪 Testing

### Comprehensive Test Suite
- **E2E Tests**: Complete user journey testing
- **Security Tests**: OWASP Top 10 compliance
- **Performance Tests**: Load testing with 1000+ concurrent users
- **Mobile Tests**: Cross-device compatibility
- **Accessibility Tests**: WCAG 2.1 compliance

### Test Commands
```bash
# Run all tests
npm test

# E2E tests
npm run test:e2e

# Performance tests
npm run test:performance

# Security tests
npm run test:security

# Load tests
npm run test:load
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and npm
- PostgreSQL 14+
- Redis 6+
- Firebase project for notifications

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/agridao.git
cd agridao
```

2. **Install dependencies**
```bash
npm install
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start development server**
```bash
npm run dev
```

5. **Run tests**
```bash
npm run test:e2e
```

### Environment Variables

#### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-firebase-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=your-app-id
```

#### Backend Configuration
See backend documentation for database and API setup.

## 📁 Project Structure

```
AgriDAO/
├── src/
│   ├── components/          # Reusable UI components
│   ├── pages/              # Route-based pages
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── stores/             # Zustand state stores
│   ├── types/              # TypeScript definitions
│   └── styles/             # Global styles
├── e2e/                    # End-to-end tests
├── public/                 # Static assets
├── tests/                  # Unit tests
└── docs/                   # Documentation
```

## 🎯 Key Components

### Core Components
- **ProductCard**: Display product information
- **SearchFilter**: Advanced filtering interface
- **ShoppingCart**: Persistent cart management
- **OrderTracking**: Real-time order status
- **UserProfile**: Farmer and buyer profiles
- **NotificationCenter**: Push notification UI

### Mobile Components
- **MobileNavigation**: Bottom tab navigation
- **SwipeActions**: Touch gesture handlers
- **OfflineStatus**: Connectivity indicators
- **TouchOptimized**: Mobile-friendly inputs

## 🔧 Development

### Available Scripts
```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm test            # Run all tests
npm run test:e2e    # Run E2E tests
npm run test:ui     # Run tests with UI

# Code quality
npm run lint        # Run ESLint
npm run format      # Format with Prettier
npm run typecheck   # Type checking
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Run the test suite
6. Submit a pull request

## 📊 Performance Benchmarks

### Core Web Vitals
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **TTI (Time to Interactive)**: < 3.5s

### Mobile Performance
- **First Contentful Paint**: < 1.8s (3G)
- **Speed Index**: < 3.4s (3G)
- **Estimated Input Latency**: < 50ms

## 🔐 Security Features

- **OWASP Top 10** compliance
- **Input validation** and sanitization
- **Rate limiting** on all endpoints
- **HTTPS enforcement**
- **Content Security Policy (CSP)**
- **Secure authentication** with JWT tokens

## 📱 PWA Configuration

### Manifest
- **Name**: AgriDAO Marketplace
- **Short Name**: AgriDAO
- **Description**: Decentralized agricultural marketplace
- **Theme Color**: #22c55e
- **Background Color**: #ffffff
- **Display**: standalone
- **Icons**: Multiple sizes for different devices

### Service Worker Features
- **Offline caching** for static assets
- **Background sync** for pending actions
- **Push notification** handling
- **Cache-first strategy** for images
- **Network-first strategy** for API calls

## 🌐 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **Mobile browsers**: iOS Safari 14+, Chrome Mobile 90+

## 📞 Support

- **Documentation**: [docs.agridao.com](https://docs.agridao.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/agridao/issues)
- **Discord**: [AgriDAO Community](https://discord.gg/agridao)
- **Email**: support@agridao.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Farmers** - For their invaluable feedback and testing
- **Open Source Community** - For the amazing tools and libraries
- **Web3 Community** - For blockchain integration guidance
- **Agricultural Organizations** - For domain expertise and partnerships

---

**Built with ❤️ for farmers worldwide**
