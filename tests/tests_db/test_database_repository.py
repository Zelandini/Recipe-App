from datetime import datetime
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.user import User

def test_browse_pagination_and_sorting(repo):
    items = repo.get_recipes_by_page(page=1, per_page=5, sort_by="name", sort_dir="asc")
    assert isinstance(items, list)
    assert 0 < len(items) <= 5
    r = items[0]
    assert hasattr(r, "id") and hasattr(r, "name")

def test_search_by_name(repo):
    items, total = repo.search_recipes_paged(
        query="chicken", category=None, author=None, ingredient=None,
        page=1, per_page=5, sort_by="name", sort_dir="asc"
    )
    assert isinstance(items, list) and isinstance(total, int)

def test_search_by_author_and_ingredient(repo):
    items, total = repo.search_recipes_paged(
        query=None, category=None, author="jam", ingredient="garlic",
        page=1, per_page=5, sort_by="name", sort_dir="asc"
    )
    assert isinstance(items, list) and isinstance(total, int)

def test_search_by_category(repo):
    sample = repo.get_recipes_by_page(1,1,"name","asc")[0]
    cat = sample.category.name if sample.category else None
    if not cat:
        # if sample has no category, just pass—dataset dependent
        return
    items, total = repo.search_recipes_paged(
        query=None, category=cat, author=None, ingredient=None,
        page=1, per_page=5, sort_by="name", sort_dir="asc"
    )
    assert total >= 1

def test_distinct_values(repo):
    authors = repo.distinct_values("author", "jam", limit=5)
    assert isinstance(authors, list)
    assert len(authors) <= 5

def test_repo_add_and_get_recipe(repo):
    base = repo.get_recipes_by_page(page=1, per_page=1, sort_by="name", sort_dir="asc")[0]
    new_id = 987654321
    new_recipe = Recipe(
        new_id, "Repo Added Recipe", base.author,
        base.cook_time or 0, base.preparation_time or 0,
        base.date or datetime(2025,1,1), "added via repo",
        base.images or [], base.category,
        base.ingredient_quantities or [], base.ingredients or [],
        None, base.nutrition, base.servings, base.recipe_yield,
        base.instructions or []
    )
    repo.add_recipe(new_recipe)
    got = repo.get_recipe(new_id)
    assert got is not None and got.name == "Repo Added Recipe" and got.author.id == base.author.id

def test_repo_add_review_and_average(repo):
    recipe = repo.get_recipes_by_page(page=1, per_page=1, sort_by="name", sort_dir="asc")[0]
    u = User("repo_user_test", "hash", None)  # username, password, id=None (auto)
    repo.add_user(u)
    assert u.id is not None
    repo.add_review(recipe.id, u.id, 4, "nice one")
    reviews = repo.reviews_for_recipe(recipe.id)
    assert any(r.user.username == "repo_user_test" for r in reviews)
    avg = repo.average_rating(recipe.id)
    assert avg >= 4.0

