from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.security import (
    create_access_token,
    hash_password,
    verify_password
)

from app.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=schemas.UserResponse,
    status_code=201
)
def register_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    email = str(user_data.email).lower()

    statement = select(models.User).where(
        models.User.email == email
    )

    existing_user = db.scalar(statement)

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    new_user = models.User(
        email=email,
        password_hash=hash_password(
            user_data.password
        )
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post(
    "/login",
    response_model=schemas.TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username.lower()

    statement = select(models.User).where(
        models.User.email == email
    )

    user = db.scalar(statement)

    if (
        user is None
        or not verify_password(
            form_data.password,
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    access_token = create_access_token(
        subject=str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get(
    "/me",
    response_model=schemas.UserResponse
)
def get_me(
    current_user: models.User = Depends(
        get_current_user
    )
):
    return current_user