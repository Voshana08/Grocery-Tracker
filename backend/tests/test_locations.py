from app.models import StockStatus


def test_get_location_returns_its_items_as_json(client, add_item):
    item = add_item("Full cream milk 2L", "Dairy & eggs", "fridge", StockStatus.low)

    response = client.get("/api/locations/fridge")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Fridge",
        "slug": "fridge",
        "items": [
            {
                "id": item.id,
                "name": "Full cream milk 2L",
                "category": "Dairy & eggs",
                "status": "low",
            }
        ],
    }


def test_unknown_slug_is_404(client):
    response = client.get("/api/locations/not-a-real-place")

    assert response.status_code == 404
    assert response.json() == {"detail": "Location not found"}
