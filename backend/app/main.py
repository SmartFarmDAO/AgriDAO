import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import health, farmers, marketplace, finance, ai, supplychain, governance, commerce, users, auth


load_dotenv()

app = FastAPI(title="AgriDAO Backend", version="0.1.0")

cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,"  # Vite default port
    "http://localhost:3000,http://127.0.0.1:3000,"  # Create React App default
    "http://localhost:8000,http://127.0.0.1:8000"   # Common backend port
)

allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health.router)
app.include_router(farmers.router, prefix="/farmers", tags=["farmers"])
app.include_router(marketplace.router, prefix="/marketplace", tags=["marketplace"])
app.include_router(finance.router, prefix="/finance", tags=["finance"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(supplychain.router, prefix="/supplychain", tags=["supplychain"])
app.include_router(governance.router, prefix="/governance", tags=["governance"])
app.include_router(commerce.router, prefix="/commerce", tags=["commerce"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


