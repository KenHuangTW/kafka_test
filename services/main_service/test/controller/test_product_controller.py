import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from services.main_service.app.models import Product


def test_product_crud_flow(test_client: TestClient, db_session: Session) -> None:
    create_payload = {
        "name": "Laptop",
        "description": "13 inch",
        "price": 42000,
        "currency": "TWD",
        "sale_limit": 2,
    }
    create_response = test_client.post("/product/", json=create_payload)
    assert create_response.status_code == 200

    created = create_response.json()
    product_id = created["id"]
    assert product_id > 0
    assert created["name"] == "Laptop"
    assert created["price"] == 42000
    assert created["currency"] == "TWD"
    assert created["sale_limit"] == 2
    assert created["delete_at"] is None

    product_in_db = db_session.execute(select(Product).where(Product.id == product_id)).scalar_one()
    assert product_in_db.price == 42000
    assert product_in_db.currency == "TWD"
    assert product_in_db.sale_limit == 2

    get_response = test_client.get(f"/product/{product_id}")
    assert get_response.status_code == 200
    got = get_response.json()
    assert got["id"] == product_id
    assert got["name"] == "Laptop"

    update_payload = {
        "name": "Laptop Pro",
        "description": "14 inch",
        "price": 52000,
        "currency": "USD",
        "sale_limit": 5,
    }
    update_response = test_client.put(f"/product/{product_id}", json=update_payload)
    assert update_response.status_code == 200
    assert update_response.json() == {"success": True}

    with Session(bind=db_session.get_bind()) as verify_session:
        updated_in_db = verify_session.execute(select(Product).where(Product.id == product_id)).scalar_one()
    assert updated_in_db.name == "Laptop Pro"
    assert updated_in_db.description == "14 inch"
    assert updated_in_db.price == 52000
    assert updated_in_db.currency == "USD"
    assert updated_in_db.sale_limit == 5
    assert updated_in_db.delete_at is None

    delete_response = test_client.delete(f"/product/{product_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True}

    with Session(bind=db_session.get_bind()) as verify_session:
        deleted_in_db = verify_session.execute(select(Product).where(Product.id == product_id)).scalar_one()
    assert deleted_in_db.delete_at is not None

    get_deleted_response = test_client.get(f"/product/{product_id}")
    assert get_deleted_response.status_code == 404
    assert get_deleted_response.json()["detail"] == "product not found"


@pytest.mark.parametrize("method", ["GET", "PUT", "DELETE"])
def test_product_not_found_cases(test_client: TestClient, method: str) -> None:
    payload = {"name": "X", "description": "Y", "price": 1, "currency": "TWD", "sale_limit": 1}
    response = test_client.request(method, "/product/99999", json=payload if method == "PUT" else None)

    assert response.status_code == 404
    assert response.json()["detail"] == "product not found"
