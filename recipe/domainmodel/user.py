from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.review import Review


class User:
    def __init__(self, username: str, password: str, user_id: int = None):
        self.__id = user_id
        self.__username = username
        self.__password = password
        self.__favourite_recipes = []
        self.__reviews = []

    def __repr__(self) -> str:
        return f"<User {self.id}: {self.username}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        # Handle cases where IDs might be None
        if self.id is None or other.id is None:
            return self.username == other.username
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, User):
            raise TypeError("Comparison must be between User instances")
        # Handle cases where IDs might be None
        if self.id is None and other.id is None:
            return self.username < other.username
        if self.id is None:
            return True
        if other.id is None:
            return False
        return self.id < other.id

    def __hash__(self) -> int:
        # Use username for hashing if ID is None
        if self.id is not None:
            return hash(self.id)
        return hash(self.username)

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, user_id: int):
        if user_id is not None and (type(user_id) is not int or user_id < 0):
            raise ValueError("User ID must be a positive integer or None")
        self.__id = user_id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def password(self) -> str:
        return self.__password

    @property
    def favourite_recipes(self) -> list["Favourite"]:
        return self.__favourite_recipes

    @property
    def reviews(self) -> list["Review"]:
        return self.__reviews

    def add_favourite_recipe(self, recipe: "Favourite") -> None:
        if not isinstance(recipe, Favourite):
            raise TypeError("Expected a Favourite instance")
        if recipe not in self.__favourite_recipes:
            self.__favourite_recipes.append(recipe)
        else:
            raise ValueError("Recipe already in user's favourites")

    def remove_favourite_recipe(self, recipe: "Favourite") -> None:
        if recipe in self.__favourite_recipes:
            self.__favourite_recipes.remove(recipe)
        else:
            raise ValueError("Recipe not found in user's favourites")

    def add_review(self, review: "Review") -> None:
        if not isinstance(review, Review):
            raise TypeError("Expected a Review instance")
        self.__reviews.append(review)

    def remove_review(self, review: "Review") -> None:
        if review in self.__reviews:
            self.__reviews.remove(review)
        else:
            raise ValueError("Review not found in user's reviews")

    def check_password(self, password: str) -> bool:
        from werkzeug.security import check_password_hash
        return check_password_hash(self.__password, password)