# tests/e2e/test_e2e.py
import pytest
from recipe import create_app

@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return app

@pytest.fixture()
def client(app):
    return app.test_client()

def _first_recipe_id(app):
    recipes = app.repository.get_all_recipes()
    assert recipes, "Repository should be populated in create_app.populate(...)"
    return recipes[0].id, recipes[0].name

def test_register_login_logout_flow(client, app):
    # Register
    r = client.post(
        "/authentication/register",
        data={"username": "e2e_user", "password": "ValidPass123", "confirm": "ValidPass123"},
        follow_redirects=True,
    )
    assert r.status_code == 200

    # Login
    r = client.post(
        "/authentication/login",
        data={"username": "e2e_user", "password": "ValidPass123"},
        follow_redirects=True,
    )
    assert r.status_code == 200

    # Logout
    r = client.get("/authentication/logout", follow_redirects=True)
    assert r.status_code == 200

def test_review_requires_login_and_then_succeeds(client, app):
    recipe_id, _ = _first_recipe_id(app)

    # Not logged in -> should redirect to login
    r = client.post(f"/reviews/add/{recipe_id}", data={"rating": "5", "comment": "Great recipe!!!"}, follow_redirects=False)
    assert r.status_code in (302, 303)

    # Register + login
    client.post("/authentication/register",
                data={"username": "e2e_reviewer", "password": "ValidPass123", "confirm": "ValidPass123"},
                follow_redirects=True)
    client.post("/authentication/login",
                data={"username": "e2e_reviewer", "password": "ValidPass123"},
                follow_redirects=True)

    # Post a valid review
    r = client.post(
        f"/reviews/add/{recipe_id}",
        data={"rating": "5", "comment": "Absolutely delicious recipe!"},
        follow_redirects=True,
    )
    assert r.status_code == 200

    # Verify via repository that a review was stored
    reviews = app.repository.reviews_for_recipe(recipe_id)
    assert any(getattr(rv, "rating", None) == 5 for rv in reviews)

def test_search_and_favourite_flow(client, app):
    recipe_id, recipe_name = _first_recipe_id(app)

    # Register + login
    client.post("/authentication/register",
                data={"username": "e2e_fav", "password": "ValidPass123", "confirm": "ValidPass123"},
                follow_redirects=True)
    client.post("/authentication/login",
                data={"username": "e2e_fav", "password": "ValidPass123"},
                follow_redirects=True)

    r = client.get("/browse/?query=a", follow_redirects=True)
    assert r.status_code == 200

    # Add favourite
    r = client.post(f"/favourites/add/{recipe_id}", follow_redirects=True)
    assert r.status_code == 200

    # List favourites – ensure recipe shows up
    r = client.get("/favourites/list", follow_redirects=True)
    assert r.status_code == 200
    assert recipe_name in r.get_data(as_text=True)
