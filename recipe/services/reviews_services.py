# recipe/services/reviews_services.py
from recipe.adapters.repository import AbstractRepository
from typing import List
from recipe.domainmodel.review import Review
from datetime import datetime


def add_review(user_id: int, recipe_id: int, rating: int, comment: str, repo: AbstractRepository):
    """Add a review for a recipe"""
    # Validate rating
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValueError("Rating must be an integer between 1 and 5")

    # Verify user and recipe exist
    user = repo.get_user(user_id)
    recipe = repo.get_recipe(recipe_id)

    if not user or not recipe:
        raise ValueError("User or Recipe not found")

    # Check if user already reviewed this recipe
    existing_reviews = repo.reviews_for_recipe(recipe_id)
    for review in existing_reviews:
        if review.user.id == user_id:
            raise ValueError("You have already reviewed this recipe")

    # Add the review
    repo.add_review(recipe_id, user_id, rating, comment)


def get_reviews_for_recipe(recipe_id: int, repo: AbstractRepository) -> List[Review]:
    """Get all reviews for a recipe, sorted by most recent"""
    reviews = repo.reviews_for_recipe(recipe_id)
    # Sort by timestamp, most recent first
    return sorted(reviews, key=lambda r: r.timestamp, reverse=True)


def get_average_rating(recipe_id: int, repo: AbstractRepository) -> float:
    """Get average rating for a recipe"""
    return repo.average_rating(recipe_id)


def get_review_stats(recipe_id: int, repo: AbstractRepository) -> dict:
    """Get review statistics for a recipe"""
    reviews = repo.reviews_for_recipe(recipe_id)

    if not reviews:
        return {
            'total_reviews': 0,
            'average_rating': 0.0,
            'rating_distribution': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        }

    # Calculate rating distribution
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    total_rating = 0

    for review in reviews:
        rating_counts[review.rating] += 1
        total_rating += review.rating

    return {
        'total_reviews': len(reviews),
        'average_rating': total_rating / len(reviews),
        'rating_distribution': rating_counts
    }


def user_has_reviewed(user_id: int, recipe_id: int, repo: AbstractRepository) -> bool:
    """Check if a user has already reviewed a recipe"""
    reviews = repo.reviews_for_recipe(recipe_id)
    return any(review.user.id == user_id for review in reviews)


def format_reviews_for_display(reviews: List[Review]) -> List[dict]:
    """Format reviews for template display"""
    formatted_reviews = []

    for review in reviews:
        formatted_reviews.append({
            'id': review.id,
            'user': review.user.username,
            'rating': review.rating,
            'comment': review.text,
            'timestamp': review.timestamp,
            'formatted_date': review.timestamp.strftime("%B %d, %Y")
        })

    return formatted_reviews