"""
Create or reset the default admin user's password.

Usage (from the backend/ directory):
    python -m scripts.reset_admin
"""
import logging

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import Base, SessionLocal, engine
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def reset_admin() -> None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == settings.default_admin_email).first()

        if user:
            logger.info("Updating existing admin user...")
            user.hashed_password = get_password_hash(settings.default_admin_password)
        else:
            logger.info("Creating new admin user...")
            user = User(
                email=settings.default_admin_email,
                hashed_password=get_password_hash(settings.default_admin_password),
                full_name="Admin User",
            )
            db.add(user)

        db.commit()
        logger.info("Admin user configured successfully. Email: %s", settings.default_admin_email)
    finally:
        db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    reset_admin()
