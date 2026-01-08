from datetime import datetime
from sqlalchemy import text

from recipe.domainmodel.author import Author
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.category import Category
from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review

def test_orm_save_and_load_author(empty_session):
    a = Author(70001, "ORM Save Author")
    empty_session.add(a)
    empty_session.commit()
    loaded = empty_session.get(Author, 70001)
    assert loaded and loaded.name == "ORM Save Author"

def test_orm_save_and_load_category(empty_session):
    from sqlalchemy import text
    from recipe.domainmodel.category import Category

    empty_session.execute(
        text("INSERT INTO categories (id, name) VALUES (:id, :name)"),
        {"id": 80001, "name": "ORM Save Category"}
    )
    empty_session.commit()

    loaded = empty_session.get(Category, 80001)
    assert loaded is not None
    assert loaded.name == "ORM Save Category"

    new_cat = Category("ORM Inserted Category")
    empty_session.add(new_cat)
    empty_session.commit()

    assert new_cat.id is not None  # assigned by DB
    loaded2 = empty_session.get(Category, new_cat.id)
    assert loaded2 is not None
    assert loaded2.name == "ORM Inserted Category"




def test_author_recipe_relationship(empty_session):
    # 1) Seed rows via SQL
    empty_session.execute(
        text("INSERT INTO authors (id, name) VALUES (:id, :name)"),
        {"id": 101, "name": "Unit Author"}
    )
    empty_session.execute(
        text("""
        INSERT INTO nutrition (id, calories, fat, saturated_fat, cholesterol, sodium,
                               carbohydrates, fiber, sugar, protein)
        VALUES (:id,:calories,:fat,:saturated_fat,:cholesterol,:sodium,
                :carbohydrates,:fiber,:sugar,:protein)
        """),
        {
            "id": 202, "calories": 250, "fat": 10, "saturated_fat": 3, "cholesterol": 30,
            "sodium": 200, "carbohydrates": 30, "fiber": 5, "sugar": 12, "protein": 8
        }
    )
    empty_session.execute(
        text("INSERT INTO categories (id, name) VALUES (:id, :name)"),
        {"id": 909, "name": "Unit Category"}
    )
    empty_session.commit()

    # 2) Load managed instances
    a = empty_session.get(Author, 101)
    n = empty_session.get(Nutrition, 202)
    c = empty_session.get(Category, 909)

    # 3) Build recipe using managed instances
    r = Recipe(
        303, "Unit Recipe", a, 15, 5, datetime(2025, 1, 1),
        "desc", [], None, [], [], None, n, "4", "1 batch", ["step1"]
    )
    r.category = c

    empty_session.add(r)
    empty_session.commit()

    # 4) Assert relationships
    fetched = empty_session.get(Recipe, 303)
    assert fetched is not None
    assert fetched.author is not None and fetched.author.name == "Unit Author"
    assert fetched.nutrition is not None and abs(fetched.nutrition.calories - 250) < 1e-6
    assert fetched.category is not None and fetched.category.name == "Unit Category"

def test_orm_user_review_relationship(empty_session):
    # seed minimal related rows via SQL
    empty_session.execute(text("INSERT INTO authors (id,name) VALUES (90001,'A')"))
    empty_session.execute(text("INSERT INTO categories (id,name) VALUES (90002,'C')"))
    empty_session.execute(text("""
        INSERT INTO nutrition (id, calories, fat, saturated_fat, cholesterol, sodium,
                               carbohydrates, fiber, sugar, protein)
        VALUES (90003,100,1,0.5,0,10,20,1,5,2)
    """))
    empty_session.commit()

    A = empty_session.get(Author, 90001)
    C = empty_session.get(Category, 90002)
    N = empty_session.get(Nutrition, 90003)

    r = Recipe(90004, "ReviewTarget", A, 0, 0, datetime(2025,1,1),
               "desc", [], None, [], [], None, N, None, None, [])
    r.category = C
    empty_session.add(r)

    u = User("orm_user", "hash", 91001)  # User(username, password, id)
    empty_session.add(u)
    empty_session.flush()

    rev = Review(92001, u, r, datetime(2025,1,2), 5, "great")
    empty_session.add(rev)
    empty_session.commit()

    got = empty_session.get(Review, 92001)
    assert got and got.user.username == "orm_user" and got.recipe.id == 90004
