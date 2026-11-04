from datetime import UTC, datetime

from app.models import StockStatus
from app.services.inventory import get_location_by_slug, list_location_items, set_status


def test_lists_only_this_locations_items_in_name_order(session, add_item):
    add_item("Yoghurt", "Dairy & eggs", "fridge", StockStatus.plenty)
    add_item("Butter", "Dairy & eggs", "fridge", StockStatus.out)
    add_item("Basmati rice 1kg", "Pantry staples", "pantry", StockStatus.low)

    items = list_location_items(session, get_location_by_slug(session, "fridge"))

    assert [(i.name, i.category, i.status) for i in items] == [
        ("Butter", "Dairy & eggs", StockStatus.out),
        ("Yoghurt", "Dairy & eggs", StockStatus.plenty),
    ]


def test_location_with_no_items_is_an_empty_list(session):
    assert list_location_items(session, get_location_by_slug(session, "cleaning")) == []


def test_unknown_slug_finds_no_location(session):
    assert get_location_by_slug(session, "garage") is None


def test_set_status_changes_status_and_updated_at(session, add_item):
    item = add_item("Butter", "Dairy & eggs", "fridge", StockStatus.plenty)
    item.updated_at = datetime(2026, 1, 1, tzinfo=UTC)
    session.add(item)
    session.commit()

    result = set_status(session, item.id, StockStatus.out)

    session.refresh(item)
    assert result.status == StockStatus.out
    assert (result.name, result.category) == ("Butter", "Dairy & eggs")
    assert item.status == StockStatus.out
    assert item.updated_at > datetime(2026, 1, 1, tzinfo=UTC)


def test_set_status_on_unknown_item_returns_none(session):
    assert set_status(session, 999, StockStatus.low) is None


def test_patch_status_returns_the_updated_item(client, add_item):
    item = add_item("Eggs 12 pack", "Dairy & eggs", "fridge", StockStatus.plenty)

    response = client.patch(f"/api/inventory/{item.id}", json={"status": "low"})

    assert response.status_code == 200
    assert response.json() == {
        "id": item.id,
        "name": "Eggs 12 pack",
        "category": "Dairy & eggs",
        "status": "low",
    }
    assert client.get("/api/locations/fridge").json()["items"][0]["status"] == "low"


def test_patch_with_a_made_up_status_is_rejected(client, add_item):
    item = add_item("Eggs 12 pack", "Dairy & eggs", "fridge", StockStatus.plenty)

    response = client.patch(f"/api/inventory/{item.id}", json={"status": "half"})

    assert response.status_code == 422


def test_patch_unknown_item_is_404(client):
    response = client.patch("/api/inventory/999", json={"status": "low"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Item not found"}


def test_removing_an_item_keeps_the_product_and_past_trips(client, add_item):
    item = add_item("Butter", "Dairy & eggs", "fridge", StockStatus.low)
    trip = {
        "store": "Aldi",
        "trip_date": "2026-11-04",
        "items": [
            {
                "product_name": "Butter",
                "category_id": 3,
                "location_slug": "fridge",
                "price_cents": 450,
            }
        ],
    }
    trip_id = client.post("/api/trips", json=trip).json()["id"]

    assert client.delete(f"/api/inventory/{item.id}").status_code == 204

    assert client.get("/api/locations/fridge").json()["items"] == []
    assert [p["name"] for p in client.get("/api/products").json()] == ["Butter"]
    assert client.get(f"/api/trips/{trip_id}").json()["total_cents"] == 450

    # Buying it again puts it back, because saving a trip restocks home.
    client.post("/api/trips", json=trip)
    assert [i["name"] for i in client.get("/api/locations/fridge").json()["items"]] == ["Butter"]


def test_delete_unknown_item_is_404(client):
    assert client.delete("/api/inventory/999").status_code == 404
