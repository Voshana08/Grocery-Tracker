from app.models import StockStatus
from app.services.inventory import get_location_by_slug, list_location_items


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
