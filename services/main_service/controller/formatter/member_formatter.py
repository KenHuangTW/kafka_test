from services.main_service.schemas.member import (
    MemberAuthData,
    MemberLoginResponse,
    MemberRegisterResponse,
)


def format_register_response(member_id: int, token: str) -> MemberRegisterResponse:
    return MemberRegisterResponse(
        success=True,
        message="register success",
        data=MemberAuthData(member_id=member_id, token=token),
    )


def format_login_response(member_id: int, token: str) -> MemberLoginResponse:
    return MemberLoginResponse(
        success=True,
        message="login success",
        data=MemberAuthData(member_id=member_id, token=token),
    )
