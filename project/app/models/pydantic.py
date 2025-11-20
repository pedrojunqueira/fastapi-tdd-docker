from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl
    summary: str | None = None


class SummaryResponseSchema(SummaryPayloadSchema):
    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    summary: str


# User schemas
class UserCreateSchema(BaseModel):
    email: str
    role: str = "reader"  # Default role


class UserResponseSchema(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime
    last_login: datetime | None = None


class CurrentUserSchema(BaseModel):
    id: int
    email: str
    role: str


# Override the auto-generated SummarySchema to include user_id
class SummarySchema(BaseModel):
    id: int
    url: str
    summary: str
    created_at: datetime
    user_id: int | None = None
