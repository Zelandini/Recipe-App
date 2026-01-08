import random
import datetime
from typing import Optional, List
from recipe.adapters.repository import AbstractRepository
from recipe.domainmodel.recipe import Recipe

def get_recipe_by_id(repo: AbstractRepository, recipe_id: int) -> Optional[Recipe]:
    return repo.get_recipe(recipe_id)

def get_all_recipes(repo: AbstractRepository) -> List[Recipe]:
    return repo.get_all_recipes()


def get_featured_recipes(repo: AbstractRepository, count: int = 3) -> List[Recipe]:
    all_recipes = repo.get_all_recipes()
    if not all_recipes:
        return []

    today = datetime.date.today().isoformat()
    random.seed(today + "featured")

    return random.sample(all_recipes, min(count, len(all_recipes)))

def get_recipe_of_the_day(repo: AbstractRepository) -> Optional[Recipe]:
    all_recipes = repo.get_all_recipes()
    if not all_recipes:
        return None

    today = datetime.date.today().isoformat()
    random.seed(today)

    return random.choice(all_recipes)