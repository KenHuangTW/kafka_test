from datetime import datetime
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from services.main_service.controller.product_controller import (
    create_new_product,
    delete_product,
    get_product,
    update_existing_product,
)
from services.main_service.schemas.product import ProductUpsertRequest


@pytest.mark.asyncio
async def test_get_product_flow_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.utcnow()
    fake_product = SimpleNamespace(
        id=9,
        name="Mouse",
        description="Wireless",
        price=1000,
        currency="TWD",
        create_at=now,
        update_at=now,
        delete_at=None,
    )
    monkeypatch.setattr(
        "services.main_service.controller.product_controller.get_active_product_by_id",
        lambda db, product_id: fake_product,
    )

    response = await get_product(db=object(), product_id=9)

    assert response.id == 9
    assert response.name == "Mouse"
    assert response.price == 1000


@pytest.mark.asyncio
async def test_get_product_raises_when_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "services.main_service.controller.product_controller.get_active_product_by_id",
        lambda db, product_id: None,
    )

    with pytest.raises(HTTPException) as exc:
        await get_product(db=object(), product_id=999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "product not found"


@pytest.mark.asyncio
async def test_create_product_flow_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.utcnow()
    monkeypatch.setattr(
        "services.main_service.controller.product_controller.create_product",
        lambda db, name, description, price, currency: SimpleNamespace(
            id=10,
            name=name,
            description=description,
            price=price,
            currency=currency,
            create_at=now,
            update_at=now,
            delete_at=None,
        ),
    )

    response = await create_new_product(
        db=object(),
        payload=ProductUpsertRequest(
            name="Monitor",
            description="27 inch",
            price=8999,
            currency="TWD",
        ),
    )

    assert response.id == 10
    assert response.name == "Monitor"
    assert response.currency == "TWD"


@pytest.mark.asyncio
async def test_update_product_flow_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.utcnow()
    fake_product = SimpleNamespace(
        id=11,
        name="Old",
        description=None,
        price=1,
        currency="USD",
        create_at=now,
        update_at=now,
        delete_at=None,
    )
    called: dict[str, object] = {}

    monkeypatch.setattr(
        "services.main_service.controller.product_controller.get_active_product_by_id",
        lambda db, product_id: fake_product,
    )

    def fake_update(db, product, name, description, price, currency):
        called["product"] = product
        called["name"] = name
        called["description"] = description
        called["price"] = price
        called["currency"] = currency
        return product

    monkeypatch.setattr("services.main_service.controller.product_controller.update_product", fake_update)

    response = await update_existing_product(
        db=object(),
        product_id=11,
        payload=ProductUpsertRequest(
            name="New",
            description="updated",
            price=300,
            currency="TWD",
        ),
    )

    assert response.success is True
    assert called["product"] is fake_product
    assert called["name"] == "New"
    assert called["price"] == 300
    assert called["currency"] == "TWD"


@pytest.mark.asyncio
async def test_delete_product_flow_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    now = datetime.utcnow()
    fake_product = SimpleNamespace(
        id=12,
        name="SSD",
        description="1TB",
        price=2500,
        currency="TWD",
        create_at=now,
        update_at=now,
        delete_at=None,
    )
    called: dict[str, object] = {}

    monkeypatch.setattr(
        "services.main_service.controller.product_controller.get_active_product_by_id",
        lambda db, product_id: fake_product,
    )

    def fake_soft_delete(db, product):
        called["product"] = product
        return product

    monkeypatch.setattr("services.main_service.controller.product_controller.soft_delete_product", fake_soft_delete)

    response = await delete_product(db=object(), product_id=12)

    assert response.success is True
    assert called["product"] is fake_product
