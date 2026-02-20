from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

from services.payment_service.controller.repository.payment_repository import (
    create_order,
    get_active_member_by_id,
    get_active_product_by_id,
)


def test_get_active_member_by_id_reads_from_session() -> None:
    fake_member = SimpleNamespace(id=1)
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = fake_member

    member = get_active_member_by_id(db=fake_db, member_id=1)

    fake_db.execute.assert_called_once()
    assert member is fake_member


def test_get_active_product_by_id_reads_from_session() -> None:
    fake_product = SimpleNamespace(id=2)
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = fake_product

    product = get_active_product_by_id(db=fake_db, product_id=2)

    fake_db.execute.assert_called_once()
    assert product is fake_product


def test_create_order_with_fake_db_session() -> None:
    fake_db = MagicMock()

    def fake_refresh(order: object) -> None:
        order.id = 100

    fake_db.refresh.side_effect = fake_refresh

    order = create_order(
        db=fake_db,
        member_id=8,
        product_id=3,
        amount=Decimal("99.00"),
        currency="TWD",
    )

    fake_db.add.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()
    assert order.id == 100
    assert order.member_id == 8
    assert order.product_id == 3
    assert order.amount == Decimal("99.00")
    assert order.currency == "TWD"
