"""Authentication router – simple token-based auth for consultant dashboard."""

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

from backend.config import settings
from backend.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

ALGORITHM = "HS256"


def create_access_token(expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": "consultant", "exp": expire}
    return jwt.encode(payload, settings.app_secret_key, algorithm=ALGORITHM)


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """FastAPI dependency — verifies the JWT token."""
    try:
        payload = jwt.decode(
            credentials.credentials, settings.app_secret_key, algorithms=[ALGORITHM]
        )
        return payload.get("sub", "")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate consultant with password and return JWT."""
    if request.password != settings.consultant_password:
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token()
    return TokenResponse(access_token=token)
