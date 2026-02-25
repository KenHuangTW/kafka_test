from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from services.payment_service.controller.payment_controller import checkout_payment
from services.payment_service.schemas import PaymentCheckoutRequest


@pytest.mark.asyncio
async def test_checkout_success_with_mocks(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_member = SimpleNamespace(id=7)
    fake_product = SimpleNamespace(id=3, price=2500, currency="TWD", sale_limit=2)
    fake_order = SimpleNamespace(id=12, member_id=7, product_id=3, amount=Decimal("2500.00"), currency="TWD")

    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.decode_member_token",
        lambda token: 7,
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_member_by_id",
        lambda db, member_id: fake_member,
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_product_by_id",
        lambda db, product_id: fake_product,
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.create_order",
        lambda db, member_id, product_id, amount, currency: fake_order,
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.count_active_orders_by_product_id",
        lambda db, product_id: 1,
    )

    response = await checkout_payment(
        db=object(),
        payload=PaymentCheckoutRequest(token="t", product_id=3),
    )

    assert response.success is True
    assert response.message == "payment success"
    assert response.data.order_id == 12
    assert response.data.amount == Decimal("2500.00")


@pytest.mark.asyncio
async def test_checkout_raises_for_invalid_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def raise_invalid(token: str) -> int:
        raise HTTPException(status_code=401, detail="invalid token")

    monkeypatch.setattr("services.payment_service.controller.payment_controller.decode_member_token", raise_invalid)

    with pytest.raises(HTTPException) as exc:
        await checkout_payment(db=object(), payload=PaymentCheckoutRequest(token="bad", product_id=1))

    assert exc.value.status_code == 401
    assert exc.value.detail == "invalid token"


@pytest.mark.asyncio
async def test_checkout_raises_when_member_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.payment_service.controller.payment_controller.decode_member_token", lambda token: 5)
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_member_by_id",
        lambda db, member_id: None,
    )

    with pytest.raises(HTTPException) as exc:
        await checkout_payment(db=object(), payload=PaymentCheckoutRequest(token="ok", product_id=1))

    assert exc.value.status_code == 401
    assert exc.value.detail == "invalid token"


@pytest.mark.asyncio
async def test_checkout_raises_when_product_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.payment_service.controller.payment_controller.decode_member_token", lambda token: 5)
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_member_by_id",
        lambda db, member_id: SimpleNamespace(id=5),
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_product_by_id",
        lambda db, product_id: None,
    )

    with pytest.raises(HTTPException) as exc:
        await checkout_payment(db=object(), payload=PaymentCheckoutRequest(token="ok", product_id=9))

    assert exc.value.status_code == 404
    assert exc.value.detail == "product not found"


@pytest.mark.asyncio
async def test_checkout_raises_when_product_sold_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("services.payment_service.controller.payment_controller.decode_member_token", lambda token: 5)
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_member_by_id",
        lambda db, member_id: SimpleNamespace(id=5),
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_product_by_id",
        lambda db, product_id: SimpleNamespace(id=9, price=100, currency="TWD", sale_limit=1),
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.count_active_orders_by_product_id",
        lambda db, product_id: 1,
    )

    with pytest.raises(HTTPException) as exc:
        await checkout_payment(db=object(), payload=PaymentCheckoutRequest(token="ok", product_id=9))

    assert exc.value.status_code == 409
    assert exc.value.detail == "product sold out"


@pytest.mark.asyncio
async def test_checkout_does_not_apply_sold_out_when_sale_limit_is_null(monkeypatch: pytest.MonkeyPatch) -> None:
    fake_order = SimpleNamespace(id=13, member_id=5, product_id=9, amount=Decimal("100.00"), currency="TWD")

    monkeypatch.setattr("services.payment_service.controller.payment_controller.decode_member_token", lambda token: 5)
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_member_by_id",
        lambda db, member_id: SimpleNamespace(id=5),
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.get_active_product_by_id",
        lambda db, product_id: SimpleNamespace(id=9, price=100, currency="TWD", sale_limit=None),
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.count_active_orders_by_product_id",
        lambda db, product_id: 999,
    )
    monkeypatch.setattr(
        "services.payment_service.controller.payment_controller.create_order",
        lambda db, member_id, product_id, amount, currency: fake_order,
    )

    response = await checkout_payment(
        db=object(),
        payload=PaymentCheckoutRequest(token="ok", product_id=9),
    )

    assert response.success is True
    assert response.data.order_id == 13
