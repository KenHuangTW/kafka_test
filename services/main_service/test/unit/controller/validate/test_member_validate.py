from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from services.main_service.controller.validate.member_validate import (
    ensure_account_not_exists,
    validate_login_credentials,
)


def test_ensure_account_not_exists_raises_when_duplicated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "services.main_service.controller.validate.member_validate.get_member_by_account",
        lambda db, account: SimpleNamespace(id=1, account=account),
    )

    with pytest.raises(HTTPException) as exc:
        ensure_account_not_exists(db=object(), account="ken")

    assert exc.value.status_code == 409


def test_validate_login_credentials_success(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_member = SimpleNamespace(id=1, account="ken", password="hashed")
    monkeypatch.setattr(
        "services.main_service.controller.validate.member_validate.get_member_by_account",
        lambda db, account: fake_member,
    )
    monkeypatch.setattr(
        "services.main_service.controller.validate.member_validate.verify_password",
        lambda raw_password, hashed_password: True,
    )

    member = validate_login_credentials(db=object(), account="ken", password="1234567890")
    assert member.id == 1


def test_validate_login_credentials_raises_when_password_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_member = SimpleNamespace(id=1, account="ken", password="hashed")
    monkeypatch.setattr(
        "services.main_service.controller.validate.member_validate.get_member_by_account",
        lambda db, account: fake_member,
    )
    monkeypatch.setattr(
        "services.main_service.controller.validate.member_validate.verify_password",
        lambda raw_password, hashed_password: False,
    )

    with pytest.raises(HTTPException) as exc:
        validate_login_credentials(db=object(), account="ken", password="1234567890")

    assert exc.value.status_code == 401
