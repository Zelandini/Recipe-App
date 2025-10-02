# recipe/services/favourites_services.py
from recipe.adapters.repository import AbstractRepository
from typing import List
from recipe.domainmodel.recipe import Recipe


def add_favourite(user_id: int, recipe_id: int, repo: AbstractRepository):
    """Add a recipe to user's favourites"""
    # Verify user and recipe exist
    user = repo.get_user(user_id)
    recipe = repo.get_recipe(recipe_id)

    if not user or not recipe:
        raise ValueError("User or Recipe not found")

    repo.add_favourite(user_id, recipe_id)


def remove_favourite(user_id: int, recipe_id: int, repo: AbstractRepository):
    """Remove a recipe from user's favourites"""
    repo.remove_favourite(user_id, recipe_id)


def get_user_favourites(user_id: int, repo: AbstractRepository) -> List[Recipe]:
    """Get all favourite recipes for a user"""
    return repo.favourites_for_user(user_id)


def is_favourite(user_id: int, recipe_id: int, repo: AbstractRepository) -> bool:
    """Check if a recipe is in user's favourites"""
    favourites = repo.favourites_for_user(user_id)
    return any(recipe.id == recipe_id for recipe in favourites if recipe)


def get_favourites_count(user_id: int, repo: AbstractRepository) -> int:
    """Get count of user's favourite recipes"""
    favourites = repo.favourites_for_user(user_id)
    return len([recipe for recipe in favourites if recipe])