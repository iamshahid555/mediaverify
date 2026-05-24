from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.db.database import (
    create_session,
    create_user,
    delete_session,
    get_user_by_email,
)
from app.models.schemas import (
    AuthResponse,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    UserResponse,
)
from app.services.security import (
    create_session_token,
    get_bearer_token,
    hash_password,
    require_current_user,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        created_at=user["created_at"],
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    password_hash, password_salt = hash_password(request.password)

    try:
        user = create_user(
            full_name=request.full_name,
            email=request.email,
            password_hash=password_hash,
            password_salt=password_salt,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    token = create_session_token()
    create_session(user["id"], token)

    return AuthResponse(
        token=token,
        user=_build_user_response(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest):
    user = get_user_by_email(request.email)
    if not user or not verify_password(
        request.password,
        user["password_hash"],
        user["password_salt"],
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    token = create_session_token()
    create_session(user["id"], token)

    return AuthResponse(
        token=token,
        user=_build_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
def get_current_account(current_user: dict = Depends(require_current_user)):
    return _build_user_response(current_user)


@router.post("/logout", response_model=MessageResponse)
def logout(
    authorization: str | None = Header(default=None),
    _current_user: dict = Depends(require_current_user),
):
    token = get_bearer_token(authorization)
    if token:
        delete_session(token)

    return MessageResponse(message="Signed out successfully.")
