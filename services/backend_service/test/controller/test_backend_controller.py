from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from services.payment_service.app.models import Member, Order, Product


def test_get_product_and_order_success(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed")
    product = Product(name="Laptop", description="13 inch", price=42000, currency="TWD")
    db_session.add(member)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(member)
    db_session.refresh(product)

    order = Order(
        member_id=member.id,
        product_id=product.id,
        amount=Decimal("42000.00"),
        currency="TWD",
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    product_response = test_client.get(f"/product/{product.id}")
    assert product_response.status_code == 200
    product_body = product_response.json()
    assert product_body["id"] == product.id
    assert product_body["name"] == "Laptop"
    assert product_body["price"] == 42000

    order_response = test_client.get(f"/order/{order.id}")
    assert order_response.status_code == 200
    order_body = order_response.json()
    assert order_body["id"] == order.id
    assert order_body["member_id"] == member.id
    assert order_body["product_id"] == product.id
    assert order_body["amount"] == "42000.00"
    assert order_body["currency"] == "TWD"


def test_get_product_and_order_not_found(test_client: TestClient) -> None:
    product_response = test_client.get("/product/99999")
    assert product_response.status_code == 404
    assert product_response.json()["detail"] == "product not found"

    order_response = test_client.get("/order/99999")
    assert order_response.status_code == 404
    assert order_response.json()["detail"] == "order not found"
