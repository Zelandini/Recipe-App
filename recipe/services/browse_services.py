import math
from typing import List, Tuple
from recipe.adapters.repository import AbstractRepository


def get_recipes_by_page(repo: AbstractRepository, page: int, per_page: int):
    total_recipes = repo.get_total_recipe_count()
    total_pages = math.ceil(total_recipes / per_page) if total_recipes > 0 else 1

    # If page is beyond available pages, return empty
    if page > total_pages:
        return [], total_pages, total_recipes

    # Only clamp to minimum of 1
    page = max(1, page)

    recipes = repo.get_recipes_by_page(page, per_page)
    return recipes, total_pages, total_recipes