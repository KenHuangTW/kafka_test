from unittest.mock import MagicMock

from services.main_service.controller.repository.member_repository import (
    create_member,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password_with_bcrypt() -> None:
    hashed = hash_password("1234567890")
    assert hashed != "1234567890"
    assert verify_password("1234567890", hashed) is True
    assert verify_password("xxxxxxxxxx", hashed) is False


def test_create_member_with_fake_db_session() -> None:
    fake_db = MagicMock()

    def fake_refresh(member: object) -> None:
        member.id = 77

    fake_db.refresh.side_effect = fake_refresh

    member = create_member(db=fake_db, account="ken", password="1234567890")

    fake_db.add.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()
    assert member.account == "ken"
    assert member.password != "1234567890"
    assert member.id == 77
