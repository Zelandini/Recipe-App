from flask import Blueprint, render_template, current_app
from recipe.services.recipe_services import get_featured_recipes, get_recipe_of_the_day

bp = Blueprint("home", __name__)

@bp.route("/")
def index():
    repo = current_app.repository

    featured_recipes = get_featured_recipes(repo, count=6)
    recipe_of_day = get_recipe_of_the_day(repo)

    featured = []
    for recipe in featured_recipes:
        featured.append({
            'id': recipe.id,
            'name': recipe.name,
            'author': recipe.author.name if recipe.author else 'Unknown',
            'time': f"{(recipe.cook_time or 0) + (recipe.preparation_time or 0)} min",
            'category': recipe.category.name if recipe.category else 'Uncategorized',
            'desc': recipe.description,
            'images': recipe.images,
            'nutrition': {
                'calories': recipe.nutrition.calories if recipe.nutrition else 0,
                'protein': recipe.nutrition.protein if recipe.nutrition else 0,
                'fat': recipe.nutrition.fat if recipe.nutrition else 0,
                'carbs': recipe.nutrition.carbohydrates if recipe.nutrition else 0,
            }
        })

    rod = None
    if recipe_of_day:
        rod = {
            'id': recipe_of_day.id,
            'name': recipe_of_day.name,
            'author': recipe_of_day.author.name if recipe_of_day.author else 'Unknown',
            'time': f"{(recipe_of_day.cook_time or 0) + (recipe_of_day.preparation_time or 0)} min",
            'category': recipe_of_day.category.name if recipe_of_day.category else 'Uncategorized',
            'desc': recipe_of_day.description,
            'images': recipe_of_day.images,
            'nutrition': {
                'calories': recipe_of_day.nutrition.calories if recipe_of_day.nutrition else 0,
                'protein': recipe_of_day.nutrition.protein if recipe_of_day.nutrition else 0,
                'fat': recipe_of_day.nutrition.fat if recipe_of_day.nutrition else 0,
                'carbs': recipe_of_day.nutrition.carbohydrates if recipe_of_day.nutrition else 0,
            }
        }

    return render_template("home.html", rod=rod, featured=featured)
