from types import SimpleNamespace
from unittest.mock import MagicMock

from services.main_service.controller.repository.product_repository import (
    create_product,
    get_active_product_by_id,
    soft_delete_product,
    update_product,
)


def test_get_active_product_by_id_reads_from_session() -> None:
    fake_product = SimpleNamespace(id=18)
    fake_db = MagicMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = fake_product

    product = get_active_product_by_id(db=fake_db, product_id=18)

    fake_db.execute.assert_called_once()
    assert product is fake_product


def test_create_product_with_fake_db_session() -> None:
    fake_db = MagicMock()

    def fake_refresh(product: object) -> None:
        product.id = 88

    fake_db.refresh.side_effect = fake_refresh

    product = create_product(
        db=fake_db,
        name="Keyboard",
        description="Mechanical keyboard",
        price=1999,
        currency="TWD",
    )

    fake_db.add.assert_called_once()
    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once()
    assert product.id == 88
    assert product.name == "Keyboard"
    assert product.price == 1999
    assert product.currency == "TWD"


def test_update_product_with_fake_db_session() -> None:
    fake_db = MagicMock()
    product = SimpleNamespace(name="A", description=None, price=1, currency="USD")

    updated = update_product(
        db=fake_db,
        product=product,
        name="B",
        description="updated",
        price=2,
        currency="TWD",
    )

    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once_with(product)
    assert updated is product
    assert product.name == "B"
    assert product.description == "updated"
    assert product.price == 2
    assert product.currency == "TWD"


def test_soft_delete_product_sets_delete_at() -> None:
    fake_db = MagicMock()
    product = SimpleNamespace(delete_at=None)

    deleted = soft_delete_product(db=fake_db, product=product)

    fake_db.commit.assert_called_once()
    fake_db.refresh.assert_called_once_with(product)
    assert deleted is product
    assert product.delete_at is not None
