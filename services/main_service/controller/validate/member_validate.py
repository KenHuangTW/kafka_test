from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from services.main_service.app.models import Member
from services.main_service.controller.repository.member_repository import (
    get_member_by_account,
    verify_password,
)


def ensure_account_not_exists(db: Session, account: str) -> None:
    exists = get_member_by_account(db=db, account=account)
    if exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="account already exists",
        )


def validate_login_credentials(db: Session, account: str, password: str) -> Member:
    member = get_member_by_account(db=db, account=account)
    if member is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid account or password",
        )

    if not verify_password(raw_password=password, hashed_password=member.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid account or password",
        )

    return member
