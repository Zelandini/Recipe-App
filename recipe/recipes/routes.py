from flask import Blueprint, render_template, abort, current_app

from recipe.domainmodel import recipe
from recipe.services.recipe_services import get_recipe_by_id

bp = Blueprint("recipes", __name__)

@bp.route("/<int:recipe_id>")
def detail(recipe_id: int):
   """Recipe detail page."""
   repo = current_app.repository
   recipe = get_recipe_by_id(repo, recipe_id)

   if not recipe:
       abort(404)

   # Normalize fields
   cook = getattr(recipe, "cook_time", 0) or 0
   prep  = getattr(recipe, "preparation_time", 0) or 0
   imgs = getattr(recipe, "images", None)
   if isinstance(imgs, str):
       images = [imgs] if imgs.strip() else []
   elif isinstance(imgs, (list, tuple)):
       images = [s for s in imgs if isinstance(s, str) and s.strip()]
   else:
       images = []

   instructions = recipe.instructions if isinstance(recipe.instructions, list) else []
   ingredient_quantities = recipe.ingredient_quantities if isinstance(recipe.ingredient_quantities, list) else []
   nutri = recipe.nutrition

   # Calculate Health Star Rating
   health_star = repo.calculate_health_star_rating(recipe)

   # Convert to dict format for template
   recipe_data = {
       "id": recipe.id,
       "name": recipe.name,
       "author": recipe.author.name if recipe.author else "Unknown",
       "time": f"{cook + prep} min",
       "prep_time": prep,
       "cook_time": cook,
       "category": recipe.category.name if recipe.category else "Uncategorized",
       "desc": recipe.description,
       "ingredients": recipe.ingredients,
       "ingredient_quantities": ingredient_quantities,  # Added ingredient quantities
       "instructions": instructions,
       "images": images,
       "nutrition": {
           "calories": getattr(nutri, "calories", 0) if nutri else 0,
           "protein": getattr(nutri, "protein", 0)  if nutri else 0,
           "fat": getattr(nutri, "fat", 0)          if nutri else 0,
           "carbs": getattr(nutri, "carbohydrates", 0) if nutri else 0,
       },
       "health_star": health_star  # Added health star rating
   }

   return render_template("recipe_detail.html", recipe=recipe_data)
