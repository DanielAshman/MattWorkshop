from concurrent.futures import ThreadPoolExecutor


def favourite(client, headers, catalog_item_id):
    return client.put(f"/api/favourites/{catalog_item_id}", headers=headers)


def favourite_ids(client, headers):
    response = client.get("/api/favourites", headers=headers)
    assert response.status_code == 200, response.text
    return [item["id"] for item in response.json()]


def test_saved_product_appears_in_favourites(client, demo_headers):
    response = favourite(client, demo_headers, 3)

    assert response.status_code == 200, response.text
    assert favourite_ids(client, demo_headers) == [3]


def test_favourites_are_listed_newest_first(client, demo_headers):
    for catalog_item_id in (1, 5, 2):
        favourite(client, demo_headers, catalog_item_id)

    assert favourite_ids(client, demo_headers) == [2, 5, 1]


def test_saving_a_favourite_twice_keeps_one_copy(client, demo_headers):
    favourite(client, demo_headers, 3)
    response = favourite(client, demo_headers, 3)

    assert response.status_code == 200, response.text
    assert favourite_ids(client, demo_headers) == [3]


def test_shoppers_only_see_their_own_favourites(client, demo_headers):
    other = client.post(
        "/api/auth/register",
        json={"email": "other@example.com", "password": "secret123"},
    ).json()
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}
    favourite(client, demo_headers, 3)

    assert favourite_ids(client, other_headers) == []


def test_unknown_product_cannot_be_saved(client, demo_headers):
    response = favourite(client, demo_headers, 99999)

    assert response.status_code == 404
    assert favourite_ids(client, demo_headers) == []


def test_favourites_require_a_signed_in_shopper(client, anon_headers):
    assert client.get("/api/favourites", headers=anon_headers).status_code == 401
    assert favourite(client, anon_headers, 3).status_code == 401


def unfavourite(client, headers, catalog_item_id):
    return client.delete(f"/api/favourites/{catalog_item_id}", headers=headers)


def test_removed_favourite_no_longer_appears(client, demo_headers):
    favourite(client, demo_headers, 1)
    favourite(client, demo_headers, 3)

    response = unfavourite(client, demo_headers, 1)

    assert response.status_code == 200, response.text
    assert favourite_ids(client, demo_headers) == [3]


def test_removing_a_product_that_is_not_a_favourite_changes_nothing(client, demo_headers):
    favourite(client, demo_headers, 3)

    response = unfavourite(client, demo_headers, 1)

    assert response.status_code == 200, response.text
    assert favourite_ids(client, demo_headers) == [3]


def test_removing_a_favourite_requires_a_signed_in_shopper(client, anon_headers):
    assert unfavourite(client, anon_headers, 3).status_code == 401


def test_a_sixth_favourite_is_refused_and_the_first_five_are_kept(client, demo_headers):
    for catalog_item_id in (1, 2, 3, 4, 5):
        favourite(client, demo_headers, catalog_item_id)

    response = favourite(client, demo_headers, 6)

    assert response.status_code == 409
    assert response.json()["detail"] == "You can have up to 5 favourites"
    assert favourite_ids(client, demo_headers) == [5, 4, 3, 2, 1]


def test_removing_a_favourite_frees_a_slot(client, demo_headers):
    for catalog_item_id in (1, 2, 3, 4, 5):
        favourite(client, demo_headers, catalog_item_id)
    unfavourite(client, demo_headers, 1)

    response = favourite(client, demo_headers, 6)

    assert response.status_code == 200, response.text
    assert favourite_ids(client, demo_headers) == [6, 5, 4, 3, 2]


def test_saving_an_existing_favourite_at_the_limit_is_not_refused(client, demo_headers):
    for catalog_item_id in (1, 2, 3, 4, 5):
        favourite(client, demo_headers, catalog_item_id)

    response = favourite(client, demo_headers, 3)

    assert response.status_code == 200, response.text
    assert favourite_ids(client, demo_headers) == [5, 4, 3, 2, 1]


def test_simultaneous_saves_cannot_exceed_the_limit(client, demo_headers):
    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(lambda item_id: favourite(client, demo_headers, item_id), range(1, 11)))

    assert len(favourite_ids(client, demo_headers)) == 5
