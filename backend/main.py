from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import Base, engine
from backend.routes.complaint_routes import router as complaint_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CivicMind AI",
    description="AI-powered smart governance complaint system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(
    complaint_router,
    prefix="/api/complaints",
    tags=["Complaints"]
)

@app.get("/")
def root():
    return {
        "message": "CivicMind AI Backend Running",
        "status": "success"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }