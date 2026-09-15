import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import enforce_login_rate_limit
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token, UserRead

router = APIRouter(tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/token", response_model=Token)
async def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    enforce_login_rate_limit(request)

    user = db.query(User).filter(User.email == form_data.username).first()

    # Bootstrap convenience: create the configured default admin on first
    # login if no users exist yet at all. Only ever applies to an empty
    # database, so it can't be used to take over an existing account.
    if (
        user is None
        and db.query(User).count() == 0
        and form_data.username == settings.default_admin_email
        and form_data.password == settings.default_admin_password
    ):
        user = User(
            email=settings.default_admin_email,
            hashed_password=get_password_hash(settings.default_admin_password),
            full_name="Admin User",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("Bootstrapped default admin user on first login")

    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token)


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
