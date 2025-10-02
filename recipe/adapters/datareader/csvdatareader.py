import os
import csv
import ast
from datetime import datetime
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.recipe import Recipe


class CSVDataReader:
    def __init__(self, csv_filename):
        self.__csv_filename = csv_filename
        self.__authors = {}
        self.__categories = {}
        self.__recipes = []
        self.__nutrition_id_counter = 1
        self.__category_id_counter = 1

    def read_csv_file(self):
        with open(self.__csv_filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                recipe = self._create_recipe_from_row(row)
                if recipe:
                    self.__recipes.append(recipe)

    def _create_recipe_from_row(self, row):
        try:
            recipe_id = int(row['RecipeId'])
            name = row['Name']
            author_id = int(row['AuthorId'])
            author_name = row['AuthorName']
            cook_time = int(row['CookTime'])
            prep_time = int(row['PrepTime'])
            date_pub = self.parse_date(row['DatePublished'])
            description = row['Description']
            images = ast.literal_eval(row['Images'])
            recipe_category = row['RecipeCategory']
            ingredient_quantities = ast.literal_eval(row['RecipeIngredientQuantities'])
            ingredients = [str(i).strip().capitalize() for i in ast.literal_eval(row['RecipeIngredientParts'])]
            calories = float(row['Calories'])
            fat_content = float(row['FatContent'])
            saturated_fat_content = float(row['SaturatedFatContent'])
            cholesterol = float(row['CholesterolContent'])
            sodium = float(row['SodiumContent'])
            carbohydrates = float(row['CarbohydrateContent'])
            fiber = float(row['FiberContent'])
            sugars = float(row['SugarContent'])
            protein = float(row['ProteinContent'])
            serving_size = row['RecipeServings']
            recipe_yield = row['RecipeYield']
            instructions = ast.literal_eval(row['RecipeInstructions'])

            author = self._get_create_author(author_id, author_name)
            category = self._get_create_category(recipe_category)

            nutrition = Nutrition(
                nutrition_id=self.__nutrition_id_counter,
                calories=calories,
                fat=fat_content,
                saturated_fat=saturated_fat_content,
                cholesterol=cholesterol,
                sodium=sodium,
                carbohydrates=carbohydrates,
                fiber=fiber,
                sugar=sugars,
                protein=protein
            )
            self.__nutrition_id_counter += 1

            recipe = Recipe(
                recipe_id=recipe_id,
                name=name,
                author=author,
                cook_time=cook_time,
                preparation_time=prep_time,
                created_date=date_pub,
                description=description,
                images=images,
                category=category,
                ingredient_quantities=ingredient_quantities,
                ingredients=ingredients,
                nutrition=nutrition,
                servings=str(serving_size),
                recipe_yield=recipe_yield,
                instructions=instructions
            )

            author.add_recipe(recipe)
            category.add_recipe(recipe)
            return recipe

        except Exception as e:
            print(f"Error processing recipe {row.get('RecipeId', 'unknown')}: {e}")
            return None

    def _get_create_author(self, author_id, author_name):
        if author_id not in self.__authors:
            self.__authors[author_id] = Author(author_id, author_name)
        return self.__authors[author_id]

    def _get_create_category(self, category_name):
        if category_name not in self.__categories:
            self.__categories[category_name] = Category(category_name, [], self.__category_id_counter)
            self.__category_id_counter += 1
        return self.__categories[category_name]

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return datetime.now()

    @property
    def recipes(self):
        return self.__recipes

    @property
    def authors(self):
        return list(self.__authors.values())

    @property
    def categories(self):
        return list(self.__categories.values())