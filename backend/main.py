"""
main.py
───────
CarbonCalc FastAPI application entry point.

Responsibilities:
    1. Create the FastAPI application instance with full OpenAPI metadata
    2. Register the lifespan context — runs init_db() before the first request
    3. Mount all API routers
    4. Expose the root health-check endpoint

Lifespan (startup / shutdown):
    FastAPI's lifespan replaces the deprecated @app.on_event("startup").
    Code before `yield` runs on startup; code after runs on shutdown.
    init_db() is called here so tables are always created/verified before
    any HTTP request is processed.

Router mounting strategy:
    All routers use the /api/v1 prefix. This gives a clean versioning path:
    when breaking changes are needed, /api/v2 routers are added alongside
    /api/v1 with no disruption to existing clients (the Next.js frontend,
    mobile apps, or third-party integrations).

Future routers to mount here (do NOT add until their phase is complete):
    - app.api.auth        → POST /api/v1/auth/login, /refresh  (Phase 2)
    - app.api.emissions   → CRUD for emission records            (Phase 3)
    - app.api.recommendations → GET recommendations             (Phase 4)
    - app.api.agents      → LangGraph agent trigger endpoints    (Phase 5)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.users import router as users_router
from app.api.emissions import router as emissions_router
from app.api.simulator import router as simulator_router
from app.api.recommendations import router as recommendations_router
from app.api.copilot import router as copilot_router
from app.api.auth import router as auth_router
from app.api.reports import router as reports_router
from app.database.init_db import init_db


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup  (before yield): Initialise the database — creates all tables
                              registered in Base.metadata if they don't exist.
    Shutdown (after yield):  Currently a no-op. Future: gracefully close
                              async DB pools, LangGraph agent connections, etc.
    """
    # -- Startup
    print("[startup] CarbonCalc API starting up...")
    init_db()
    print("[startup] Ready to accept requests")

    yield  # Application runs here

    # -- Shutdown
    print("[shutdown] CarbonCalc API shutting down...")


# ── OpenAPI Tag Metadata ──────────────────────────────────────────────────────
# These descriptions appear in the Swagger UI tag sections.
tags_metadata = [
    {
        "name": "Users",
        "description": (
            "User account management. "
            "Register new users and retrieve account information. "
            "Passwords are hashed with bcrypt — plaintext is never stored."
        ),
    },
    {
        "name": "Emissions",
        "description": "Carbon emission records tracking and analytics.",
    },
    {
        "name": "Health",
        "description": "Service health and status checks.",
    },
]


# ── Application Instance ──────────────────────────────────────────────────────
app = FastAPI(
    title="CarbonCalc API",
    description=(
        "## CarbonCalc — AI-Powered Sustainability Footprint Platform\n\n"
        "Backend API for tracking, analysing, and reducing carbon emissions "
        "using AI agents, ML models, and a digital twin simulation engine.\n\n"
        "**Current Phase:** Backend Foundation — User Management\n\n"
        "**Stack:** FastAPI · PostgreSQL · SQLAlchemy · Pydantic v2"
    ),
    version="0.1.0",
    contact={
        "name": "CarbonCalc Team",
    },
    license_info={
        "name": "Private — All rights reserved",
    },
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


# ── CORS Middleware ───────────────────────────────────────────────────────────
# Allow the Next.js dev server (port 3000) to call this API during development.
# In production, replace ["*"] with the exact Vercel deployment domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js dev server
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────────────────────
# Include API routers
app.include_router(
    users_router,
    prefix="/api/v1",
)

app.include_router(
    emissions_router,
    prefix="/api/v1",
)

app.include_router(
    simulator_router,
    prefix="/api/v1",
)

app.include_router(
    recommendations_router,
    prefix="/api/v1",
)

app.include_router(
    copilot_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    reports_router,
    prefix="/api/v1",
)


# ── Root Health Check ─────────────────────────────────────────────────────────
@app.get(
    "/",
    tags=["Health"],
    summary="Root health check",
    description="Returns the service name and version. Use /api/v1/... for all resources.",
)
def root() -> dict:
    """
    Lightweight health check endpoint.
    Load balancers and uptime monitors hit this route to verify the service is up.
    No database call is made — this must always respond, even if the DB is down.
    """
    return {
        "service": "CarbonCalc API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }