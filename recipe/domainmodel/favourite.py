class Favourite:
    def __init__(self, favourite_id: int, user: "User", recipe: "Recipe"):
        self.__id = favourite_id
        self.__user = user
        self.__recipe = recipe

    @property
    def id(self) -> int:
        return self.__id

    @property
    def user(self) -> "User":
        return self.__user

    @property
    def recipe(self) -> "Recipe":
        return self.__recipe

    def __repr__(self) -> str:
        return f"<Favourite {self.id}: user={self.user.id}, recipe={self.recipe.id}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Favourite):
            return False
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Favourite):
            raise TypeError("Comparison must be between Favourite instances")
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)