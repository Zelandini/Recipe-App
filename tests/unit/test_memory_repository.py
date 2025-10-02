import pytest
from datetime import datetime
from recipe.adapters.memory_repository import populate
from recipe.adapters.memory_repository import MemoryRepository
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.category import Category
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.domainmodel.author import Author


class MockUser:
    def __init__(self, user_id, username, name):
        self.id = user_id
        self.username = username
        self.name = name

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


@pytest.fixture
def repository():
    return MemoryRepository()


@pytest.fixture
def sample_author():
    return Author(1, "Gordon Ramsay")


@pytest.fixture
def sample_category():
    return Category("Italian", [], 1)


@pytest.fixture
def sample_nutrition():
    return Nutrition(1, 250.0, 8.0, 3.0, 15.0, 120.0, 35.0, 5.0, 12.0, 10.0)


@pytest.fixture
def sample_recipe(sample_author, sample_category, sample_nutrition):
    return Recipe(
        recipe_id=1,
        name="Spaghetti Carbonara",
        author=sample_author,
        cook_time=20,
        preparation_time=15,
        description="Classic Italian pasta dish",
        images=["carbonara.jpg"],
        category=sample_category,
        ingredient_quantities=["200g pasta", "100g bacon"],
        ingredients=["pasta", "bacon", "eggs", "cheese"],
        nutrition=sample_nutrition,
        servings="4",
        recipe_yield="4 portions",
        instructions=["Boil pasta", "Cook bacon", "Mix with eggs"]
    )


def test_repository_construction():
    repo = MemoryRepository()
    assert repo.get_total_recipe_count() == 0
    assert repo.get_all_recipes() == []


def test_add_recipe(repository, sample_recipe):
    repository.add_recipe(sample_recipe)
    assert repository.get_total_recipe_count() == 1
    assert sample_recipe in repository.get_all_recipes()


def test_add_recipe_none(repository):
    repository.add_recipe(None)
    assert repository.get_total_recipe_count() == 0


def test_add_recipe_invalid_type(repository):
    repository.add_recipe("not a recipe")
    assert repository.get_total_recipe_count() == 0


def test_add_multiple_recipes(repository, sample_author, sample_category):
    recipe1 = Recipe(1, "Apple Pie", sample_author, category=sample_category)
    recipe2 = Recipe(2, "Banana Bread", sample_author, category=sample_category)
    recipe3 = Recipe(3, "Chocolate Cake", sample_author, category=sample_category)

    repository.add_recipe(recipe1)
    repository.add_recipe(recipe2)
    repository.add_recipe(recipe3)

    assert repository.get_total_recipe_count() == 3


def test_get_recipe_by_id(repository, sample_recipe):
    repository.add_recipe(sample_recipe)
    retrieved_recipe = repository.get_recipe(1)
    assert retrieved_recipe == sample_recipe
    assert retrieved_recipe.name == "Spaghetti Carbonara"


def test_get_recipe_nonexistent_id(repository):
    result = repository.get_recipe(999)
    assert result is None


def test_get_recipe_after_multiple_adds(repository, sample_author, sample_category):
    recipe1 = Recipe(10, "Recipe One", sample_author, category=sample_category)
    recipe2 = Recipe(20, "Recipe Two", sample_author, category=sample_category)

    repository.add_recipe(recipe1)
    repository.add_recipe(recipe2)

    assert repository.get_recipe(10) == recipe1
    assert repository.get_recipe(20) == recipe2
    assert repository.get_recipe(15) is None


def test_get_all_recipes_empty(repository):
    recipes = repository.get_all_recipes()
    assert recipes == []


def test_get_all_recipes_sorted(repository, sample_author, sample_category):
    recipe1 = Recipe(1, "Zebra Cake", sample_author, category=sample_category)
    recipe2 = Recipe(2, "Apple Pie", sample_author, category=sample_category)
    recipe3 = Recipe(3, "Banana Bread", sample_author, category=sample_category)

    repository.add_recipe(recipe1)
    repository.add_recipe(recipe2)
    repository.add_recipe(recipe3)

    all_recipes = repository.get_all_recipes()
    assert len(all_recipes) == 3
    assert all_recipes[0] == recipe1
    assert all_recipes[1] == recipe2
    assert all_recipes[2] == recipe3


def test_get_recipes_by_page_first_page(repository, sample_author, sample_category):
    for i in range(1, 6):
        recipe = Recipe(i, f"Recipe {i:02d}", sample_author, category=sample_category)
        repository.add_recipe(recipe)

    page1_recipes = repository.get_recipes_by_page(1, 2)
    assert len(page1_recipes) == 2
    assert page1_recipes[0].id == 1
    assert page1_recipes[1].id == 2


def test_get_recipes_by_page_middle_page(repository, sample_author, sample_category):
    for i in range(1, 6):
        recipe = Recipe(i, f"Recipe {i:02d}", sample_author, category=sample_category)
        repository.add_recipe(recipe)

    page2_recipes = repository.get_recipes_by_page(2, 2)
    assert len(page2_recipes) == 2
    assert page2_recipes[0].id == 3
    assert page2_recipes[1].id == 4


def test_get_recipes_by_page_last_page(repository, sample_author, sample_category):
    for i in range(1, 6):
        recipe = Recipe(i, f"Recipe {i:02d}", sample_author, category=sample_category)
        repository.add_recipe(recipe)

    page3_recipes = repository.get_recipes_by_page(3, 2)
    assert len(page3_recipes) == 1
    assert page3_recipes[0].id == 5


def test_get_recipes_by_page_beyond_available(repository, sample_author, sample_category):
    recipe = Recipe(1, "Single Recipe", sample_author, category=sample_category)
    repository.add_recipe(recipe)

    page2_recipes = repository.get_recipes_by_page(2, 5)
    assert len(page2_recipes) == 0


def test_get_recipes_by_page_empty_repository(repository):
    page1_recipes = repository.get_recipes_by_page(1, 5)
    assert len(page1_recipes) == 0


def test_get_total_recipe_count_empty(repository):
    assert repository.get_total_recipe_count() == 0


def test_get_total_recipe_count_after_additions(repository, sample_author, sample_category):
    assert repository.get_total_recipe_count() == 0

    repository.add_recipe(Recipe(1, "Recipe 1", sample_author, category=sample_category))
    assert repository.get_total_recipe_count() == 1

    repository.add_recipe(Recipe(2, "Recipe 2", sample_author, category=sample_category))
    repository.add_recipe(Recipe(3, "Recipe 3", sample_author, category=sample_category))
    assert repository.get_total_recipe_count() == 3


def test_add_and_retrieve_recipe(repository, sample_author, sample_category):
    recipe = Recipe(100, "Test Recipe", sample_author, category=sample_category)
    repository.add_recipe(recipe)

    retrieved = repository.get_recipe(100)
    assert retrieved == recipe
    assert retrieved.name == "Test Recipe"


def test_add_favourite(repository, sample_recipe):
    user_id = 1
    repository.add_recipe(sample_recipe)

    repository.add_favourite(user_id, sample_recipe.id)

    favourites = repository.favourites_for_user(user_id)

    assert len(favourites) == 1
    assert sample_recipe.id in [recipe.id for recipe in favourites]


def test_remove_favourite(repository, sample_recipe):
    user_id = 1
    repository.add_recipe(sample_recipe)

    repository.add_favourite(user_id, sample_recipe.id)
    repository.remove_favourite(user_id, sample_recipe.id)

    favourites = repository.favourites_for_user(user_id)

    assert len(favourites) == 0


def test_add_review(repository, sample_recipe):
    user_id = 1
    user = MockUser(user_id=user_id, username="testuser", name="Test User")
    repository.add_user(user)

    repository.add_recipe(sample_recipe)

    repository.add_review(sample_recipe.id, user_id, 4, "Great recipe!")

    reviews = repository.reviews_for_recipe(sample_recipe.id)

    assert len(reviews) == 1
    assert reviews[0].rating == 4
    assert reviews[0].text == "Great recipe!"


def test_average_rating(repository, sample_recipe):
    user1 = MockUser(user_id=1, username="testuser1", name="Test User 1")
    user2 = MockUser(user_id=2, username="testuser2", name="Test User 2")

    repository.add_user(user1)
    repository.add_user(user2)

    repository.add_recipe(sample_recipe)
    repository.add_review(sample_recipe.id, user1.id, 4, "Good recipe!")
    repository.add_review(sample_recipe.id, user2.id, 5, "Excellent recipe!")

    avg_rating = repository.average_rating(sample_recipe.id)

    assert avg_rating == 4.5


def test_calculate_health_star_rating(repository, sample_recipe):
    sample_recipe.nutrition = Nutrition(1, 250.0, 8.0, 3.0, 15.0, 120.0, 35.0, 5.0, 12.0, 10.0)

    health_star = repository.calculate_health_star_rating(sample_recipe)

    assert health_star == 2.0


def test_search_recipes_by_name(repository, sample_recipe):
    repository.add_recipe(sample_recipe)

    results = repository.search_recipes(query="Carbonara", category="", author="", ingredient="")

    assert len(results) == 1
    assert results[0].name == "Spaghetti Carbonara"


def test_search_recipes_by_category(repository, sample_recipe):
    repository.add_recipe(sample_recipe)

    results = repository.search_recipes(query="", category="Italian", author="", ingredient="")

    assert len(results) == 1
    assert results[0].category.name == "Italian"


def test_search_recipes_by_author(repository, sample_recipe):
    repository.add_recipe(sample_recipe)

    results = repository.search_recipes(query="", category="", author="Gordon Ramsay", ingredient="")

    assert len(results) == 1
    assert results[0].author.name == "Gordon Ramsay"


def test_search_recipes_by_ingredient(repository, sample_recipe):
    repository.add_recipe(sample_recipe)

    results = repository.search_recipes(query="", category="", author="", ingredient="bacon")

    assert len(results) == 1
    assert "bacon" in [ingredient.lower() for ingredient in results[0].ingredients]


def test_calculate_health_star_rating_missing_nutrition(repository, sample_recipe):
    sample_recipe.nutrition = Nutrition(1, None, 8.0, 3.0, 15.0, 120.0, 35.0, 5.0, 12.0, 10.0)
    health_star = repository.calculate_health_star_rating(sample_recipe)

    assert health_star == "Health star rating unavailable"
