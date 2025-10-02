from datetime import datetime
# from recipe.domainmodel.user import User
# from recipe.domainmodel.recipe import Recipe


class Review:
    def __init__(self, review_id: int, user: "User", recipe: 'Recipe', timestamp: datetime, rating: int, text: str = ""):
        self.__id = review_id
        self.__user = user
        self.__recipe = recipe
        self.__timestamp = timestamp
        self.__rating = rating
        self.__text = text

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user(self) -> 'User':
        return self.__user

    @property
    def recipe(self) -> 'Recipe':
        return self.__recipe

    @property
    def timestamp(self) -> datetime:
        return self.__timestamp

    @property
    def rating(self) -> int:
        return self.__rating

    @property
    def text(self) -> str:
        return self.__text

    def __repr__(self) -> str:
        return f"<Review {self.id}: user={self.user.id}, recipe={self.recipe.id}, rating={self.rating}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Review):
            return False
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Review):
            raise TypeError("Comparison must be between Review instances")
        # first by timestamp, then by id
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)
