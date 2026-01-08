# recipe/adapters/orm.py
from sqlalchemy import Table, Column, Integer, Float, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import registry, relationship

from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.recipe_image import RecipeImage
from recipe.domainmodel.recipe_ingredient import RecipeIngredient
from recipe.domainmodel.recipe_instruction import RecipeInstruction

# Create mapper registry
mapper_registry = registry()
metadata = mapper_registry.metadata

# Tables
authors_table = Table(
    'authors', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False)
)

categories_table = Table(
    'categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False)
)

nutrition_table = Table(
    'nutrition', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('calories', Float, nullable=False),
    Column('fat', Float, nullable=False),
    Column('saturated_fat', Float, nullable=False),
    Column('cholesterol', Float, nullable=False),
    Column('sodium', Float, nullable=False),
    Column('carbohydrates', Float, nullable=False),
    Column('fiber', Float, nullable=False),
    Column('sugar', Float, nullable=False),
    Column('protein', Float, nullable=False)
)

recipes_table = Table(
    'recipes', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(255), nullable=False),
    Column('author_id', Integer, ForeignKey('authors.id'), nullable=False),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('nutrition_id', Integer, ForeignKey('nutrition.id')),
    Column('description', Text),
    Column('cook_time', Integer, default=0),
    Column('preparation_time', Integer, default=0),
    Column('created_date', DateTime),
    Column('servings', String(50)),
    Column('recipe_yield', String(50)),
    Column('rating', Float)
)

recipe_images_table = Table(
    'recipe_images', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), nullable=False),
    Column('url', Text, nullable=False),
    Column('position', Integer, nullable=False)
)

recipe_ingredients_table = Table(
    'recipe_ingredients', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), nullable=False),
    Column('quantity', String(255), nullable=False),
    Column('ingredient', String(255), nullable=False),
    Column('position', Integer, nullable=False)
)

recipe_instructions_table = Table(
    'recipe_instructions', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), nullable=False),
    Column('step', Text, nullable=False),
    Column('position', Integer, nullable=False)
)

users_table = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), nullable=False, unique=True),
    Column('password', String(255), nullable=False)
)

reviews_table = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('text', Text, nullable=False),
    Column('timestamp', DateTime, nullable=False),
    UniqueConstraint('user_id', 'recipe_id', name='uq_review_user_recipe')
)

favourites_table = Table(
    'favourites', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('recipe_id', Integer, ForeignKey('recipes.id'), nullable=False),
    UniqueConstraint('user_id', 'recipe_id', name='uq_fav_user_recipe')
)


def map_model_to_tables():
    """Map YOUR domain models to database tables."""

    mapper_registry.map_imperatively(Author, authors_table, properties={
        '_Author__id': authors_table.c.id,
        '_Author__name': authors_table.c.name,
        '_Author__recipes': relationship(Recipe, back_populates='_Recipe__author')
    })

    mapper_registry.map_imperatively(Category, categories_table, properties={
        '_Category__id': categories_table.c.id,
        '_Category__name': categories_table.c.name,
        '_Category__recipes': relationship(Recipe, back_populates='_Recipe__category')
    })

    mapper_registry.map_imperatively(Nutrition, nutrition_table, properties={
        '_Nutrition__id': nutrition_table.c.id,
        '_Nutrition__calories': nutrition_table.c.calories,
        '_Nutrition__fat': nutrition_table.c.fat,
        '_Nutrition__saturated_fat': nutrition_table.c.saturated_fat,
        '_Nutrition__cholesterol': nutrition_table.c.cholesterol,
        '_Nutrition__sodium': nutrition_table.c.sodium,
        '_Nutrition__carbohydrates': nutrition_table.c.carbohydrates,
        '_Nutrition__fiber': nutrition_table.c.fiber,
        '_Nutrition__sugar': nutrition_table.c.sugar,
        '_Nutrition__protein': nutrition_table.c.protein
    })

    mapper_registry.map_imperatively(Recipe, recipes_table, properties={
        '_Recipe__id': recipes_table.c.id,
        '_Recipe__name': recipes_table.c.name,
        '_Recipe__description': recipes_table.c.description,
        '_Recipe__cook_time': recipes_table.c.cook_time,
        '_Recipe__preparation_time': recipes_table.c.preparation_time,
        '_Recipe__date': recipes_table.c.created_date,
        '_Recipe__servings': recipes_table.c.servings,
        '_Recipe__recipe_yield': recipes_table.c.recipe_yield,
        '_Recipe__rating': recipes_table.c.rating,
        '_Recipe__author': relationship(Author, back_populates='_Author__recipes'),
        '_Recipe__category': relationship(Category, back_populates='_Category__recipes'),
        '_Recipe__nutrition': relationship(Nutrition),
        '_Recipe__reviews': relationship(Review, back_populates='_Review__recipe')
    })

    mapper_registry.map_imperatively(RecipeImage, recipe_images_table, properties={
        '_RecipeImage__recipe_id': recipe_images_table.c.recipe_id,
        '_RecipeImage__url': recipe_images_table.c.url,
        '_RecipeImage__position': recipe_images_table.c.position
    })

    mapper_registry.map_imperatively(RecipeIngredient, recipe_ingredients_table, properties={
        '_RecipeIngredient__recipe_id': recipe_ingredients_table.c.recipe_id,
        '_RecipeIngredient__quantity': recipe_ingredients_table.c.quantity,
        '_RecipeIngredient__ingredient': recipe_ingredients_table.c.ingredient,
        '_RecipeIngredient__position': recipe_ingredients_table.c.position
    })

    mapper_registry.map_imperatively(RecipeInstruction, recipe_instructions_table, properties={
        '_RecipeInstruction__recipe_id': recipe_instructions_table.c.recipe_id,
        '_RecipeInstruction__step': recipe_instructions_table.c.step,
        '_RecipeInstruction__position': recipe_instructions_table.c.position
    })

    mapper_registry.map_imperatively(User, users_table, properties={
        '_User__id': users_table.c.id,
        '_User__username': users_table.c.username,
        '_User__password': users_table.c.password,
        '_User__reviews': relationship(Review, back_populates='_Review__user'),
        '_User__favourite_recipes': relationship(Favourite, back_populates='_Favourite__user')
    })

    mapper_registry.map_imperatively(Review, reviews_table, properties={
        '_Review__id': reviews_table.c.id,
        '_Review__rating': reviews_table.c.rating,
        '_Review__text': reviews_table.c.text,
        '_Review__timestamp': reviews_table.c.timestamp,
        '_Review__user': relationship(User, back_populates='_User__reviews'),
        '_Review__recipe': relationship(Recipe, back_populates='_Recipe__reviews')
    })

    mapper_registry.map_imperatively(Favourite, favourites_table, properties={
        '_Favourite__id': favourites_table.c.id,
        '_Favourite__user': relationship(User, back_populates='_User__favourite_recipes'),
        '_Favourite__recipe': relationship(Recipe)
    })