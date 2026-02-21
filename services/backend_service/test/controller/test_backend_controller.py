from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from services.payment_service.app.models import Member, Order, Product


def test_get_product_and_order_success(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="ken", password="hashed")
    product = Product(name="Laptop", description="13 inch", price=42000, currency="TWD", sale_limit=5)
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
    assert product_body["success"] is True
    assert product_body["message"] == "get product success"
    assert product_body["data"]["id"] == product.id
    assert product_body["data"]["name"] == "Laptop"
    assert product_body["data"]["price"] == 42000
    assert product_body["data"]["sale_limit"] == 5

    order_response = test_client.get(f"/order/{order.id}")
    assert order_response.status_code == 200
    order_body = order_response.json()
    assert order_body["success"] is True
    assert order_body["message"] == "get order success"
    assert order_body["data"]["id"] == order.id
    assert order_body["data"]["member_id"] == member.id
    assert order_body["data"]["product_id"] == product.id
    assert order_body["data"]["amount"] == "42000.00"
    assert order_body["data"]["currency"] == "TWD"


def test_get_product_and_order_not_found(test_client: TestClient) -> None:
    product_response = test_client.get("/product/99999")
    assert product_response.status_code == 404
    assert product_response.json()["detail"] == "product not found"

    order_response = test_client.get("/order/99999")
    assert order_response.status_code == 404
    assert order_response.json()["detail"] == "order not found"


def test_get_product_and_order_list_success(test_client: TestClient, db_session: Session) -> None:
    member = Member(account="list-user", password="hashed")
    db_session.add(member)

    product_1 = Product(name="Keyboard", description="wireless", price=2100, currency="TWD", sale_limit=10)
    product_2 = Product(name="Mouse", description="ergonomic", price=1500, currency="TWD", sale_limit=8)
    product_deleted = Product(name="Legacy", description=None, price=999, currency="TWD", sale_limit=1)
    db_session.add_all([product_1, product_2, product_deleted])
    db_session.commit()
    db_session.refresh(member)
    db_session.refresh(product_1)
    db_session.refresh(product_2)
    db_session.refresh(product_deleted)

    product_deleted.delete_at = datetime.utcnow()
    db_session.commit()

    order_1 = Order(
        member_id=member.id,
        product_id=product_1.id,
        amount=Decimal("2100.00"),
        currency="TWD",
    )
    order_2 = Order(
        member_id=member.id,
        product_id=product_2.id,
        amount=Decimal("1500.00"),
        currency="TWD",
    )
    order_deleted = Order(
        member_id=member.id,
        product_id=product_1.id,
        amount=Decimal("1.00"),
        currency="TWD",
    )
    db_session.add_all([order_1, order_2, order_deleted])
    db_session.commit()
    db_session.refresh(order_1)
    db_session.refresh(order_2)
    db_session.refresh(order_deleted)

    order_deleted.delete_at = datetime.utcnow()
    db_session.commit()

    product_response = test_client.get("/product/?limit=10&offset=0")
    assert product_response.status_code == 200
    product_body = product_response.json()
    assert product_body["success"] is True
    assert product_body["message"] == "get product list success"
    assert len(product_body["data"]) == 2
    assert [item["id"] for item in product_body["data"]] == [product_1.id, product_2.id]

    order_response = test_client.get("/order/?limit=10&offset=0")
    assert order_response.status_code == 200
    order_body = order_response.json()
    assert order_body["success"] is True
    assert order_body["message"] == "get order list success"
    assert len(order_body["data"]) == 2
    assert [item["id"] for item in order_body["data"]] == [order_1.id, order_2.id]


def test_get_product_and_order_list_empty(test_client: TestClient) -> None:
    product_response = test_client.get("/product/")
    assert product_response.status_code == 200
    assert product_response.json() == {
        "success": True,
        "message": "get product list success",
        "data": [],
    }

    order_response = test_client.get("/order/")
    assert order_response.status_code == 200
    assert order_response.json() == {
        "success": True,
        "message": "get order list success",
        "data": [],
    }
