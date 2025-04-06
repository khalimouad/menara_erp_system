"""
Menara Framework - Main Application Entry Point
"""
import os
import importlib
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
import logging.config
import sys

import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from core.config import settings
from core.db import init_db, get_db
from core.logger import setup_logging
from core.module_loader import load_modules, get_module_manifest
from core.template import templates
from core_modules.core.redirects import redirect_manager
from core_modules.tenancy.src.db_manager import get_all_tenants
from core_modules.tenancy.middleware import TenantMiddleware

# Configure logging
setup_logging()
logger = logging.getLogger('menara')

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/api/docs" if settings.SHOW_API_DOCS else None,
    redoc_url="/api/redoc" if settings.SHOW_API_DOCS else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add tenant middleware
app.add_middleware(TenantMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory=Path("static")), name="static")

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

# Root endpoint
@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """
    Root endpoint that handles initial redirection
    """
    try:
        # Check if any tenants exist
        tenants = get_all_tenants(db)
        if not tenants:
            return RedirectResponse(url="/setup", status_code=303)
        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise

# Setup wizard routes
from core_modules.tenancy.controls.setup_controller import router as setup_router
app.include_router(setup_router, tags=["setup"])

# Remove duplicate login route registrations
# The routes are already included via the tenancy module

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "ok", "version": settings.VERSION}

# Test endpoint for debugging
@app.get("/test", response_class=HTMLResponse)
async def test_endpoint():
    """
    Simple test endpoint to verify the application is functioning.
    """
    return """
    <html>
        <head>
            <title>Test Endpoint</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .success { color: green; font-weight: bold; }
                h1 { color: #333; }
            </style>
        </head>
        <body>
            <h1>Menara ERP Test Endpoint</h1>
            <p class="success">✅ The application is running!</p>
            <p>This is a test endpoint to verify the application is functioning correctly.</p>
            <p>Current time: <span id="current-time"></span></p>
            
            <h2>Registered Routes</h2>
            <ul>
                {% for route in request.app.routes %}
                <li>
                    <strong>{{ route.path }}</strong> 
                    ({{ route.methods|join(', ') if route.methods else 'No methods' }})
                </li>
                {% endfor %}
            </ul>
            
            <script>
                document.getElementById('current-time').textContent = new Date().toLocaleString();
            </script>
        </body>
    </html>
    """

# Load all modules
@app.on_event("startup")
async def startup_event():
    """
    Load all modules on application startup.
    """
    try:
        # Create necessary directories if they don't exist
        os.makedirs("static", exist_ok=True)
        os.makedirs("core_modules", exist_ok=True)
        
        # Load core and custom modules
        load_modules(app)
        
        logger.info(f"Menara Framework v{settings.VERSION} started successfully")
        logger.info(f"Loaded modules: {', '.join(m['name'] for m in get_module_manifest())}")
    except Exception as e:
        logger.error(f"Error in startup event: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        uvicorn.run(
            "app:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            workers=settings.WORKERS
        )
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise