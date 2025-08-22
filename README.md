<div align="center">
<h1>AgriDAO – Ethical AgriFinance & Marketplace</h1>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)](https://nodejs.org/)
</div>

## Project info

AgriDAO is a decentralized platform connecting farmers with ethical lenders and buyers through a transparent marketplace and financing system.

## Features

- 🌱 **Marketplace**: Buy and sell farm products directly
- 💰 **Finance**: Support farmers through donations and investments
- 📊 **Transparency**: Track funding impact with real-time metrics
- 🚜 **Farmer Onboarding**: Easy profile and listing management

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- Docker (optional, for containerized development)

### Frontend Development

```sh
# Install dependencies
npm install

# Start development server
npm run dev
```

## Backend (FastAPI)

The backend lives in `backend/` and provides authentication, marketplace, governance and finance KPIs.

Quick start (local Python):

```sh
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Using Docker Compose (frontend + backend):

```sh
docker compose up --build
```

API base URL (local): `http://localhost:8000`

Key endpoints:

- GET `/marketplace/products` – list products
- GET `/finance/requests` – list funding requests
- POST `/finance/requests/{id}/donate` – donate to a request
- GET `/finance/metrics` – finance KPIs (GMV, fee revenue, orders, take rate)

## Environment Variables

Copy `.env.example` to `.env` and set values as needed. Notable variables:

- `VITE_API_BASE` – frontend API base (e.g., http://localhost:8000)
- `VITE_PLATFORM_FEE_RATE` – platform fee rate (e.g., 0.08)

Backend-specific variables are documented in `backend/README.md`.

## Mobile App (Experimental)

```sh
cd mobile
npm install
npm start  # Requires Expo CLI
```

## What technologies are used for this project?

This project is built with:

- Vite, TypeScript, React, shadcn-ui, Tailwind CSS (web)
- FastAPI, SQLModel, SQLite (backend)
- Docker Compose (dev orchestration)
  
## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Project Link: [https://github.com/yourusername/agridao](https://github.com/yourusername/agridao)
