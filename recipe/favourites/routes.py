# recipe/favourites/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from recipe.authentication.routes import login_required
import recipe.services.favourites_services as favourites_services

favourites_bp = Blueprint("favourites", __name__, template_folder="../templates")


@favourites_bp.route('/add/<int:recipe_id>', methods=['POST'])
@login_required
def add_favourite(recipe_id):
    """Add a recipe to user's favourites"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            # Try to get user by username if user_id not in session
            username = session.get('username')
            if username:
                user = current_app.repository.get_user_by_username(username)
                user_id = user.id if user else None

        if not user_id:
            flash("Please log in to add favourites.", "error")
            return redirect(url_for('authentication_bp.login'))

        favourites_services.add_favourite(user_id, recipe_id, current_app.repository)
        flash("Recipe added to favourites!", "success")

        # Return JSON for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': 'Added to favourites'})

    except ValueError as e:
        flash("Could not add to favourites.", "error")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': str(e)})

    # Redirect back to the recipe page
    return redirect(request.referrer or url_for('recipes.detail', recipe_id=recipe_id))


@favourites_bp.route('/remove/<int:recipe_id>', methods=['POST'])
@login_required
def remove_favourite(recipe_id):
    """Remove a recipe from user's favourites"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            username = session.get('username')
            if username:
                user = current_app.repository.get_user_by_username(username)
                user_id = user.id if user else None

        if not user_id:
            flash("Please log in to manage favourites.", "error")
            return redirect(url_for('authentication_bp.login'))

        favourites_services.remove_favourite(user_id, recipe_id, current_app.repository)
        flash("Recipe removed from favourites.", "success")

        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': True, 'message': 'Removed from favourites'})

    except Exception as e:
        flash("Could not remove from favourites.", "error")
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'success': False, 'message': str(e)})

    return redirect(request.referrer or url_for('favourites.list'))


@favourites_bp.route('/list')
@login_required
def list():
    """Display user's favourite recipes"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            username = session.get('username')
            if username:
                user = current_app.repository.get_user_by_username(username)
                if user:
                    user_id = user.id
                    session['user_id'] = user_id

        if not user_id:
            flash("Please log in to view favourites.", "error")
            return redirect(url_for('authentication_bp.login'))

        favourite_recipes = favourites_services.get_user_favourites(user_id, current_app.repository)

        # Format recipes for template - this is likely where the error occurs
        favourites = []
        for recipe in favourite_recipes:
            if recipe:
                favourites.append({
                    'id': recipe.id,
                    'name': getattr(recipe, 'name', 'Unknown Recipe'),
                    'author': getattr(recipe.author, 'name', 'Unknown') if hasattr(recipe,
                                                                                   'author') and recipe.author else 'Unknown',
                    'time': f"{(getattr(recipe, 'cook_time', 0) or 0) + (getattr(recipe, 'preparation_time', 0) or 0)} min",
                    'category': getattr(recipe.category, 'name', 'Uncategorized') if hasattr(recipe,
                                                                                             'category') and recipe.category else 'Uncategorized',
                    'desc': getattr(recipe, 'description', 'No description available'),
                    'images': getattr(recipe, 'images', []),
                    'nutrition': {
                        'calories': getattr(recipe.nutrition, 'calories', 0) if hasattr(recipe,
                                                                                        'nutrition') and recipe.nutrition else 0,
                        'protein': getattr(recipe.nutrition, 'protein', 0) if hasattr(recipe,
                                                                                      'nutrition') and recipe.nutrition else 0,
                        'fat': getattr(recipe.nutrition, 'fat', 0) if hasattr(recipe,
                                                                              'nutrition') and recipe.nutrition else 0,
                        'carbs': getattr(recipe.nutrition, 'carbohydrates', 0) if hasattr(recipe,
                                                                                          'nutrition') and recipe.nutrition else 0,
                    }
                })

        return render_template('favourites/list.html', favourites=favourites)

    except Exception as e:
        import traceback
        # Show the actual error instead of redirecting
        return f"<pre>Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


# Helper function to inject favourite status into templates
@favourites_bp.app_context_processor
def inject_favourites():
    def is_favourite(recipe_id):
        if 'username' not in session:
            return False

        try:
            user_id = session.get('user_id')
            if not user_id:
                username = session.get('username')
                if username:
                    user = current_app.repository.get_user_by_username(username)
                    user_id = user.id if user else None

            if user_id:
                return favourites_services.is_favourite(user_id, recipe_id, current_app.repository)
        except:
            pass
        return False

    def favourites_count():
        if 'username' not in session:
            return 0

        try:
            user_id = session.get('user_id')
            if not user_id:
                username = session.get('username')
                if username:
                    user = current_app.repository.get_user_by_username(username)
                    user_id = user.id if user else None

            if user_id:
                return favourites_services.get_favourites_count(user_id, current_app.repository)
        except:
            pass
        return 0

    return {'is_favourite': is_favourite, 'favourites_count': favourites_count}


@favourites_bp.route('/debug')
@login_required
def debug_favourites():
    try:
        user_id = session.get('user_id')
        username = session.get('username')
        repo = current_app.repository

        debug_info = []
        debug_info.append(f"Session user_id: {user_id}")
        debug_info.append(f"Session username: {username}")

        # Check the raw favourites storage
        debug_info.append(f"Raw __user_favourites dict: {repo._MemoryRepository__user_favourites}")

        if user_id:
            # Check what's actually stored for this user
            user_favs = repo._MemoryRepository__user_favourites.get(user_id, set())
            debug_info.append(f"User {user_id} favourite IDs: {user_favs}")

            # Test each recipe ID individually
            for recipe_id in user_favs:
                recipe = repo.get_recipe(recipe_id)
                debug_info.append(f"Recipe ID {recipe_id} -> {recipe}")
                if recipe:
                    debug_info.append(f"  Recipe name: {recipe.name}")
                else:
                    debug_info.append(f"  Recipe is None!")

            # Test the repository method directly
            repo_result = repo.favourites_for_user(user_id)
            debug_info.append(f"Repository favourites_for_user: {repo_result}")
            debug_info.append(f"Repository result length: {len(repo_result)}")

            # Test the service
            service_result = favourites_services.get_user_favourites(user_id, repo)
            debug_info.append(f"Service result: {service_result}")
            debug_info.append(f"Service result length: {len(service_result)}")

        return "<pre>" + "\n".join(debug_info) + "</pre>"

    except Exception as e:
        import traceback
        return f"<pre>Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"


@favourites_bp.route('/simple-test')
@login_required
def simple_test():
    try:
        repo = current_app.repository
        user_id = 2

        # Test 1: Direct recipe lookup
        recipe = repo.get_recipe_by_id(5150)
        test1 = f"get_recipe_by_id(5150): {recipe} | Name: {recipe.name if recipe else 'None'}"

        # Test 2: Check stored favourites
        stored_favs = repo._MemoryRepository__user_favourites.get(user_id, set())
        test2 = f"Stored favourite IDs: {stored_favs}"

        # Test 3: Manual recipe lookup for each ID
        manual_recipes = []
        for recipe_id in stored_favs:
            r = repo.get_recipe_by_id(recipe_id)
            manual_recipes.append(r)
        test3 = f"Manual lookup results: {manual_recipes}"

        # Test 4: The actual method call
        result = repo.favourites_for_user(user_id)
        test4 = f"favourites_for_user result: {result}"

        return f"<pre>{test1}\n{test2}\n{test3}\n{test4}</pre>"

    except Exception as e:
        import traceback
        return f"<pre>Error: {traceback.format_exc()}</pre>"


@favourites_bp.route('/loop-test')
@login_required
def loop_test():
    try:
        repo = current_app.repository
        stored_favs = {5150}  # Simulate your stored favourites

        debug = []
        debug.append(f"Starting with IDs: {stored_favs}")

        for recipe_id in stored_favs:
            debug.append(f"Processing recipe_id: {recipe_id} (type: {type(recipe_id)})")
            recipe = repo.get_recipe_by_id(recipe_id)
            debug.append(f"Got recipe: {recipe}")
            debug.append(f"Recipe is None: {recipe is None}")
            debug.append(f"Recipe bool: {bool(recipe) if recipe else 'N/A'}")
            debug.append("---")

        return "<pre>" + "\n".join(debug) + "</pre>"

    except Exception as e:
        import traceback
        return f"<pre>Error: {traceback.format_exc()}</pre>"