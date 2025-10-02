# recipe/adapters/repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review


class AbstractRepository(ABC):
    @abstractmethod
    def add_recipe(self, recipe: Recipe):
        raise NotImplementedError

    @abstractmethod
    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        raise NotImplementedError

    @abstractmethod
    def get_all_recipes(self) -> List[Recipe]:
        raise NotImplementedError

    @abstractmethod
    def get_recipes_by_page(self, page: int, per_page: int) -> List[Recipe]:
        raise NotImplementedError

    @abstractmethod
    def get_total_recipe_count(self) -> int:
        raise NotImplementedError

    # NOTE: Keeping your project’s existing search signature.
    @abstractmethod
    def search_recipes(self, query: str, category: str, author: str, ingredient: str) -> List[Recipe]:
        raise NotImplementedError

    @abstractmethod
    def add_favourite(self, user_id: int, recipe_id: int):
        raise NotImplementedError

    @abstractmethod
    def remove_favourite(self, user_id: int, recipe_id: int):
        raise NotImplementedError

    @abstractmethod
    def favourites_for_user(self, user_id: int) -> List[Recipe]:
        raise NotImplementedError

    @abstractmethod
    def add_review(self, recipe_id: int, user_id: int, rating: int, comment: str):
        raise NotImplementedError

    @abstractmethod
    def reviews_for_recipe(self, recipe_id: int) -> List[Review]:
        raise NotImplementedError

    @abstractmethod
    def average_rating(self, recipe_id: int) -> float:
        raise NotImplementedError

    @abstractmethod
    def calculate_health_star_rating(self, recipe: Recipe) -> Optional[float]:
        raise NotImplementedError

    # NEW: used by /api/browse/options for short, searchable dropdowns
    @abstractmethod
    def distinct_values(self, field: str, query: str = "", limit: int = 10) -> List[str]:
        """Return up to `limit` distinct values for a field ('name', 'author', 'category', 'ingredient'),
        filtered by case-insensitive substring `query`."""
        raise NotImplementedError
