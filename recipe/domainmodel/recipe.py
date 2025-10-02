from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from recipe.domainmodel.author import Author
    from recipe.domainmodel.category import Category

from datetime import datetime

from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.review import Review

class Recipe:
    def __init__(self, recipe_id: int, name: str, author: "Author",
                 cook_time: int = 0,
                 preparation_time: int = 0,
                 created_date: datetime = None,
                 description: str = "",
                 images: list[str] = None,
                 category: "Category" = None,
                 ingredient_quantities: list[str] = None,
                 ingredients: list[str] = None,
                 rating: float | None = None,
                 nutrition: "Nutrition" = None,
                 servings: str | None = None,
                 recipe_yield: str | None = None,
                 instructions: list[str] = None):

        if not isinstance(recipe_id, int) or recipe_id <= 0:
            raise ValueError("id must be a positive int.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string.")
        if author is None:
            raise ValueError("author is required.")

        self.__id = recipe_id
        self.__name = name
        self.__author = author
        self.__cook_time = cook_time
        self.__preparation_time = preparation_time
        self.__date = created_date if created_date else datetime.now()
        self.__description = description
        self.__images = images if images else []
        self.__category = category
        self.__ingredient_quantities = ingredient_quantities if ingredient_quantities else []
        self.__ingredients = ingredients if ingredients else []
        self.__rating = rating
        self.__nutrition = nutrition
        self.__servings = servings if servings else "Not specified"
        self.__recipe_yield = recipe_yield if recipe_yield else "Not specified"
        self.__instructions = instructions if instructions else []
        self.__reviews = []

    def __repr__(self) -> str:
        return (f"<Recipe {self.__name} with id: {self.id} was created by {self.__author.name} "
            f"on {self.__date}>")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Recipe):
            return False
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Recipe):
            raise TypeError("Comparison must be between Recipe instances")
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.__id)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def author(self) -> "Author":
        return self.__author

    @property
    def cook_time(self) -> int:
        return self.__cook_time

    @cook_time.setter
    def cook_time(self, value: int):
        if value < 0:
            raise ValueError("Cook time cannot be negative.")
        self.__cook_time = value

    @property
    def preparation_time(self) -> int:
        return self.__preparation_time

    @preparation_time.setter
    def preparation_time(self, value: int):
        if value < 0:
            raise ValueError("Preparation time cannot be negative.")
        self.__preparation_time = value

    @property
    def date(self) -> datetime:
        return self.__date

    @date.setter
    def date(self, value: datetime):
        if not isinstance(value, datetime):
            raise TypeError("date must be a datetime.")
        self.__date = value

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, text: str):
        self.__description = text.strip()

    @property
    def images(self) -> list[str]:
        return self.__images

    @images.setter
    def images(self, value: list[str]):
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise TypeError("images must be a list of strings.")
        self.__images = value

    @property
    def category(self) -> "Category":
        return self.__category

    @category.setter
    def category(self, value: "Category"):
        self.__category = value

    @property
    def ingredient_quantities(self) -> list[str]:
        return self.__ingredient_quantities

    @property
    def ingredients(self) -> list[str]:
        return self.__ingredients

    @property
    def rating(self) -> float | None:
        return self.__rating

    @rating.setter
    def rating(self, value: float):
        if value is not None and (value < 0 or value > 5):
            raise ValueError("Rating must be between 0 and 5.")
        self.__rating = value

    @property
    def nutrition(self) -> "Nutrition":
        return self.__nutrition

    @nutrition.setter
    def nutrition(self, value: "Nutrition"):
        self.__nutrition = value

    @property
    def servings(self) -> str:
        return self.__servings

    @servings.setter
    def servings(self, value: str):
        self.__servings = value if value else "Not specified"

    @property
    def recipe_yield(self) -> str:
        return self.__recipe_yield

    @recipe_yield.setter
    def recipe_yield(self, value: str):
        self.__recipe_yield = value if value else "Not specified"

    @property
    def instructions(self) -> list[str]:
        return self.__instructions

    @instructions.setter
    def instructions(self, steps: list[str]):
        if not isinstance(steps, list):
            raise ValueError("Instructions must be provided as a list of strings.")
        self.__instructions = steps

    @property
    def reviews(self) -> list[Review]:
        return self.__reviews

    def add_review(self, review: Review) -> None:
        if isinstance(review, Review):
            self.__reviews.append(review)
            self.__update_rating()
        else:
            raise TypeError("Expected a Review instance")

    def remove_review(self, review: Review) -> None:
        if review in self.__reviews:
            self.__reviews.remove(review)
            self.__update_rating()
        else:
            raise ValueError("Review not found in recipe's reviews")

    def __update_rating(self) -> None:
        if self.__reviews:
            ratings = [r.rating for r in self.__reviews if
                       hasattr(r, "rating") and r.rating is not None]
            if ratings:
                average_rating = sum(ratings) / len(ratings)
                self.__rating = round(average_rating, 1)
            else:
                self.__rating = None
        else:
            self.__rating = None