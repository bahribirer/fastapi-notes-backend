from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings


def init_admin(db: Session):
    if settings.BOOTSTRAP_ADMIN_EMAIL and settings.BOOTSTRAP_ADMIN_PASSWORD:
        admin = db.query(User).filter(User.email == settings.BOOTSTRAP_ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.BOOTSTRAP_ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.BOOTSTRAP_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
