import bcrypt

from sqlalchemy import select
from sqlalchemy.orm import Session

from services.main_service.app.models import Member


def hash_password(raw_password: str) -> str:
    hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False


def get_member_by_account(db: Session, account: str) -> Member | None:
    stmt = select(Member).where(Member.account == account)
    return db.execute(stmt).scalar_one_or_none()


def create_member(db: Session, account: str, password: str) -> Member:
    member = Member(account=account, password=hash_password(password))
    db.add(member)
    db.commit()
    db.refresh(member)
    return member
