"""
app/schemas/user.py
───────────────────
Pydantic v2 schemas for the User domain.

Schema separation is intentional and critical:

    UserCreate      → Input schema for POST /users/.
                      Accepts `password` (plaintext). Pydantic validates it
                      before it reaches the endpoint. The endpoint hashes it
                      and discards the plaintext immediately.

    UserResponse    → Output schema for all user-returning endpoints.
                      NEVER includes hashed_password. This is a hard
                      security boundary — Pydantic will raise an error if
                      you accidentally try to include it.

    UserListResponse → Envelope for GET /users/. Includes total count
                        alongside the list — needed for future pagination
                        (the frontend can't know total pages without it).

Why from_attributes=True (formerly orm_mode)?
    Pydantic reads values from SQLAlchemy model attributes, not dict keys.
    Without this, UserResponse.model_validate(db_user) would fail because
    SQLAlchemy ORM objects are not plain dictionaries.

Future schemas to add in this file:
    UserUpdate      → PATCH /users/{id} — partial updates (Phase 2)
    UserProfile     → Extended profile with carbon stats (Phase 3)
    UserPublic      → Minimal public view for leaderboards (Phase 4)
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# ── Input Schema ──────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    """
    Validated input for POST /users/ (user registration).

    The `password` field is plaintext — it is hashed in the endpoint
    before the User ORM object is constructed. It never touches the DB.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Alice Johnson"],
        description="Full display name of the user or company",
    )

    email: EmailStr = Field(
        ...,
        examples=["alice@example.com"],
        description="Valid email address — must be unique in the system",
    )

    password: str = Field(
        ...,
        min_length=8,
        examples=["securepass123"],
        description="Minimum 8 characters. Will be hashed before storage.",
    )

    industry_type: str | None = Field(
        None,
        max_length=100,
        description="Industry sector selected by company",
    )

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        """Reject names that are only whitespace."""
        if not value.strip():
            raise ValueError("Name must not be blank or whitespace only")
        return value.strip()

    @field_validator("password")
    @classmethod
    def password_complexity(cls, value: str) -> str:
        """
        Basic complexity check. Extend this in Phase 2 (auth hardening)
        to enforce uppercase, digits, and special characters.
        """
        if value.isspace():
            raise ValueError("Password must not be blank")
        return value


# ── Output Schema ─────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    """
    API response shape for a single user.

    Security contract: hashed_password is deliberately absent.
    Pydantic only serialises fields declared in this class.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Unique user identifier")
    name: str = Field(description="Display name")
    email: str = Field(description="Email address")
    industry_type: str | None = Field(None, description="Primary industry sector")
    is_active: bool = Field(description="Account status")
    created_at: datetime = Field(description="Registration timestamp (UTC)")
    updated_at: datetime = Field(description="Last profile update timestamp (UTC)")


# ── List Response Envelope ────────────────────────────────────────────────────
class UserListResponse(BaseModel):
    """
    Envelope for GET /users/ — wraps the list with metadata.

    `count` is the total number of matching records (ignoring skip/limit).
    This is essential for frontend pagination: the UI needs total_pages,
    which requires knowing the total count.

    Future: add `page`, `page_size`, `total_pages` when pagination is wired.
    """

    count: int = Field(description="Total number of users in the system")
    users: list[UserResponse] = Field(description="Page of user records")