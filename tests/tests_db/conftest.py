import shutil
from pathlib import Path
import tempfile

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from recipe.adapters import orm
from recipe.adapters.database_repository import DatabaseRepository
from recipe.adapters.database_populate import populate as db_populate

# Paths
THIS_DIR = Path(__file__).parent
CSV_EXCERPT = THIS_DIR / "data" / "recipes-excerpt.csv"
TEST_DB_PATH = THIS_DIR / "recipes-test.db"
TEST_DB_URI = f"sqlite:///{TEST_DB_PATH}"
MEM_DB_URI = "sqlite://"

def _wipe_all(engine):
    with engine.begin() as conn:
        for table in reversed(orm.mapper_registry.metadata.sorted_tables):
            conn.execute(table.delete())

def _populate_from_excerpt(engine):

    tmpdir = Path(tempfile.mkdtemp(prefix="recipes_pop_"))
    csv_target = tmpdir / "recipes.csv"
    shutil.copyfile(CSV_EXCERPT, csv_target)
    db_populate(engine, str(tmpdir))

@pytest.fixture(scope="session")
def engine():
    clear_mappers()
    orm.map_model_to_tables()
    engine = create_engine(TEST_DB_URI, connect_args={"check_same_thread": False})
    orm.mapper_registry.metadata.create_all(engine)
    yield engine


@pytest.fixture(scope="function")
def session_factory(engine):
    _wipe_all(engine)
    _populate_from_excerpt(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    return Session

@pytest.fixture(scope="function")
def repo(session_factory):
    return DatabaseRepository(session_factory)

@pytest.fixture(scope="function")
def empty_session():
    """
    Pure ORM unit tests: brand-new in-memory DB with empty tables.
    """
    clear_mappers()
    orm.map_model_to_tables()
    engine = create_engine(MEM_DB_URI)
    orm.mapper_registry.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    s = Session()
    try:
        yield s
    finally:
        s.close()
        orm.mapper_registry.metadata.drop_all(engine)
