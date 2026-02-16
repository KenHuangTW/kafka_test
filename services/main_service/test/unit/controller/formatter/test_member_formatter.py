from services.main_service.controller.formatter.member_formatter import (
    format_login_response,
    format_register_response,
)


def test_format_register_response() -> None:
    response = format_register_response(member_id=1, token="token-1")
    assert response.success is True
    assert response.message == "register success"
    assert response.data.member_id == 1
    assert response.data.token == "token-1"


def test_format_login_response() -> None:
    response = format_login_response(member_id=2, token="token-2")
    assert response.success is True
    assert response.message == "login success"
    assert response.data.member_id == 2
    assert response.data.token == "token-2"
