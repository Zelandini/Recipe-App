from flask import Blueprint, render_template, request, current_app

bp = Blueprint("browse", __name__)
PAGE_SIZE = 20

@bp.route("/", methods=["GET"])
def browse():
    repo = getattr(current_app, "repository", None)

    # Get search parameters from the query string
    query = request.args.get("query", "").strip()
    category = request.args.get("category", "").strip()
    author = request.args.get("author", "").strip()
    ingredient = request.args.get("ingredient", "").strip()

    # Pagination and sorting logic
    page = max(1, int(request.args.get("page", 1)))
    sort = (request.args.get("sort", "") or "").lower()

    # Perform the search in the repository
    all_recipes = list(repo.search_recipes(query, category, author, ingredient)) if repo and hasattr(repo, "search_recipes") else []

    enriched = []
    for r in all_recipes:
        cook = getattr(r, "cook_time", 0) or 0
        prep = getattr(r, "preparation_time", 0) or 0
        total_time = cook + prep

        author_obj = getattr(r, "author", None)
        author_name = getattr(author_obj, "name", None) if author_obj else None
        if not author_name:
            author_name = str(author_obj) if author_obj else "Unknown"

        calories = None
        nutri = getattr(r, "nutrition", None)
        if nutri and getattr(nutri, "calories", None) is not None:
            calories = nutri.calories

        desc = (getattr(r, "desc", None) or getattr(r, "description", "") or "").strip()

        # Calculate Health Star Rating
        health_star = repo.calculate_health_star_rating(r)

        enriched.append((r, total_time, author_name, calories, prep, desc, health_star))

    # Sorting based on the 'sort' parameter (same as your existing logic)
    if sort == "time_desc":
        enriched.sort(key=lambda x: x[1], reverse=True)
    elif sort == "time_asc":
        enriched.sort(key=lambda x: x[1])
    elif sort == "cal_desc":
        enriched.sort(key=lambda x: (x[3] is None, x[3] if x[3] is not None else 0), reverse=True)
    elif sort == "cal_asc":
        enriched.sort(key=lambda x: (x[3] is None, x[3] if x[3] is not None else 0))
    elif sort == "author_az":
        enriched.sort(key=lambda x: x[2].lower() if x[2] else "")
    elif sort == "author_za":
        enriched.sort(key=lambda x: x[2].lower() if x[2] else "", reverse=True)
    elif sort == "prep":
        enriched.sort(key=lambda x: (x[4] is None, x[4] if x[4] is not None else 10**9))

    total = len(enriched)
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(page, total_pages)
    start_i = (page - 1) * PAGE_SIZE
    end_i = start_i + PAGE_SIZE
    page_recipes = enriched[start_i:end_i]

    recipes = []
    for r, total_time, author_name, calories, prep_time, desc, health_star in page_recipes:
        recipes.append({
            "id": r.id,
            "name": r.name,
            "author": author_name,
            "total_time": total_time,
            "prep_time": prep_time,
            "calories": calories,
            "images": getattr(r, "images", []) or [],
            "desc": desc,
            "health_star": health_star,  # Add health star rating here
        })

    return render_template(
        "browse.html",
        recipes=recipes,
        page=page,
        total_pages=total_pages,
        sort=sort,
        query=query,
        category=category,
        author=author,
        ingredient=ingredient
    )
