import pytest
from sqlmodel import select

from app.models import Category, InventoryItem, Product, StockStatus
from app.services.inventory import InvalidChoice, add_item


def category_id(session, name):
    return session.exec(select(Category).where(Category.name == name)).one().id


def test_add_item_creates_product_and_inventory_item(session):
    dairy = category_id(session, "Dairy & eggs")

    item = add_item(session, "Greek yoghurt 1kg", dairy, "fridge", StockStatus.low)

    assert (item.name, item.category, item.status) == ("Greek yoghurt 1kg", "Dairy & eggs", "low")
    product = session.exec(select(Product)).one()
    assert product.default_location_id is not None
    assert session.get(InventoryItem, item.id).product_id == product.id


def test_add_item_reuses_a_product_whatever_its_capitals(session):
    dairy = category_id(session, "Dairy & eggs")
    add_item(session, "Butter", dairy, "fridge", StockStatus.plenty)

    item = add_item(session, "butter", dairy, "pantry", StockStatus.plenty)

    assert item.name == "Butter"
    assert len(session.exec(select(Product)).all()) == 1
    assert len(session.exec(select(InventoryItem)).all()) == 2


def test_adding_an_item_already_in_that_place_updates_its_status(session):
    dairy = category_id(session, "Dairy & eggs")
    first = add_item(session, "Butter", dairy, "fridge", StockStatus.plenty)

    again = add_item(session, "BUTTER", dairy, "fridge", StockStatus.out)

    assert again.id == first.id
    assert again.status == StockStatus.out
    assert len(session.exec(select(InventoryItem)).all()) == 1


def test_add_item_with_unknown_location_or_category_is_refused(session):
    dairy = category_id(session, "Dairy & eggs")
    with pytest.raises(InvalidChoice) as error:
        add_item(session, "Butter", dairy, "garage", StockStatus.plenty)
    assert error.value.loc == ("location_slug",)

    with pytest.raises(InvalidChoice) as error:
        add_item(session, "Butter", 999, "fridge", StockStatus.plenty)
    assert error.value.loc == ("category_id",)


def test_post_item_then_it_appears_on_the_location_page(client, session):
    body = {
        "product_name": "  Basmati rice 1kg ",
        "category_id": category_id(session, "Pantry staples"),
        "location_slug": "pantry",
    }

    response = client.post("/api/items", json=body)

    assert response.status_code == 200
    assert response.json()["name"] == "Basmati rice 1kg"  # spaces trimmed
    assert response.json()["status"] == "plenty"  # the default
    items = client.get("/api/locations/pantry").json()["items"]
    assert [i["name"] for i in items] == ["Basmati rice 1kg"]


def test_post_item_with_a_blank_name_is_422(client, session):
    body = {"product_name": "   ", "category_id": 1, "location_slug": "fridge"}

    response = client.post("/api/items", json=body)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "product_name"]


def test_post_item_with_an_unknown_category_is_422_on_that_field(client):
    body = {"product_name": "Butter", "category_id": 999, "location_slug": "fridge"}

    response = client.post("/api/items", json=body)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "category_id"]


def test_lists_for_the_form(client, session):
    add_item(
        session, "Full cream milk 2L", category_id(session, "Dairy & eggs"), "fridge", "plenty"
    )

    assert [c["name"] for c in client.get("/api/categories").json()][:2] == [
        "Fruit & veg",
        "Meat & seafood",
    ]
    assert client.get("/api/locations").json() == [
        {"name": "Fridge", "slug": "fridge"},
        {"name": "Pantry", "slug": "pantry"},
        {"name": "Cleaning cupboard", "slug": "cleaning"},
    ]
    assert [p["name"] for p in client.get("/api/products?search=MILK").json()] == [
        "Full cream milk 2L"
    ]
    assert client.get("/api/products?search=rice").json() == []
