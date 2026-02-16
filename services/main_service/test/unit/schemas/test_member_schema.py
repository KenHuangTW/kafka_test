import pytest
from pydantic import ValidationError

from services.main_service.schemas.member import MemberLoginRequest, MemberRegisterRequest


def test_register_schema_accepts_password_length_10() -> None:
    payload = MemberRegisterRequest(account="ken", password="1234567890")
    assert payload.account == "ken"


def test_register_schema_rejects_password_length_not_10() -> None:
    with pytest.raises(ValidationError):
        MemberRegisterRequest(account="ken", password="123")


def test_login_schema_accepts_password_length_10() -> None:
    payload = MemberLoginRequest(account="ken", password="abcdefghij")
    assert payload.account == "ken"
