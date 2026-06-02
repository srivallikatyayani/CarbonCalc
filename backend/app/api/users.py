"""
app/api/users.py
────────────────
User management API endpoints.

Endpoints:
    POST /users/    → Register a new user
    GET  /users/    → List all users (paginated)

Dependency injection:
    Every endpoint receives a `db: Session` via `Depends(get_db)`.
    FastAPI calls get_db(), which yields a SessionLocal() instance,
    and closes it automatically after the response is sent.

Error handling philosophy:
    - 409 Conflict     → duplicate email (valid request, state conflict)
    - 422 Unprocessable → Pydantic validation failure (automatic, from schema)
    - 500 Internal     → unexpected DB errors (propagated, logged by uvicorn)

Future endpoints in this router (Phase 2+):
    GET    /users/{id}    → Get single user by ID
    PATCH  /users/{id}    → Update user profile
    DELETE /users/{id}    → Soft-delete (set is_active=False)
    GET    /users/me      → Get current authenticated user (after JWT auth)
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.security import hash_password
from app.database.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserListResponse, UserResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


# ── POST /users/ ──────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
        "Creates a new user account. The password is hashed with bcrypt "
        "before storage — it is never persisted in plaintext. "
        "Returns 409 if the email is already registered."
    ),
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
    """
    Register a new user account.

    Flow:
        1. Check for duplicate email (409 if found)
        2. Hash the plaintext password
        3. Build and persist the User ORM object
        4. Commit the transaction
        5. Refresh the object (loads server-side: id, created_at, updated_at)
        6. Return UserResponse (hashed_password is excluded by schema)
    """
    # ── 1. Duplicate email check ──────────────────────────────────────────────
    existing_user = db.scalar(
        select(User).where(User.email == payload.email)
    )
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{payload.email}' already exists.",
        )

    # ── 2. Hash password — plaintext is discarded after this line ─────────────
    hashed_pw = hash_password(payload.password)

    # ── 3. Build ORM object ───────────────────────────────────────────────────
    db_user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hashed_pw,
        is_active=True,
    )

    # ── 4. Persist ────────────────────────────────────────────────────────────
    db.add(db_user)
    db.commit()

    # ── 5. Refresh — loads server-generated id, created_at, updated_at ────────
    db.refresh(db_user)

    # ── 6. Return (Pydantic serialises; hashed_password is excluded) ──────────
    return db_user


# ── GET /users/ ───────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description=(
        "Returns a paginated list of all registered users. "
        "Use `skip` and `limit` for pagination. "
        "The `count` field always reflects the total number of users, "
        "regardless of the current page."
    ),
)
def list_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Max records to return"),
    db: Session = Depends(get_db),
) -> UserListResponse:
    """
    Retrieve a paginated list of users.

    `count` = total users in the DB (for frontend pagination controls).
    `users` = the current page of results.

    Future: add `is_active` filter query param to exclude deactivated accounts.
    """
    # Total count (independent of pagination — needed by frontend)
    total_count = db.scalar(select(func.count()).select_from(User))

    # Paginated results
    users = db.scalars(
        select(User).offset(skip).limit(limit)
    ).all()

    return UserListResponse(count=total_count or 0, users=list(users))


class UserIndustryUpdate(BaseModel):
    industry_type: str


@router.put(
    "/{user_id}/industry",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user industry sector",
)
def update_user_industry(
    user_id: int,
    payload: UserIndustryUpdate,
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found.",
        )
    user.industry_type = payload.industry_type.strip()
    db.commit()
    db.refresh(user)
    return user