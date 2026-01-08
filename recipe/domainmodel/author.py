class Author:
    def __init__(self, author_id: int, name: str, recipes: list["Recipe"] = None):
        self.__id = author_id
        self.__name = name
        self.__recipes = recipes if recipes is not None else []

    def __repr__(self) -> str:
        return f"<Author {self.id}: {self.name}>"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Author):
            return False
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Author):
            raise TypeError("Comparison must be between Author instances")
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def id(self) -> int:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def recipes(self) -> list["Recipe"]:
        return self.__recipes

    def add_recipe(self, recipe: "Recipe") -> None:
        from recipe.domainmodel.recipe import Recipe
        if not isinstance(recipe, Recipe):
            raise TypeError("Expected a Recipe instance")
        if recipe in self.__recipes:
            return

        self.__recipes.append(recipe)

