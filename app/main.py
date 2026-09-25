from enum import Enum
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="JobTrack API",
    description="API for managing job applications",
    version="0.1.0"
)

class ApplicationStatus(str,Enum):
    interested = "interested"
    applied = "applied"
    interview = "interview"
    offer = "offer"
    rejected = "rejected"

class ApplicationCreate(BaseModel):
    company: str = Field(min_length=2, max_length=100)
    position: str = Field(min_length=2, max_length=100)
    country: Optional[str] = None
    status: ApplicationStatus = ApplicationStatus.interested
    job_url: Optional[str] = None
    notes: Optional[str] = None

class Application(ApplicationCreate):
    id: int

applications: list[Application] = []

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

@app.post(
    "/applications",
    response_model=Application,
    status_code=201
)
def create_application(application: ApplicationCreate):
    new_application = Application(
        id=len(applications) + 1,
        **application.model_dump()
    )

    applications.append(new_application)

    return new_application

@app.get(
    "/applications",
    response_model=list[Application]
)
def get_applications():
    return applications

@app.get(
    "/applications/{application_id}",
    response_model=Application
)
def get_application(application_id : int):
    for application in applications:
        if application.id == application_id :
            return application

    raise HTTPException(
        status_code=404,
        detail="Application not found"
    )

@app.put(
    "/applications/{application_id}",
    response_model=Application
)
def update_application (
    application_id : int,
    application_data : ApplicationCreate
):
    for index, application in enumerate(applications):
        if application.id == application_id :
            updated_application = Application(
                id = application_id,
                **application_data.model_dump()
            )

            applications[index] = updated_application

            return updated_application

    raise HTTPException(
        status_code=404,
        detail="Application not found"
    )

@app.delete(
    "/applications/{application_id}",
    status_code=204
)
def delete_application(application_id: int):

    for index, application in enumerate(applications):

        if application.id == application_id:
            applications.pop(index)
            return

    raise HTTPException(
        status_code=404,
        detail="Application not found"
    )