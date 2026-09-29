from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)

# Insert an application
@router.post(
    "/",
    response_model=schemas.ApplicationResponse,
    status_code=201
)
def create_application(
    application: schemas.ApplicationCreate,
    db: Session = Depends(get_db)
):
    new_application = models.Application(
        **application.model_dump()
    )

    db.add(new_application)
    db.commit()
    db.refresh(new_application)

    return new_application

# Get applications
@router.get(
    "/",
    response_model=list[schemas.ApplicationResponse]
)
def get_applications(
    db: Session = Depends(get_db)
):
    statement = select(models.Application).order_by(
        models.Application.id
    )

    applications = db.scalars(statement).all()

    return applications

# Get application by id
@router.get(
    "/{application_id}",
    response_model=schemas.ApplicationResponse
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = db.get(
        models.Application,
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    return application

# Update an applications
@router.put(
    "/{application_id}",
    response_model=schemas.ApplicationResponse
)
def update_application(
    application_id: int,
    application_data: schemas.ApplicationCreate,
    db: Session = Depends(get_db)
):
    application = db.get(
        models.Application,
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    for field, value in application_data.model_dump().items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application

# Delete an application
@router.delete(
    "/{application_id}",
    status_code=204
)
def delete_application(
    application_id: int,
    db: Session = Depends(get_db)
):
    application = db.get(
        models.Application,
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    db.delete(application)
    db.commit()

    return

@router.patch(
    "/{application_id}",
    response_model=schemas.ApplicationResponse
)
def patch_application(
    application_id: int,
    application_data: schemas.ApplicationUpdate,
    db: Session = Depends(get_db)
):
    application = db.get(
        models.Application,
        application_id
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    update_data = application_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(application, field, value)

    db.commit()
    db.refresh(application)

    return application