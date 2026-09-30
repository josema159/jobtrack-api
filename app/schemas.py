from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime

class ApplicationStatus(str, Enum):
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


class ApplicationResponse(ApplicationCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdate(BaseModel):
    company: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    position: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )
    country: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    job_url: Optional[str] = None
    notes: Optional[str] = None    

class PaginationMetadata(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool

class ApplicationListResponse(BaseModel):
    metadata: PaginationMetadata
    items: list[ApplicationResponse]    

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128
    )


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class TokenResponse(BaseModel):
    access_token: str
    token_type: str    

class StatisticsResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    interview_rate: float
    offer_rate: float    

class ApplicationStatusHistoryResponse(BaseModel):
    id: int
    from_status: ApplicationStatus | None
    to_status: ApplicationStatus
    changed_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )    