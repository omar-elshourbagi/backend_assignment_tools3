"""FastAPI application entry point"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from mysql.connector import Error as MySQLError
from database import init_db
from routes import auth, health
from routes import events
from handlers.exceptions import EventPlannerException
from handlers.middleware import (
    exception_handler,
    eventplanner_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    mysql_exception_handler
)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="EventPlanner Phase 0 API",
    description="Event Planner API - No authentication required. Pass user_id as a query parameter.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add exception handlers
app.add_exception_handler(EventPlannerException, eventplanner_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(MySQLError, mysql_exception_handler)
app.add_exception_handler(Exception, exception_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(events.router)

if __name__ == "__main__":
    import uvicorn
    print("✓ Swagger UI available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
