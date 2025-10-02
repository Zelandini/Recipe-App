# recipe/__init__.py
from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "change-me"  # set via env in prod
    csrf.init_app(app)

    # ===== Repository =====
    from recipe.adapters.memory_repository import MemoryRepository, populate
    repository = MemoryRepository()
    populate(repository)
    app.repository = repository

    # ===== Existing blueprints (unchanged) =====
    from .home.routes import bp as home_bp
    from .browse.routes import bp as browse_bp
    from .recipes.routes import bp as recipes_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(browse_bp, url_prefix="/browse")
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

    # Auth blueprint (unchanged)
    from recipe.authentication.routes import authentication_blueprint
    app.register_blueprint(authentication_blueprint, url_prefix="/authentication")

    # Favourites blueprint (unchanged import name)
    from recipe.favourites.routes import favourites_bp
    app.register_blueprint(favourites_bp, url_prefix="/favourites")

    # Reviews blueprint (unchanged)
    from recipe.reviews.routes import reviews_bp
    app.register_blueprint(reviews_bp, url_prefix="/reviews")

    # ===== NEW: API for dropdown/combobox suggestions =====
    # GET /api/browse/options?field=author&q=jo&limit=10
    # (safe with CSRF because it's GET-only)
    from recipe.browse.api import api as browse_api
    app.register_blueprint(browse_api, url_prefix="/api/browse")

    return app
