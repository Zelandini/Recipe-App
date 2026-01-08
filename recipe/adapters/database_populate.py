# recipe/adapters/database_populate.py
import os
from sqlalchemy.orm import sessionmaker
from recipe.adapters.datareader.csvdatareader import CSVDataReader


def populate(engine, data_path: str):
    """Populate database from CSV file."""
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        csv_file = os.path.join(data_path, "recipes.csv")

        print("Reading CSV file...")
        reader = CSVDataReader(csv_file, database_mode=True)  # PASS database_mode=True
        reader.read_csv_file()

        print(f"Adding {len(reader.authors)} authors...")
        for author in reader.authors:
            session.add(author)
        session.commit()

        print(f"Adding {len(reader.categories)} categories...")
        for category in reader.categories:
            session.add(category)
        session.commit()

        print(f"Adding {len(reader.recipes)} recipes...")
        for recipe in reader.recipes:
            # CLEAR the lists on the recipe
            recipe._Recipe__images = []
            recipe._Recipe__ingredients = []
            recipe._Recipe__ingredient_quantities = []
            recipe._Recipe__instructions = []

            # Add nutrition if exists
            if recipe.nutrition:
                session.add(recipe.nutrition)

            # Add the recipe
            session.add(recipe)

        session.commit()

        # Add all helper objects
        print(f"Adding {len(reader.recipe_images)} recipe images...")
        for img in reader.recipe_images:
            session.add(img)
        session.commit()

        print(f"Adding {len(reader.recipe_ingredients)} recipe ingredients...")
        for ing in reader.recipe_ingredients:
            session.add(ing)
        session.commit()

        print(f"Adding {len(reader.recipe_instructions)} recipe instructions...")
        for inst in reader.recipe_instructions:
            session.add(inst)
        session.commit()

        print("✓ Database populated successfully!")

    except Exception as e:
        print(f"Error populating database: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()