from sqlalchemy.orm import Session

from services.main_service.controller.formatter.member_formatter import (
    format_login_response,
    format_register_response,
)
from services.main_service.controller.repository.member_repository import create_member
from services.main_service.controller.validate.member_validate import (
    ensure_account_not_exists,
    validate_login_credentials,
)
from services.main_service.schemas.member import (
    MemberLoginRequest,
    MemberLoginResponse,
    MemberRegisterRequest,
    MemberRegisterResponse,
)
from services.main_service.utils.jwt import issue_member_token


async def register_member(db: Session, payload: MemberRegisterRequest) -> MemberRegisterResponse:
    ensure_account_not_exists(db=db, account=payload.account)
    member = create_member(db=db, account=payload.account, password=payload.password)
    token = issue_member_token(member_id=member.id, account=member.account)
    return format_register_response(member_id=member.id, token=token)


async def login_member(db: Session, payload: MemberLoginRequest) -> MemberLoginResponse:
    member = validate_login_credentials(db=db, account=payload.account, password=payload.password)
    token = issue_member_token(member_id=member.id, account=member.account)
    return format_login_response(member_id=member.id, token=token)
