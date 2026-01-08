# recipe/services/reviews_services.py
from recipe.adapters.repository import AbstractRepository
from typing import List
from recipe.domainmodel.review import Review
from datetime import datetime


def add_review(user_id: int, recipe_id: int, rating: int, comment: str, repo: AbstractRepository) -> bool:
    # Validate rating
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        raise ValueError("Rating must be an integer between 1 and 5")

    # Verify user and recipe exist
    user = repo.get_user(user_id)
    recipe = repo.get_recipe(recipe_id)
    if not user or not recipe:
        raise ValueError("User or Recipe not found")

    # Detect whether this user has already reviewed this recipe
    existing = next((r for r in repo.reviews_for_recipe(recipe_id) if getattr(r.user, "id", None) == user_id), None)

    # Delegate to repository (your DB repo now upserts internally)
    repo.add_review(recipe_id=recipe_id, user_id=user_id, rating=rating, comment=comment)

    # True if we updated an existing review, False if we inserted new
    return existing is not None


def get_reviews_for_recipe(recipe_id: int, repo: AbstractRepository) -> List[Review]:
    """Get all reviews for a recipe, sorted by most recent"""
    reviews = repo.reviews_for_recipe(recipe_id)
    # Sort by timestamp, most recent first
    return sorted(reviews, key=lambda r: r.timestamp, reverse=True)


def get_average_rating(recipe_id: int, repo: AbstractRepository) -> float:
    """Get average rating for a recipe"""
    return repo.average_rating(recipe_id)


def get_review_stats(recipe_id: int, repo: AbstractRepository) -> dict:
    """Get review statistics for a recipe."""
    reviews = repo.reviews_for_recipe(recipe_id)

    if not reviews:
        return {
            "total_reviews": 0,
            "average_rating": 0.0,
            "rating_distribution": {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
        }

    # Use repo's average (DB-backed) to match what's stored on recipe
    avg = float(repo.average_rating(recipe_id) or 0.0)

    # Distribution
    rating_counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for r in reviews:
        try:
            rating_counts[int(r.rating)] += 1
        except Exception:
            # ignore malformed ratings
            pass

    return {
        "total_reviews": len(reviews),
        "average_rating": avg,
        "rating_distribution": rating_counts,
    }


def user_has_reviewed(user_id: int, recipe_id: int, repo: AbstractRepository) -> bool:
    """Check if a user has already reviewed a recipe"""
    reviews = repo.reviews_for_recipe(recipe_id)
    return any(review.user.id == user_id for review in reviews)


def format_reviews_for_display(reviews: List[Review]) -> List[dict]:
    """Format reviews for template display, robust to missing fields."""
    formatted = []
    for r in reviews or []:
        ts = getattr(r, "timestamp", None)
        try:
            formatted_date = ts.strftime("%B %d, %Y") if ts else ""
        except Exception:
            formatted_date = ""
        formatted.append({
            "id": getattr(r, "id", None),
            "user": getattr(getattr(r, "user", None), "username", "Unknown"),
            "rating": getattr(r, "rating", 0),
            "comment": getattr(r, "text", ""),
            "timestamp": ts,
            "formatted_date": formatted_date,
        })
    return formatted