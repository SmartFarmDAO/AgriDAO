# AgriDAO – Ethical AgriFinance & Marketplace

## Project info

**URL**: https://lovable.dev/projects/4cea5b43-1506-4833-ac6a-023d157af440

## How can I edit this code?

There are several ways of editing your application.

**Use Lovable**

Simply visit the [Lovable Project](https://lovable.dev/projects/4cea5b43-1506-4833-ac6a-023d157af440) and start prompting.

Changes made via Lovable will be committed automatically to this repo.

**Use your preferred IDE**

If you want to work locally using your own IDE, you can clone this repo and push changes. Pushed changes will also be reflected in Lovable.

The only requirement is having Node.js & npm installed - [install with nvm](https://github.com/nvm-sh/nvm#installing-and-updating)

Follow these steps:

```sh
# Step 1: Clone the repository using the project's Git URL.
git clone <YOUR_GIT_URL>

# Step 2: Navigate to the project directory.
cd <YOUR_PROJECT_NAME>

# Step 3: Install the necessary dependencies.
npm i

# Step 4: Start the development server with auto-reloading and an instant preview.
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

Backend-specific variables are documented in `backend/README.md` and `backend/pyproject.toml`/`requirements.txt`.

## Mobile App (optional)

An experimental mobile client lives in `mobile/`. You can open it with Expo tooling if desired.

**Edit a file directly in GitHub**

- Navigate to the desired file(s).
- Click the "Edit" button (pencil icon) at the top right of the file view.
- Make your changes and commit the changes.

**Use GitHub Codespaces**

- Navigate to the main page of your repository.
- Click on the "Code" button (green button) near the top right.
- Select the "Codespaces" tab.
- Click on "New codespace" to launch a new Codespace environment.
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite, TypeScript, React, shadcn-ui, Tailwind CSS (web)
- FastAPI, SQLModel, SQLite (backend)
- Docker Compose (dev orchestration)

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/4cea5b43-1506-4833-ac6a-023d157af440) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/tips-tricks/custom-domain#step-by-step-guide)
