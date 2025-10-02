import pytest
from recipe.services.recipe_services import (
    get_recipe_by_id, get_all_recipes, get_featured_recipes, get_recipe_of_the_day
)
from recipe.services.browse_services import get_recipes_by_page
from recipe.adapters.memory_repository import MemoryRepository
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category


# Fixtures
@pytest.fixture
def empty_repository():
    return MemoryRepository()


@pytest.fixture
def populated_repository():
    repo = MemoryRepository()
    author = Author(1, "Jamie Oliver")
    category = Category("Main Course", [], 1)

    recipes = [
        Recipe(1, "Apple Pie", author, category=category),
        Recipe(2, "Banana Bread", author, category=category),
        Recipe(3, "Chocolate Cake", author, category=category),
        Recipe(4, "Dinner Roll", author, category=category),
        Recipe(5, "Egg Salad", author, category=category)
    ]

    for recipe in recipes:
        repo.add_recipe(recipe)

    return repo


# Recipe services tests
def test_get_recipe_by_id_success(populated_repository):
    recipe = get_recipe_by_id(populated_repository, 1)
    assert recipe is not None
    assert recipe.name == "Apple Pie"
    assert recipe.id == 1


def test_get_recipe_by_id_not_found(populated_repository):
    recipe = get_recipe_by_id(populated_repository, 999)
    assert recipe is None


def test_get_recipe_by_id_empty_repository(empty_repository):
    recipe = get_recipe_by_id(empty_repository, 1)
    assert recipe is None


def test_get_all_recipes_success(populated_repository):
    recipes = get_all_recipes(populated_repository)
    assert len(recipes) == 5


def test_get_all_recipes_empty_repository(empty_repository):
    recipes = get_all_recipes(empty_repository)
    assert recipes == []


def test_get_featured_recipes_normal_count(populated_repository):
    featured = get_featured_recipes(populated_repository, count=3)
    assert len(featured) == 3
    # Can't predict which recipes due to randomness
    all_recipes = get_all_recipes(populated_repository)
    for recipe in featured:
        assert recipe in all_recipes


def test_get_featured_recipes_more_than_available(populated_repository):
    featured = get_featured_recipes(populated_repository, count=10)
    assert len(featured) == 5


def test_get_featured_recipes_empty_repository(empty_repository):
    featured = get_featured_recipes(empty_repository, count=3)
    assert featured == []


def test_get_recipe_of_the_day_success(populated_repository):
    recipe_of_day = get_recipe_of_the_day(populated_repository)
    assert recipe_of_day is not None
    # Can't predict which recipe due to randomness, just verify it's valid
    all_recipes = get_all_recipes(populated_repository)
    assert recipe_of_day in all_recipes


def test_get_recipe_of_the_day_empty_repository(empty_repository):
    recipe_of_day = get_recipe_of_the_day(empty_repository)
    assert recipe_of_day is None


# Browse services tests
def test_get_recipes_by_page_first_page(populated_repository):
    recipes, total_pages, total_recipes = get_recipes_by_page(populated_repository, page=1, per_page=3)

    assert len(recipes) == 3
    assert total_pages == 2  # 5 recipes / 3 per page = 2 pages
    assert total_recipes == 5


def test_get_recipes_by_page_last_page(populated_repository):
    recipes, total_pages, total_recipes = get_recipes_by_page(populated_repository, page=2, per_page=3)

    assert len(recipes) == 2  # Last 2 recipes
    assert total_pages == 2
    assert total_recipes == 5


def test_get_recipes_by_page_beyond_available(populated_repository):
    recipes, total_pages, total_recipes = get_recipes_by_page(populated_repository, page=3, per_page=3)

    assert len(recipes) == 0
    assert total_pages == 2
    assert total_recipes == 5


def test_get_recipes_by_page_empty_repository(empty_repository):
    recipes, total_pages, total_recipes = get_recipes_by_page(empty_repository, page=1, per_page=3)

    assert len(recipes) == 0
    assert total_pages == 1
    assert total_recipes == 0