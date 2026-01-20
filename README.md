# AgriDAO - Decentralized Agricultural Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](deployment/docker)
[![Node](https://img.shields.io/badge/node-20.x-green.svg)](https://nodejs.org)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://python.org)

> Empowering farmers through blockchain technology, AI-powered insights, and community support.

AgriDAO is Bangladesh's first decentralized agricultural platform that connects farmers directly with buyers, provides ethical financing, and leverages blockchain for transparent supply chain tracking.

## 🌟 Features

- **🛒 Direct Marketplace** - Connect farmers directly with buyers, eliminating middlemen
- **💰 Ethical Financing** - Interest-free funding through community donations and sponsorships
- **🤖 AI Advisory** - Real-time weather alerts, market insights, and yield predictions
- **📦 Supply Chain Tracking** - Blockchain-based transparency from farm to consumer
- **🗳️ DAO Governance** - Community-driven platform decisions and fund allocation
- **🌐 Multi-language Support** - Full Bengali and English translation
- **👥 Social Features** - Community posts, farmer profiles, and networking
- **📱 Mobile Ready** - Responsive design for all devices

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20.x
- Python 3.12+
- Git

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/AgriDAO.git
cd AgriDAO

# Copy environment file
cp .env.example .env

# Start services with Docker
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

For detailed setup instructions, see [Getting Started Guide](docs/getting-started/README.md).

## 📚 Documentation

### For Users
- [User Guide](docs/user-guide/README.md) - How to use the platform
- [Demo Guide](docs/guides/DEMO_GUIDE.md) - Quick demo walkthrough
- [FAQ](docs/user-guide/FAQ.md) - Frequently asked questions

### For Developers
- [Development Guide](docs/development/README.md) - Setup and development workflow
- [Architecture](docs/architecture/README.md) - System architecture and design
- [API Documentation](docs/api/README.md) - REST API reference
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

### For Deployment
- [Docker Deployment](docs/deployment/DOCKER_DEPLOYMENT.md) - Deploy with Docker
- [Lightsail Deployment](docs/deployment/LIGHTSAIL_DEPLOYMENT.md) - Deploy on AWS Lightsail
- [Quick Start](docs/deployment/QUICK_START.md) - Fast deployment guide

## 🏗️ Project Structure

```
AgriDAO/
├── backend/              # FastAPI backend application
│   ├── app/             # Application code
│   ├── tests/           # Backend tests
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend application
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   └── package.json    # Node dependencies
├── blockchain/          # Smart contracts and blockchain code
│   ├── contracts/      # Solidity contracts
│   ├── scripts/        # Deployment scripts
│   └── test/           # Contract tests
├── mobile/             # React Native mobile app
├── deployment/         # Deployment configurations
│   ├── docker/        # Docker configs
│   ├── lightsail/     # AWS Lightsail setup
│   └── scripts/       # Deployment scripts
├── docs/              # Documentation
└── scripts/           # Utility scripts
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: shadcn/ui + Tailwind CSS
- **State Management**: React Query + Context API
- **Blockchain**: ethers.js, RainbowKit, wagmi

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy
- **Authentication**: JWT

### Blockchain
- **Network**: Ethereum (Hardhat for development)
- **Smart Contracts**: Solidity
- **Tools**: Hardhat, ethers.js

### DevOps
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus (optional)
- **Reverse Proxy**: Nginx

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Smart contract tests
cd blockchain
npx hardhat test

# E2E tests
npm run test:e2e
```

## 📦 Deployment

### Docker (Recommended)

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d
```

### AWS Lightsail

```bash
# One-command setup
curl -fsSL https://raw.githubusercontent.com/yourusername/AgriDAO/main/deployment/lightsail/lightsail-setup.sh | bash
```

See [Deployment Documentation](docs/deployment/) for detailed instructions.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Project Lead**: [Your Name]
- **Backend Developer**: [Name]
- **Frontend Developer**: [Name]
- **Blockchain Developer**: [Name]

## 🙏 Acknowledgments

- Built for farmers in Bangladesh
- Inspired by the need for fair agricultural markets
- Powered by blockchain technology and community support

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/AgriDAO/issues)
- **Email**: support@agridao.com
- **Discord**: [Join our community](https://discord.gg/agridao)

## 🗺️ Roadmap

- [x] Core marketplace functionality
- [x] Blockchain integration
- [x] Multi-language support (English/Bengali)
- [x] AI-powered recommendations
- [x] Supply chain tracking
- [ ] Mobile app release
- [ ] Advanced analytics dashboard
- [ ] Integration with payment gateways
- [ ] Farmer training modules

## 📊 Project Status

- **Version**: 1.0.0
- **Status**: Active Development
- **Last Updated**: December 2024

---

Made with ❤️ for farmers in Bangladesh
