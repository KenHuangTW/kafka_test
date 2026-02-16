import jwt

from services.main_service.utils.jwt import issue_member_token


def test_issue_member_token(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET_KEY", "unit-test-secret")
    monkeypatch.setenv("JWT_ALGORITHM", "HS256")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "30")

    token = issue_member_token(member_id=99, account="ken")
    payload = jwt.decode(token, "unit-test-secret", algorithms=["HS256"])

    assert payload["sub"] == "99"
    assert payload["account"] == "ken"
