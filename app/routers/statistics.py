from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/statistics",
    tags=["Statistics"]
)

@router.get(
    "/",
    response_model=schemas.StatisticsResponse
)
def get_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    total_statement = (
        select(func.count())
        .select_from(models.Application)
        .where(
            models.Application.user_id == current_user.id
        )
    )

    total = db.scalar(total_statement) or 0

    status_statement = (
        select(
            models.Application.status,
            func.count(models.Application.id)
        )
        .where(
            models.Application.user_id == current_user.id
        )
        .group_by(models.Application.status)
    )

    status_results = db.execute(
        status_statement
    ).all()

    by_status = {
        status: count
        for status, count in status_results
    }

    for status in schemas.ApplicationStatus:
        by_status.setdefault(
            status.value,
            0
        )

    interview_count = by_status["interview"]
    offer_count = by_status["offer"]

    interview_rate = (
        (interview_count / total) * 100
        if total > 0
        else 0
    )

    offer_rate = (
        (offer_count / total) * 100
        if total > 0
        else 0
    )

    return {
        "total": total,
        "by_status": by_status,
        "interview_rate": round(
            interview_rate,
            2
        ),
        "offer_rate": round(
            offer_rate,
            2
        )
    }