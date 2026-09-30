from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_application = models.Application(
        **application.model_dump(),
        user_id=current_user.id
    )

    db.add(new_application)
    db.flush()

    history = models.ApplicationStatusHistory(
        application_id=new_application.id,
        from_status=None,
        to_status=new_application.status
    )

    db.add(history)

    db.commit()
    db.refresh(new_application)

    return new_application

# Get applications
@router.get(
    "/",
    response_model=schemas.ApplicationListResponse
)
def get_applications(
    status: schemas.ApplicationStatus | None = None,
    country: str | None = None,
    company: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    filters = [
        models.Application.user_id == current_user.id
    ]

    if status is not None:
        filters.append(
            models.Application.status == status.value
        )

    if country is not None:
        filters.append(
            models.Application.country.ilike(country)
        )

    if company is not None:
        filters.append(
            models.Application.company.ilike(f"%{company}%")
        )

    statement = select(models.Application)

    count_statement = select(
        func.count()
    ).select_from(models.Application)

    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)

    offset = (page - 1) * limit

    statement = (
        statement
        .order_by(models.Application.id)
        .offset(offset)
        .limit(limit)
    )

    applications = db.scalars(statement).all()

    total = db.scalar(count_statement) or 0

    total_pages = (
        total + limit - 1
    ) // limit

    has_next = page < total_pages
    has_previous = page > 1
    
    return {
        "metadata": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
            "has_next": has_next,
            "has_previous": has_previous
        },
        "items": applications
    }

# Get application by id
@router.get(
    "/{application_id}",
    response_model=schemas.ApplicationResponse
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    statement = select(models.Application).where(
        models.Application.id == application_id,
        models.Application.user_id == current_user.id
    )

    application = db.scalar(statement)

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    statement = select(models.Application).where(
        models.Application.id == application_id,
        models.Application.user_id == current_user.id
    )

    application = db.scalar(statement)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )
    
    old_status = application.status

    for field, value in application_data.model_dump().items():
        setattr(application, field, value)

    if (
        "status" in update_data
        and application.status != old_status
    ):
        history = models.ApplicationStatusHistory(
            application_id=application.id,
            from_status=old_status,
            to_status=application.status
        )

        db.add(history)

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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    statement = select(models.Application).where(
        models.Application.id == application_id,
        models.Application.user_id == current_user.id
    )

    application = db.scalar(statement)

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
@router.patch(
    "/{application_id}",
    response_model=schemas.ApplicationResponse
)
def patch_application(
    application_id: int,
    application_data: schemas.ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    statement = select(models.Application).where(
        models.Application.id == application_id,
        models.Application.user_id == current_user.id
    )

    application = db.scalar(statement)

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    old_status = application.status

    update_data = application_data.model_dump(
        exclude_unset=True,
        mode="json"
    )

    for field, value in update_data.items():
        setattr(application, field, value)

    # Solo generamos historial si realmente cambió el estado
    if (
        "status" in update_data
        and application.status != old_status
    ):
        history = models.ApplicationStatusHistory(
            application_id=application.id,
            from_status=old_status,
            to_status=application.status
        )

        db.add(history)

    db.commit()
    db.refresh(application)

    return application

# Status History of an application
@router.get(
    "/{application_id}/history",
    response_model=list[
        schemas.ApplicationStatusHistoryResponse
    ]
)
def get_application_history(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    application_statement = select(
        models.Application
    ).where(
        models.Application.id == application_id,
        models.Application.user_id == current_user.id
    )

    application = db.scalar(
        application_statement
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail="Application not found"
        )

    history_statement = (
        select(models.ApplicationStatusHistory)
        .where(
            models.ApplicationStatusHistory.application_id
            == application_id
        )
        .order_by(
            models.ApplicationStatusHistory.changed_at
        )
    )

    history = db.scalars(
        history_statement
    ).all()

    return history