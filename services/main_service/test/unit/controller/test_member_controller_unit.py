from types import SimpleNamespace

import pytest

from services.main_service.controller.member_controller import login_member, register_member
from services.main_service.schemas.member import MemberLoginRequest, MemberRegisterRequest


@pytest.mark.asyncio
async def test_register_member_flow_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "services.main_service.controller.member_controller.ensure_account_not_exists",
        lambda db, account: None,
    )
    monkeypatch.setattr(
        "services.main_service.controller.member_controller.create_member",
        lambda db, account, password: SimpleNamespace(id=11, account=account),
    )
    monkeypatch.setattr(
        "services.main_service.controller.member_controller.issue_member_token",
        lambda member_id, account: "token-11",
    )

    response = await register_member(
        db=object(),
        payload=MemberRegisterRequest(account="ken", password="1234567890"),
    )

    assert response.success is True
    assert response.data.member_id == 11
    assert response.data.token == "token-11"


@pytest.mark.asyncio
async def test_login_member_flow_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "services.main_service.controller.member_controller.validate_login_credentials",
        lambda db, account, password: SimpleNamespace(id=12, account=account),
    )
    monkeypatch.setattr(
        "services.main_service.controller.member_controller.issue_member_token",
        lambda member_id, account: "token-12",
    )

    response = await login_member(
        db=object(),
        payload=MemberLoginRequest(account="ken", password="1234567890"),
    )

    assert response.success is True
    assert response.data.member_id == 12
    assert response.data.token == "token-12"
