from sqlalchemy import inspect, select
from recipe.adapters.orm import mapper_registry

def test_tables_exist(engine):
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    for name in {
        "recipes","authors","categories","nutrition",
        "recipe_images","recipe_ingredients","recipe_instructions",
        "users","reviews","favourites"
    }:
        assert name in tables

def test_recipes_loaded(engine):
    with engine.connect() as conn:
        rows = list(conn.execute(select(mapper_registry.metadata.tables["recipes"])))
        assert len(rows) > 0
        first = rows[0]
        assert "id" in first._mapping and "name" in first._mapping

def test_authors_populated(engine):
    with engine.connect() as conn:
        rows = list(conn.execute(select(mapper_registry.metadata.tables["authors"])))
    assert len(rows) > 0

def test_categories_populated(engine):
    with engine.connect() as conn:
        rows = list(conn.execute(select(mapper_registry.metadata.tables["categories"])))
    assert len(rows) > 0

def test_nutrition_populated(engine):
    with engine.connect() as conn:
        rows = list(conn.execute(select(mapper_registry.metadata.tables["nutrition"])))
    assert len(rows) > 0
