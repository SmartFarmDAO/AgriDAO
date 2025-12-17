import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from .database import init_db
from .core.logging import CorrelationIdMiddleware, setup_logging
from .routers import health, farmers, marketplace, finance, ai, supplychain, governance, commerce, users, auth, cart, notifications, orders, disputes, analytics, admin, recommendations, social, blockchain, agents, dev_agents, cropvariety
from .middleware.security import (
    XSSProtectionMiddleware, 
    CSRFProtectionMiddleware, 
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    set_csrf_middleware
)
from .services.redis_service import redis_service
from .middleware.error_handlers import (
    validation_exception_handler,
    http_exception_handler,
    integrity_error_handler,
    general_exception_handler
)


# Ensure we load the .env at backend/.env even if CWD is project root
_here = os.path.dirname(__file__)
_backend_env = os.path.abspath(os.path.join(_here, "..", ".env"))
if os.path.exists(_backend_env):
    load_dotenv(_backend_env)
else:
    load_dotenv()

app = FastAPI(title="AgriDAO Backend", version="0.1.0")

# Setup structured logging
setup_logging(
    level=os.getenv("LOG_LEVEL", "INFO"),
    log_file=os.getenv("LOG_FILE")
)

# Correlation ID middleware (first to ensure correlation IDs are set)
app.add_middleware(CorrelationIdMiddleware)

# Security middleware
csrf_middleware = CSRFProtectionMiddleware(app)
set_csrf_middleware(csrf_middleware)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(XSSProtectionMiddleware)
app.add_middleware(CSRFProtectionMiddleware)

# CORS middleware (after security middleware)
cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    ",".join([
        # Production
        "http://54.251.65.124",
        "http://54.251.65.124:80",
        "https://54.251.65.124",
        # Vite defaults
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Common alternative dev port
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        # Backend itself (if calling from Swagger UI)
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ])
)

allow_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    await redis_service.connect()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_service.disconnect()


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
app.include_router(cart.router, prefix="/api", tags=["cart"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])

# Mount uploads directory for serving images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(orders.router, prefix="/api", tags=["orders"])
app.include_router(disputes.router, prefix="/api", tags=["disputes"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
app.include_router(social.router, prefix="/social", tags=["social"])
app.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
app.include_router(dev_agents.router, prefix="/api", tags=["development"])
app.include_router(cropvariety.router, prefix="/api/cropvariety", tags=["cropvariety"])


