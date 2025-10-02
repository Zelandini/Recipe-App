# recipe/browse/api.py
from flask import Blueprint, request, jsonify, current_app

api = Blueprint("browse_api", __name__)

@api.get("/options")
def options():
    """
    GET /api/browse/options?field=author&q=an&limit=10
    Returns a small list of distinct values for the requested field.
    """
    field = (request.args.get("field") or "").strip().lower()
    q = (request.args.get("q") or "").strip()
    limit = int(request.args.get("limit") or 10)

    repo = getattr(current_app, "repository", None)
    if repo is None:
        return jsonify([])

    # call repo helper (added in step 3)
    values = repo.distinct_values(field=field, query=q, limit=limit)
    return jsonify(values)
