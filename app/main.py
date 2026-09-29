from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import applications


app = FastAPI(
    title="JobTrack API",
    description="API for managing job applications",
    version="0.1.0"
)


Base.metadata.create_all(bind=engine)


app.include_router(applications.router)


@app.get("/")
def root():
    return {
        "message": "JobTrack API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }