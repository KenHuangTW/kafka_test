from fastapi import APIRouter

from services.main_service.controller.member_controller import login_member, register_member
from services.main_service.depend import DBSessionDep
from services.main_service.schemas.member import (
    MemberLoginRequest,
    MemberLoginResponse,
    MemberRegisterRequest,
    MemberRegisterResponse,
)

router = APIRouter(prefix="/members", tags=["members"])


@router.post("/register", response_model=MemberRegisterResponse)
async def register(payload: MemberRegisterRequest, db: DBSessionDep) -> MemberRegisterResponse:
    return await register_member(db=db, payload=payload)


@router.post("/login", response_model=MemberLoginResponse)
async def login(payload: MemberLoginRequest, db: DBSessionDep) -> MemberLoginResponse:
    return await login_member(db=db, payload=payload)
