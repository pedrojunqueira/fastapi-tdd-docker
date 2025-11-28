from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, EmailStr


class SummaryPayloadSchema(BaseModel):
    url: AnyHttpUrl
    summary: str | None = None


class SummaryResponseSchema(SummaryPayloadSchema):
    id: int


class SummaryUpdatePayloadSchema(SummaryPayloadSchema):
    summary: str


# User schemas
class UserCreateSchema(BaseModel):
    """Schema for admin creating a user manually."""

    email: EmailStr
    role: str = "reader"  # Default role


class UserUpdateSchema(BaseModel):
    """Schema for admin updating a user's role."""

    role: str


class UserResponseSchema(BaseModel):
    """Schema for user response."""

    id: int
    email: str
    role: str
    created_at: datetime
    last_login: datetime | None = None

    class Config:
        from_attributes = True


class UserListResponseSchema(BaseModel):
    """Schema for listing users."""

    users: list[UserResponseSchema]
    total: int


class CurrentUserSchema(BaseModel):
    """Schema for the current authenticated user."""

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
