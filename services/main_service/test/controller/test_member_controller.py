import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.main_service.app.models import Member


@pytest.mark.parametrize(
    "payload,seed_first,expected_status,expected_message,expected_success,expected_count",
    [
        ({"account": "ken", "password": "1234567890"}, False, 200, "register success", True, 1),
        ({"account": "ken", "password": "1234567890"}, True, 409, "account already exists", None, 1),
    ],
)
def test_register_cases(
    test_client: TestClient,
    db_session: Session,
    payload: dict[str, str],
    seed_first: bool,
    expected_status: int,
    expected_message: str,
    expected_success: bool | None,
    expected_count: int,
) -> None:
    if seed_first:
        seed_response = test_client.post("/members/register", json=payload)
        assert seed_response.status_code == 200

    response = test_client.post("/members/register", json=payload)

    assert response.status_code == expected_status
    body = response.json()
    if expected_status == 200:
        assert body["success"] is expected_success
        assert body["message"] == expected_message
        assert body["data"]["member_id"] > 0
        assert isinstance(body["data"]["token"], str)
        assert len(body["data"]["token"]) > 20
    else:
        assert body["detail"] == expected_message

    member_count = len(db_session.execute(select(Member)).scalars().all())
    assert member_count == expected_count


@pytest.mark.parametrize(
    "login_payload,expected_status,expected_message,expected_success",
    [
        ({"account": "ken", "password": "1234567890"}, 200, "login success", True),
        ({"account": "ken", "password": "0987654321"}, 401, "invalid account or password", None),
        ({"account": "nobody", "password": "1234567890"}, 401, "invalid account or password", None),
    ],
)
def test_login_cases(
    test_client: TestClient,
    db_session: Session,
    login_payload: dict[str, str],
    expected_status: int,
    expected_message: str,
    expected_success: bool | None,
) -> None:
    register_payload = {"account": "ken", "password": "1234567890"}
    register_response = test_client.post("/members/register", json=register_payload)
    assert register_response.status_code == 200

    response = test_client.post("/members/login", json=login_payload)

    assert response.status_code == expected_status
    body = response.json()
    if expected_status == 200:
        assert body["success"] is expected_success
        assert body["message"] == expected_message
        assert body["data"]["member_id"] > 0
        assert isinstance(body["data"]["token"], str)
        assert len(body["data"]["token"]) > 20
    else:
        assert body["detail"] == expected_message

    # Login should not create new member records.
    member_count = len(db_session.execute(select(Member)).scalars().all())
    assert member_count == 1
