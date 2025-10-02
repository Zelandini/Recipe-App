class Nutrition:
    def __init__(self, nutrition_id: int, calories: float, fat: float,
                 saturated_fat: float, cholesterol: float, sodium: float,
                 carbohydrates: float, fiber: float, sugar: float, protein: float):
        self.__id = nutrition_id
        self.__calories = calories
        self.__fat = fat
        self.__saturated_fat = saturated_fat
        self.__cholesterol = cholesterol
        self.__sodium = sodium
        self.__carbohydrates = carbohydrates
        self.__fiber = fiber
        self.__sugar = sugar
        self.__protein = protein

    @property
    def id(self) -> int:
        return self.__id

    @property
    def calories(self) -> float:
        return self.__calories

    @property
    def fat(self) -> float:
        return self.__fat

    @property
    def saturated_fat(self) -> float:
        return self.__saturated_fat

    @property
    def cholesterol(self) -> float:
        return self.__cholesterol

    @property
    def sodium(self) -> float:
        return self.__sodium

    @property
    def carbohydrates(self) -> float:
        return self.__carbohydrates

    @property
    def fiber(self) -> float:
        return self.__fiber

    @property
    def sugar(self) -> float:
        return self.__sugar

    @property
    def protein(self) -> float:
        return self.__protein

    def __repr__(self):
        return (
            f"<Nutrition id={self.id}, "
            f"calories={self.calories}, fat={self.fat}g, sat_fat={self.saturated_fat}g, "
            f"cholesterol={self.cholesterol}mg, sodium={self.sodium}mg, "
            f"carbs={self.carbohydrates}g, fiber={self.fiber}g, sugar={self.sugar}g, "
            f"protein={self.protein}g>"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Nutrition):
            return False
        return self.id == other.id

    def __lt__(self, other) -> bool:
        if not isinstance(other, Nutrition):
            raise TypeError("Comparison must be between Nutrition instances")
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)