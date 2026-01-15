"""
FastAPI application entry point.
Initializes the application, creates database tables, and registers routes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import router
import uvicorn

# Create all database tables on startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title="Employee Management API",
    description="REST API for managing employee records with JWT authentication",
    version="1.0.0"
)

# Configure CORS (Cross-Origin Resource Sharing)
# This allows requests from different origins (important for frontend apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins explicitly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router)


@app.get("/", tags=["Health"])
def read_root():
    """
    Root endpoint - health check.
    Used to verify API is running.
    """
    return {
        "message": "Employee Management API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint.
    Returns 200 OK if API is operational.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    # Run the application with: python main.py
    # Or use: uvicorn main:app --reload
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
