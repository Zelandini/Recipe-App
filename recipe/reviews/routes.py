# recipe/reviews/routes.py
from flask import Blueprint, request, redirect, url_for, session, flash, current_app, jsonify
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
from recipe.authentication.routes import login_required
import recipe.services.reviews_services as reviews_services

reviews_bp = Blueprint("reviews", __name__)


class ReviewForm(FlaskForm):
    rating = SelectField(
        "Rating",
        choices=[
            ('5', '5 Stars - Excellent'),
            ('4', '4 Stars - Very Good'),
            ('3', '3 Stars - Good'),
            ('2', '2 Stars - Fair'),
            ('1', '1 Star - Poor')
        ],
        validators=[DataRequired(message="Please select a rating")]
    )
    comment = TextAreaField(
        "Comment",
        validators=[
            DataRequired(message="Please write a comment"),
            Length(min=10, max=500, message="Comment must be between 10 and 500 characters")
        ],
        render_kw={"placeholder": "Share your thoughts about this recipe..."}
    )
    submit = SubmitField("Post Review")


@reviews_bp.route('/add/<int:recipe_id>', methods=['POST'])
@login_required
def add_review(recipe_id):
    """Add a review for a recipe"""
    try:
        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            username = session.get('username')
            if username:
                user = current_app.repository.get_user_by_username(username)
                user_id = user.id if user else None

        if not user_id:
            flash("Please log in to post a review.", "error")
            return redirect(url_for('authentication_bp.login'))

        # Get form data
        rating = request.form.get('rating')
        comment = request.form.get('comment', '').strip()

        # Validate form data
        if not rating or not comment:
            flash("Please provide both a rating and comment.", "error")
            return redirect(request.referrer or url_for('recipes.detail', recipe_id=recipe_id))

        try:
            rating = int(rating)
        except (ValueError, TypeError):
            flash("Invalid rating value.", "error")
            return redirect(request.referrer or url_for('recipes.detail', recipe_id=recipe_id))

        if len(comment) < 10 or len(comment) > 500:
            flash("Comment must be between 10 and 500 characters.", "error")
            return redirect(request.referrer or url_for('recipes.detail', recipe_id=recipe_id))

        # Add the review
        updated = reviews_services.add_review(user_id, recipe_id, rating, comment, current_app.repository)

        if updated:
            flash("Your review has been updated!", "success")
        else:
            flash("Review posted successfully!", "success")

    except ValueError as e:
        flash(str(e), "error")
    except Exception as e:
        flash("Could not post review. Please try again.", "error")

    # Redirect back to the recipe page
    return redirect(request.referrer or url_for('recipes.detail', recipe_id=recipe_id))


# Helper functions for templates
@reviews_bp.app_context_processor
def inject_review_helpers():
    def get_review_stats(recipe_id):
        """Get review statistics for a recipe"""
        try:
            return reviews_services.get_review_stats(recipe_id, current_app.repository)
        except:
            return {
                'total_reviews': 0,
                'average_rating': 0.0,
                'rating_distribution': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
            }

    def user_has_reviewed_recipe(recipe_id):
        """Check if current user has reviewed a recipe"""
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
                return reviews_services.user_has_reviewed(user_id, recipe_id, current_app.repository)
        except:
            pass
        return False

    def get_reviews_for_display(recipe_id):
        """Get formatted reviews for display"""
        try:
            reviews = reviews_services.get_reviews_for_recipe(recipe_id, current_app.repository)
            return reviews_services.format_reviews_for_display(reviews)
        except:
            return []

    def render_stars(rating):
        """Render star rating as HTML"""
        stars = ""
        for i in range(1, 6):
            if i <= rating:
                stars += "★"  # Filled star
            else:
                stars += "☆"  # Empty star
        return stars

    return {
        'get_review_stats': get_review_stats,
        'user_has_reviewed_recipe': user_has_reviewed_recipe,
        'get_reviews_for_display': get_reviews_for_display,
        'render_stars': render_stars
    }


@reviews_bp.route('/debug/<int:recipe_id>')
def debug_reviews(recipe_id):
    try:
        repo = current_app.repository
        reviews = repo.reviews_for_recipe(recipe_id)

        debug_info = []
        debug_info.append(f"Recipe ID: {recipe_id}")
        debug_info.append(f"Raw reviews from repo: {reviews}")
        debug_info.append(f"Total reviews: {len(reviews)}")

        for i, review in enumerate(reviews):
            debug_info.append(f"Review {i}:")
            debug_info.append(f"  Review object: {review}")
            debug_info.append(f"  User: {getattr(review, 'user', 'NO USER ATTR')}")
            debug_info.append(f"  Rating: {getattr(review, 'rating', 'NO RATING ATTR')}")
            debug_info.append(f"  Text: '{getattr(review, 'text', 'NO TEXT ATTR')}'")
            debug_info.append(f"  Timestamp: {getattr(review, 'timestamp', 'NO TIMESTAMP ATTR')}")
            debug_info.append("---")

        return "<pre>" + "\n".join(debug_info) + "</pre>"

    except Exception as e:
        import traceback
        return f"<pre>Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}</pre>"
