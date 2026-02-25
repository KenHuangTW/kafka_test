from decimal import Decimal
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.main_service.utils.jwt import issue_member_token
from services.payment_service.app.models import Member, Order, Product


def test_checkout_payment_success(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed")
    product = Product(
        name="Laptop",
        description="13 inch",
        price=42000,
        currency="TWD",
        sale_limit=2,
    )
    db_session.add(member)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(member)
    db_session.refresh(product)

    token = issue_member_token(member_id=member.id, account=member.account)
    response = test_client.post(
        "/payments/checkout",
        json={"token": token, "product_id": product.id},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "payment success"
    assert body["data"]["member_id"] == member.id
    assert body["data"]["product_id"] == product.id
    assert body["data"]["amount"] == "42000.00"
    assert body["data"]["currency"] == "TWD"

    order_id = body["data"]["order_id"]
    with Session(bind=db_session.get_bind()) as verify_session:
        order = verify_session.execute(select(Order).where(Order.id == order_id)).scalar_one()
    assert order.member_id == member.id
    assert order.product_id == product.id
    assert order.amount == Decimal("42000.00")
    assert order.currency == "TWD"


def test_checkout_payment_invalid_token(test_client: TestClient, db_session: Session) -> None:
    product = Product(name="Laptop", description=None, price=1, currency="TWD", sale_limit=1)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    response = test_client.post(
        "/payments/checkout",
        json={"token": "invalid-token", "product_id": product.id},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid token"


def test_checkout_payment_product_not_found(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed")
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)

    token = issue_member_token(member_id=member.id, account=member.account)
    response = test_client.post(
        "/payments/checkout",
        json={"token": token, "product_id": 99999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "product not found"


def test_checkout_payment_member_deleted_is_rejected(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed", delete_at=datetime.utcnow())
    product = Product(name="Laptop", description=None, price=100, currency="TWD", sale_limit=1)
    db_session.add(member)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(member)
    db_session.refresh(product)

    token = issue_member_token(member_id=member.id, account=member.account)
    response = test_client.post(
        "/payments/checkout",
        json={"token": token, "product_id": product.id},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "invalid token"


def test_checkout_payment_rejects_when_sale_limit_reached(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed")
    product = Product(name="Laptop", description=None, price=100, currency="TWD", sale_limit=1)
    db_session.add(member)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(member)
    db_session.refresh(product)

    existing_order = Order(
        member_id=member.id,
        product_id=product.id,
        amount=Decimal("100.00"),
        currency="TWD",
    )
    db_session.add(existing_order)
    db_session.commit()

    token = issue_member_token(member_id=member.id, account=member.account)
    response = test_client.post(
        "/payments/checkout",
        json={"token": token, "product_id": product.id},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "product sold out"


def test_checkout_payment_allows_when_sale_limit_is_null(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed")
    product = Product(name="Laptop", description=None, price=100, currency="TWD", sale_limit=None)
    db_session.add(member)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(member)
    db_session.refresh(product)

    existing_order = Order(
        member_id=member.id,
        product_id=product.id,
        amount=Decimal("100.00"),
        currency="TWD",
    )
    db_session.add(existing_order)
    db_session.commit()

    token = issue_member_token(member_id=member.id, account=member.account)
    response = test_client.post(
        "/payments/checkout",
        json={"token": token, "product_id": product.id},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True
