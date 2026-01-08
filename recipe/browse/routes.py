from flask import Blueprint, render_template, request, current_app, abort

bp = Blueprint("browse", __name__)
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Allowed DB sort keys — keep these aligned with your DatabaseRepository
ALLOWED_SORT = {"name", "title", "id", "rating", "author", "category"}
ALLOWED_DIR = {"asc", "desc"}

def _int_arg(name: str, default: int, minimum: int = 1, maximum: int | None = None) -> int:
    try:
        val = int(request.args.get(name, default))
    except (TypeError, ValueError):
        val = default
    if val < minimum:
        val = minimum
    if maximum is not None and val > maximum:
        val = maximum
    return val

def _str_arg(name: str, default: str = "") -> str:
    return (request.args.get(name, default) or "").strip()

@bp.route("/", methods=["GET"])
def browse():
    repo = getattr(current_app, "repository", None)
    if repo is None:
        abort(500, description="Repository not configured")

    # Filters (if any present, we will use paged search)
    query      = _str_arg("query")
    category   = _str_arg("category")
    author     = _str_arg("author")
    ingredient = _str_arg("ingredient")

    # Pagination + sorting
    page     = _int_arg("page", 1, minimum=1)
    per_page = _int_arg("size", DEFAULT_PAGE_SIZE, minimum=1, maximum=MAX_PAGE_SIZE)
    sort_by  = (_str_arg("sort") or "name").lower()
    sort_dir = (_str_arg("dir") or "asc").lower()

    # Clamp to allowed sort keys/dirs to avoid SQL injection-ish mistakes
    if sort_by not in ALLOWED_SORT:
        sort_by = "name"  # safe default
    if sort_dir not in ALLOWED_DIR:
        sort_dir = "asc"

    # If any filter is provided, use DB search (paged); else do plain browse (paged)
    has_filters = any([query, category, author, ingredient])

    if has_filters:
        items, total = repo.search_recipes_paged(
            query=query or None,
            category=category or None,
            author=author or None,
            ingredient=ingredient or None,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
    else:
        items = repo.get_recipes_by_page(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        total = repo.get_total_recipe_count()

    # Total pages
    total_pages = max(1, (total + per_page - 1) // per_page)
    # Adjust page if out of range (e.g. user changes filters)
    if page > total_pages:
        page = total_pages

    # Enrich items for template (no extra DB calls; your DB repo already bulk-loads relations)
    recipes = []
    for r in items:
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

        # Health Star Rating from repo (returns Optional[float])
        health_star = repo.calculate_health_star_rating(r)

        recipes.append({
            "id": r.id,
            "name": r.name,
            "author": author_name,
            "total_time": total_time,
            "prep_time": prep,
            "calories": calories,
            "images": getattr(r, "images", []) or [],
            "desc": desc,
            "health_star": health_star,
            "rating": getattr(r, "rating", None),
        })

    return render_template(
        "browse.html",
        recipes=recipes,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        sort=sort_by,
        dir=sort_dir,
        query=query,
        category=category,
        author=author,
        ingredient=ingredient,
        has_filters=has_filters,
    )
@bp.route("/suggest", methods=["GET"])
def suggest():
    repo = getattr(current_app, "repository", None)
    if repo is None:
        abort(500, description="Repository not configured")

    field = _str_arg("field").lower()  # e.g., "title", "author", "category", "ingredient"
    q = _str_arg("q")
    values = repo.distinct_values(field, q, limit=5)
    return jsonify(values)
