# Recipe Portal

This is a collaborative projects for CS235 at the University of Auckland.

A Flask web application for browsing, reviewing, and favouriting recipes. The project includes
domain models, repository adapters (database and in-memory), and a UI for searching and viewing
recipes sourced from a bundled CSV dataset.

## Features

- Home page with featured recipes and a recipe of the day.
- Browse page with search, filtering, pagination, and sorting.
- Recipe detail pages that include ingredients, instructions, nutrition, and ratings.
- User authentication (register/login/logout).
- Reviews and favourites for logged-in users.
- Health Star Rating calculated from per-serving nutrition values.
- Optional API endpoint for browse autocomplete options.

## Project structure

- `recipe/` – Flask application, blueprints, templates, and static assets.
  - `adapters/` – repository implementations and CSV/ORM data handling.
  - `domainmodel/` – entities such as `Recipe`, `User`, `Review`, etc.
  - `services/` – application services for recipes, browse, favourites, and reviews.
- `tests/` – unit, integration, and end-to-end tests.
- `wsgi.py` – application entry point.
- `requirements.txt` – runtime and test dependencies.

## Requirements

- Python 3.10+

Install dependencies:

```shell
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

## Configuration

The application reads settings from environment variables (or a `.env` file if using
`python-dotenv`):

- `FLASK_APP`: `wsgi.py`
- `FLASK_ENV`: `development` or `production`
- `SECRET_KEY`: Flask session secret
- `REPOSITORY`: `database` (default) or `memory`
- `DATABASE_URL`: SQLAlchemy DB URL (default: `sqlite:///recipes.db`)

## Running the app

```shell
flask run
```

By default, the app runs in database mode, creates `recipes.db` if needed, and populates it
from `recipe/adapters/data/recipes.csv` on first run.

To run with the in-memory repository:

```shell
REPOSITORY=memory flask run
```

## API endpoints

- `GET /api/browse/options?field=author&q=an&limit=10` – returns distinct values for type-ahead
  suggestions used in the browse page.

## Testing

```shell
pytest
```

## Data source

Recipe data is a modified excerpt from:
https://www.kaggle.com/datasets/irkaal/foodcom-recipes-and-reviews/
