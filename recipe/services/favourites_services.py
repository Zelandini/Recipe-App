# recipe/services/favourites_services.py
from recipe.adapters.repository import AbstractRepository
from typing import List
from recipe.domainmodel.recipe import Recipe


def add_favourite(user_id: int, recipe_id: int, repo: AbstractRepository) -> bool:
    """Add a recipe to user's favourites.
    Returns True if newly added, False if it was already a favourite."""
    # Verify user and recipe exist
    user = repo.get_user(user_id)
    recipe = repo.get_recipe(recipe_id)
    if not user or not recipe:
        raise ValueError("User or Recipe not found")

    # Check existing to give accurate UI feedback (DB uniqueness also protects)
    current = repo.favourites_for_user(user_id)
    if any(r.id == recipe_id for r in current if r):
        return False  # already favourited

    repo.add_favourite(user_id, recipe_id)
    return True


def remove_favourite(user_id: int, recipe_id: int, repo: AbstractRepository) -> bool:
    """Remove a recipe from user's favourites.
    Returns True if removed, False if it wasn't a favourite."""
    current = repo.favourites_for_user(user_id)
    if not any(r.id == recipe_id for r in current if r):
        return False  # nothing to remove

    repo.remove_favourite(user_id, recipe_id)
    return True


def get_user_favourites(user_id: int, repo: AbstractRepository) -> List[Recipe]:
    """Get all favourite recipes for a user."""
    return repo.favourites_for_user(user_id)


def is_favourite(user_id: int, recipe_id: int, repo: AbstractRepository) -> bool:
    favourites = repo.favourites_for_user(user_id)
    return any(recipe and recipe.id == recipe_id for recipe in favourites)


def get_favourites_count(user_id: int, repo: AbstractRepository) -> int:
    favourites = repo.favourites_for_user(user_id)
    return sum(1 for r in favourites if r)
