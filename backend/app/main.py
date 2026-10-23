"""
HomeFlow AI - FastAPI Application Entrypoint.
Connects REST endpoints, CORS policies, SQLite startup lifecycle, and MCP integration.
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

# Ensure parent directory is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import init_db
from app.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes SQLite database and seeds initial demo records."""
    init_db(seed=True)
    yield


app = FastAPI(
    title="HomeFlow AI - Household Coordination Assistant API",
    description="Unified AI assistant for household tasks, reminders, routines, and simulated entry events.",
    version="1.0.0-hackathon",
    lifespan=lifespan,
)

# CORS configuration for local React / Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount REST routes
app.include_router(router)


@app.get("/", tags=["Root"])
def root():
    return {
        "app": "HomeFlow AI",
        "tagline": "Intelligent Household Coordination Assistant",
        "documentation": "/docs",
        "health": "/api/health",
        "mcp_tools": "/api/mcp/tools",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True)
