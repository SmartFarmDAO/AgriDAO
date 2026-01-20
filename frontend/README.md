# AgriDAO Frontend

React 18 + TypeScript + Vite frontend application for AgriDAO marketplace.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm test` - Run unit tests
- `npm run test:e2e` - Run E2E tests
- `npm run lint` - Run ESLint
- `npm run typecheck` - Run TypeScript checks

## Tech Stack

- React 18
- TypeScript
- Vite 5
- Tailwind CSS 3
- Zustand (State Management)
- TanStack Query (Data Fetching)
- React Hook Form
- Framer Motion

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── pages/         # Page components
│   ├── hooks/         # Custom hooks
│   ├── lib/           # Utilities
│   ├── services/      # API services
│   └── config/        # Configuration
├── public/            # Static assets
├── e2e/              # E2E tests
└── index.html        # Entry HTML
```

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=your-key
VITE_FIREBASE_AUTH_DOMAIN=your-domain
VITE_FIREBASE_PROJECT_ID=your-project-id
```

## Development

The frontend runs on `http://localhost:5173` by default and proxies API requests to the backend.
