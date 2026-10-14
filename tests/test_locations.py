def test_location_page_shows_seeded_location(client):
    response = client.get("/t/fridge")
    assert response.status_code == 200
    assert "Fridge" in response.text


def test_unknown_slug_is_404(client):
    response = client.get("/t/not-a-real-place")
    assert response.status_code == 404
