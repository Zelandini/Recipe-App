# recipe/adapters/memory_repository.py
from bisect import insort_left
from typing import List, Optional, Dict, Set
import os
from datetime import datetime

from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.review import Review
from recipe.domainmodel.user import User
from recipe.adapters.repository import AbstractRepository
from recipe.adapters.datareader.csvdatareader import CSVDataReader
from recipe.domainmodel.category import Category


class MemoryRepository(AbstractRepository):
    def __init__(self):
        self.__recipe: List[Recipe] = []
        self.__user_favourites: Dict[int, Set[int]] = {}
        self.__reviews: Dict[int, List[Review]] = {}

        # Users
        self.__users_by_id: Dict[int, User] = {}
        self.__users_by_username: Dict[str, User] = {}
        self.__next_user_id: int = 1

    # ---------- Users ----------
    def add_user(self, user: User):
        if user.id is None:
            user.id = self.next_user_id()
        self.__users_by_id[user.id] = user
        self.__users_by_username[user.username] = user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.__users_by_id.get(user_id, None)

    def get_user_by_id(self, user_id: int):
        return self.get_user(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.__users_by_username.get(username, None)

    def next_user_id(self) -> int:
        user_id = self.__next_user_id
        self.__next_user_id += 1
        return user_id

    # ---------- Recipes ----------
    def add_recipe(self, recipe: Recipe):
        if isinstance(recipe, Recipe):
            insort_left(self.__recipe, recipe)

    def get_all_recipes(self) -> List[Recipe]:
        return self.__recipe

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        for recipe in self.__recipe:
            if recipe.id == recipe_id:
                return recipe
        return None

    def get_recipe_by_id(self, recipe_id):
        return self.get_recipe(recipe_id)

    def get_recipes_by_page(self, page: int, per_page: int) -> List[Recipe]:
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        return self.__recipe[start_index:end_index]

    def get_number_of_recipe(self):
        return len(self.__recipe)

    def get_total_recipe_count(self) -> int:
        return self.get_number_of_recipe()

    def search_recipes(self, query: str, category: str, author: str, ingredient: str) -> List[Recipe]:
        """
        Filter recipes by free-text query, category, author, and ingredient.
        - Category may be a Category object or a string on Recipe
        - Author may be an object with .name or a string
        - Ingredients may be list[str] or other shapes; here we assume list[str]
        """
        filtered_recipes = self.__recipe

        if query:
            q = query.lower()
            filtered_recipes = [
                r for r in filtered_recipes
                if (getattr(r, "name", "") and q in r.name.lower())
                or (getattr(r, "description", "") and q in r.description.lower())
            ]

        if category:
            c = category.lower()
            def cat_ok(r: Recipe) -> bool:
                cat_val = getattr(r, "category", None)
                if isinstance(cat_val, Category):
                    return bool(cat_val.name) and c in cat_val.name.lower()
                return bool(cat_val) and c in str(cat_val).lower()
            filtered_recipes = [r for r in filtered_recipes if cat_ok(r)]

        if author:
            a = author.lower()
            def auth_ok(r: Recipe) -> bool:
                auth = getattr(r, "author", None)
                if hasattr(auth, "name"):
                    return bool(auth.name) and a in auth.name.lower()
                return bool(auth) and a in str(auth).lower()
            filtered_recipes = [r for r in filtered_recipes if auth_ok(r)]

        if ingredient:
            ing = ingredient.lower()
            def ing_ok(r: Recipe) -> bool:
                items = getattr(r, "ingredients", None)
                if not items:
                    return False
                try:
                    return any(ing in str(x).lower() for x in items)
                except Exception:
                    return False
            filtered_recipes = [r for r in filtered_recipes if ing_ok(r)]

        return filtered_recipes

    # ---------- Reviews ----------
    def add_review(self, recipe_id: int, user_id: int, rating: int, comment: str):
        user = self.get_user_by_id(user_id)
        recipe = self.get_recipe(recipe_id)
        if not user or not recipe:
            raise ValueError("User or Recipe not found")

        timestamp = datetime.now()
        review = Review(
            review_id=len(self.__reviews) + 1,
            user=user,
            recipe=recipe,
            timestamp=timestamp,
            rating=rating,
            text=comment
        )

        if recipe_id not in self.__reviews:
            self.__reviews[recipe_id] = []
        self.__reviews[recipe_id].append(review)

    def reviews_for_recipe(self, recipe_id: int) -> List[Review]:
        reviews = self.__reviews.get(recipe_id, [])
        return [review for review in reviews if review is not None]

    def average_rating(self, recipe_id: int) -> float:
        reviews = self.reviews_for_recipe(recipe_id)
        if not reviews:
            return 0.0
        total_rating = sum([review.rating for review in reviews])
        return total_rating / len(reviews)

    # ---------- Favourites ----------
    def add_favourite(self, user_id: int, recipe_id: int):
        if user_id not in self.__user_favourites:
            self.__user_favourites[user_id] = set()
        self.__user_favourites[user_id].add(recipe_id)

    def remove_favourite(self, user_id: int, recipe_id: int):
        if user_id in self.__user_favourites and recipe_id in self.__user_favourites[user_id]:
            self.__user_favourites[user_id].remove(recipe_id)

    def favourites_for_user(self, user_id: int) -> List[Recipe]:
        if user_id not in self.__user_favourites:
            return []
        recipes: List[Recipe] = []
        for recipe_id in self.__user_favourites[user_id]:
            recipe = self.get_recipe(recipe_id)
            if recipe is not None:
                recipes.append(recipe)
        return recipes

    # ---------- Health Star ----------
    def calculate_health_star_rating(self, recipe: Recipe) -> Optional[float]:
        nutrition = getattr(recipe, "nutrition", None)
        required = ["calories", "fat", "saturated_fat", "protein", "fiber"]
        if not nutrition or any(getattr(nutrition, k, None) is None for k in required):
            return "Health star rating unavailable"

        health_star = 0.0
        if nutrition.calories <= 200:
            health_star += 1
        if nutrition.fat <= 5:
            health_star += 1
        if nutrition.saturated_fat <= 2:
            health_star += 1
        if nutrition.protein >= 10:
            health_star += 1
        if nutrition.fiber >= 5:
            health_star += 1

        return max(0.0, min(5.0, health_star))

    # ---------- Suggestions for dropdowns ----------
    def distinct_values(self, field: str, query: str = "", limit: int = 10) -> List[str]:
        field = (field or "").lower()
        allowed = {"name", "author", "category", "ingredient"}
        if field not in allowed:
            return []

        q = (query or "").lower()
        seen: Set[str] = set()

        def maybe_add(val: Optional[str]):
            if val is None:
                return
            s = str(val).strip()
            if not s:
                return
            if q and q not in s.lower():
                return
            seen.add(s)

        for r in self.get_all_recipes():
            if field == "name":
                maybe_add(getattr(r, "name", None))

            elif field == "author":
                author = getattr(r, "author", None)
                if hasattr(author, "name"):
                    maybe_add(getattr(author, "name", None))
                else:
                    maybe_add(author if author is None else str(author))

            elif field == "category":
                cat = getattr(r, "category", None)
                if isinstance(cat, Category):
                    maybe_add(getattr(cat, "name", None))
                else:
                    maybe_add(cat if cat is None else str(cat))

            elif field == "ingredient":
                items = getattr(r, "ingredients", None)
                if not items:
                    items = getattr(r, "ingredient_quantities", None)
                if isinstance(items, (list, tuple)):
                    for it in items:
                        if isinstance(it, str):
                            maybe_add(it)
                        else:
                            name = getattr(it, "ingredient", None) or getattr(it, "name", None)
                            if name is None and isinstance(it, dict):
                                name = it.get("ingredient") or it.get("name")
                            maybe_add(name)

            # Soft early-stop if we've already found enough
            if len(seen) >= max(0, limit):
                break

        return sorted(seen, key=str.casefold)[: max(0, limit)]


# --------- Populate helper (unchanged except for imports) ---------
def populate(repo: AbstractRepository):
    """
    Load recipes from CSV and add a few demo users.
    """
    dir_name = os.path.dirname(os.path.abspath(__file__))
    recipe_file_name = os.path.join(dir_name, "data", "recipes.csv")
    reader = CSVDataReader(recipe_file_name)
    reader.read_csv_file()

    for recipe in reader.recipes:
        repo.add_recipe(recipe)

    from werkzeug.security import generate_password_hash
    from recipe.domainmodel.user import User

    demo_user = User("demo", generate_password_hash("demo123"))
    admin_user = User("admin", generate_password_hash("admin"))
    test_user = User("test", generate_password_hash("password123"))

    repo.add_user(demo_user)
    repo.add_user(admin_user)
    repo.add_user(test_user)
