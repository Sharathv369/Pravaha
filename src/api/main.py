"""Main FastAPI application entry point for the PRAVAHA API."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import config
from src.api.routers import health, stations, validation

# Initialize FastAPI application
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description=config.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS Middleware for Frontend Development
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# Register Sub-Routers
app.include_router(health.router)
app.include_router(stations.router)
app.include_router(validation.router)


# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Format Pydantic request validation errors cleanly."""
    errors = exc.errors()
    first_msg = errors[0].get("msg") if errors else "Invalid request parameters."
    loc = " -> ".join(str(l) for l in errors[0].get("loc", [])) if errors else "parameter"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": f"Validation error at {loc}: {first_msg}",
            "errors": errors,
        },
    )


@app.get(
    "/",
    tags=["Root"],
    summary="API Root Information & Sitemap",
    description="Returns basic platform metadata, current version, and links to interactive OpenAPI documentation.",
)
def root():
    """Welcome root endpoint pointing to Swagger docs and health probe."""
    return {
        "title": config.API_TITLE,
        "version": config.API_VERSION,
        "description": config.API_DESCRIPTION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_probe": "/health",
        "endpoints": [
            "/health",
            "/api/stations",
            "/api/stations/{station_id}",
            "/api/stations/{station_id}/hydrograph",
            "/api/stations/{station_id}/catchment-profile",
            "/api/validation/leaderboard",
            "/api/validation/river-systems",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)

