import os
from pathlib import Path
from flask import Flask
from flask_wtf.csrf import CSRFProtect

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

csrf = CSRFProtect()


def create_app():
    """Construct the core application."""
    app = Flask(__name__)

    # ---- Config (env overrides supported) ----
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key-change-me")
    repo_mode = os.getenv("REPOSITORY", "database").lower()
    database_uri = os.getenv("DATABASE_URL", "sqlite:///recipes.db")
    database_path = Path(database_uri.replace("sqlite:///", "")).name

    csrf.init_app(app)

    print("=" * 60)
    print(f"🗄️  REPOSITORY MODE: {repo_mode.upper()}")
    print("=" * 60)

    if repo_mode == "database":
        # ===== DATABASE MODE =====
        from recipe.adapters.database_repository import DatabaseRepository
        from recipe.adapters import database_populate, orm

        # Create engine (SQLite-safe settings)
        database_engine = create_engine(
            database_uri,
            connect_args={"check_same_thread": False} if database_uri.startswith("sqlite:///") else {},
            poolclass=NullPool if database_uri.startswith("sqlite:///") else None,
            echo=False,
            future=True,
        )

        # ----- Map models BEFORE creating tables -----
        orm.map_model_to_tables()
        orm.metadata.create_all(database_engine)

        # Create session factory
        SessionFactory = sessionmaker(bind=database_engine, autoflush=True, autocommit=False, future=True)

        # Create repository instance
        app.repository = DatabaseRepository(SessionFactory)

        insp = inspect(database_engine)
        table_names = set(insp.get_table_names())
        if not table_names:
            print("⚠ No tables found; freshly created.")
        else:
            print(f"✓ Found tables: {', '.join(sorted(table_names))}")

        # Populate only if DB is empty (authors count == 0)
        try:
            with database_engine.begin() as conn:
                authors_count = conn.execute(text("SELECT COUNT(*) FROM authors")).scalar_one()
        except Exception:
            authors_count = 0  # If authors doesn't exist for some reason

        if authors_count == 0:
            print("📝 CREATING AND POPULATING DATABASE...")
            data_path = os.path.join(os.path.dirname(__file__), "adapters", "data")
            database_populate.populate(database_engine, data_path)
            print(f"✓ Database populated. Recipes loaded: {app.repository.get_total_recipe_count()}")
        else:
            print(f"✓ Database ready: {app.repository.get_total_recipe_count()} recipes loaded")

        # ===== Session management per HTTP request =====
        @app.before_request
        def _before_request_reset_session():
            # Reset the SQLAlchemy scoped session each request
            if isinstance(app.repository, DatabaseRepository):
                app.repository.reset_session()

        @app.teardown_appcontext
        def _teardown_close_session(exception=None):
            if isinstance(app.repository, DatabaseRepository):
                app.repository.close_session()

        # Friendly file existence log for SQLite
        if database_uri.startswith("sqlite:///"):
            if os.path.exists(database_path):
                print(f"✓ Database file found: {database_path}")
            else:
                print(f"⚠ Database file not found yet (will be created on first write): {database_path}")

    elif repo_mode == "memory":
        # ===== MEMORY MODE =====
        print("⚠ Using IN-MEMORY repository (data will be lost on restart)")
        from recipe.adapters.memory_repository import MemoryRepository, populate

        repository = MemoryRepository()
        populate(repository)
        app.repository = repository

        print(f"✓ Memory repository ready: {repository.get_total_recipe_count()} recipes loaded")

    else:
        raise ValueError(f"Invalid REPOSITORY mode: {repo_mode}. Use 'database' or 'memory'")

    print("=" * 60)

    # ===== Register blueprints =====
    from .home.routes import bp as home_bp
    from .browse.routes import bp as browse_bp
    from .recipes.routes import bp as recipes_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(browse_bp, url_prefix="/browse")
    app.register_blueprint(recipes_bp, url_prefix="/recipes")

    from recipe.authentication.routes import authentication_blueprint
    app.register_blueprint(authentication_blueprint, url_prefix="/authentication")

    from recipe.favourites.routes import favourites_bp
    app.register_blueprint(favourites_bp, url_prefix="/favourites")

    from recipe.reviews.routes import reviews_bp
    app.register_blueprint(reviews_bp, url_prefix="/reviews")

    from recipe.browse.api import api as browse_api
    app.register_blueprint(browse_api, url_prefix="/api/browse")

    # ===== Debug route =====
    @app.route("/debug/repository")
    def debug_repository():
        """Debug endpoint to check repository status."""
        repo = app.repository
        repo_type = type(repo).__name__
        recipe_count = repo.get_total_recipe_count()

        info = f"""
        <h1>Repository Debug Info</h1>
        <ul>
            <li><strong>Type:</strong> {repo_type}</li>
            <li><strong>Total Recipes:</strong> {recipe_count}</li>
            <li><strong>Database File:</strong> {'recipes.db exists' if os.path.exists('recipes.db') else 'No database file'}</li>
            <li><strong>DB URI:</strong> {database_uri}</li>
        </ul>
        <p><a href="/">← Back to Home</a></p>
        """
        return info

    return app

