from typing import List, Optional, Tuple
from sqlalchemy import func, asc, desc, and_
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound

from recipe.adapters.repository import AbstractRepository
from recipe.domainmodel.recipe import Recipe
from recipe.domainmodel.author import Author
from recipe.domainmodel.category import Category
from recipe.domainmodel.nutrition import Nutrition
from recipe.domainmodel.user import User
from recipe.domainmodel.review import Review
from recipe.domainmodel.favourite import Favourite
from recipe.domainmodel.recipe_image import RecipeImage
from recipe.domainmodel.recipe_ingredient import RecipeIngredient
from recipe.domainmodel.recipe_instruction import RecipeInstruction



class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory)

    def close_current_session(self):
        if self.__session is not None:
            self.__session.close()


class DatabaseRepository(AbstractRepository):
    """Database implementation matching YOUR AbstractRepository interface."""

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    # ---------- helpers for sorting/filters ----------

    @staticmethod
    def _norm_dir(sort_dir: Optional[str]) -> str:
        return "desc" if str(sort_dir or "asc").lower() == "desc" else "asc"

    @staticmethod
    def _norm_str(val: Optional[str]) -> Optional[str]:
        v = (val or "").strip()
        return v if v else None


    # ===========================
    # RECIPE METHODS
    # ===========================

    def add_recipe(self, recipe: Recipe):
        with self._session_cm as scm:
            scm.session.add(recipe)
            scm.commit()

    def get_recipe(self, recipe_id: int) -> Optional[Recipe]:
        try:
            recipe = self._session_cm.session.query(Recipe).filter(
                Recipe._Recipe__id == recipe_id
            ).one()
            self._populate_recipe_data(recipe)
            return recipe
        except NoResultFound:
            return None

    def get_recipe_by_id(self, recipe_id: int) -> Optional[Recipe]:
        return self.get_recipe(recipe_id)

    def get_all_recipes(self) -> List[Recipe]:
        recipes = self._session_cm.session.query(Recipe).all()
        self._bulk_populate_recipe_data(recipes)  # CHANGED
        return recipes

    def get_recipes_by_page(
            self,
            page: int,
            per_page: int,
            sort_by: Optional[str] = None,
            sort_dir: Optional[str] = "asc",
    ) -> List["Recipe"]:
        page = max(1, int(page or 1))
        per_page = max(1, int(per_page or 12))
        s = self._session_cm.session

        q = s.query(Recipe)

        # normalize
        sb = (sort_by or "").lower()
        dir_fn = desc if (str(sort_dir or "asc").lower() == "desc") else asc

        # defaults
        order_col = Recipe._Recipe__id
        then_col = func.lower(Recipe._Recipe__name)

        if sb in ("name", "title"):
            order_col = func.lower(Recipe._Recipe__name)
            then_col = Recipe._Recipe__id

        elif sb in ("id",):
            order_col = Recipe._Recipe__id
            then_col = func.lower(Recipe._Recipe__name)

        elif sb in ("rating",):
            from recipe.adapters.orm import reviews_table, recipes_table
            q = q.outerjoin(
                reviews_table,
                reviews_table.c.recipe_id == recipes_table.c.id
            )
            order_col = func.coalesce(func.avg(reviews_table.c.rating), 0.0)
            then_col = func.lower(Recipe._Recipe__name)
            q = q.group_by(Recipe._Recipe__id)



        elif sb in ("author",):
            q = q.join(Recipe._Recipe__author)
            order_col = func.lower(Author._Author__name)
            then_col = func.lower(Recipe._Recipe__name)
            q = q.group_by(Recipe._Recipe__id)

        elif sb in ("category", "categories"):
            q = q.join(Recipe._Recipe__category)
            order_col = func.lower(Category._Category__name)
            then_col = func.lower(Recipe._Recipe__name)
            q = q.group_by(Recipe._Recipe__id)

        # apply sorting
        q = q.order_by(dir_fn(order_col), asc(then_col))

        items = q.offset((page - 1) * per_page).limit(per_page).all()
        self._bulk_populate_recipe_data(items)
        return items

    def get_total_recipe_count(self) -> int:
        return self._session_cm.session.query(Recipe).count()

    def search_recipes(self, query: str, category: str, author: str, ingredient: str) -> List[Recipe]:
        """YOUR search_recipes signature."""
        q = self._session_cm.session.query(Recipe)

        if query:
            q = q.filter(Recipe._Recipe__name.ilike(f'%{query}%'))
        if category:
            q = q.join(Recipe._Recipe__category).filter(Category._Category__name.ilike(f'%{category}%'))
        if author:
            q = q.join(Recipe._Recipe__author).filter(Author._Author__name.ilike(f'%{author}%'))
        if ingredient:
            # Search in ingredients
            recipe_ids = self._session_cm.session.query(RecipeIngredient._RecipeIngredient__recipe_id).filter(
                RecipeIngredient._RecipeIngredient__ingredient.ilike(f'%{ingredient}%')
            ).distinct().all()
            recipe_ids = [rid[0] for rid in recipe_ids]
            q = q.filter(Recipe._Recipe__id.in_(recipe_ids))

        recipes = q.distinct(Recipe._Recipe__id).all()
        self._bulk_populate_recipe_data(recipes)  # CHANGED
        return recipes

    def search_recipes_paged(
            self,
            query: Optional[str],
            category: Optional[str],
            author: Optional[str],
            ingredient: Optional[str],
            page: int,
            per_page: int,
            sort_by: Optional[str] = None,
            sort_dir: Optional[str] = "asc",
    ):
        page = max(1, int(page or 1))
        per_page = max(1, int(per_page or 12))

        q_str = self._norm_str(query)
        c_str = self._norm_str(category)
        a_str = self._norm_str(author)
        i_str = self._norm_str(ingredient)

        s = self._session_cm.session
        base = s.query(Recipe)
        count_q = s.query(func.count(func.distinct(Recipe._Recipe__id)))

        # --- filters (mirror on count_q) ---
        if q_str:
            like = f"%{q_str}%"
            base = base.filter(Recipe._Recipe__name.ilike(like))
            count_q = count_q.filter(Recipe._Recipe__name.ilike(like))

        if a_str:
            like = f"%{a_str}%"
            base = base.join(Recipe._Recipe__author).filter(Author._Author__name.ilike(like))
            count_q = count_q.join(Recipe._Recipe__author).filter(Author._Author__name.ilike(like))

        if c_str:
            like = f"%{c_str}%"
            base = base.join(Recipe._Recipe__category).filter(Category._Category__name.ilike(like))
            count_q = count_q.join(Recipe._Recipe__category).filter(Category._Category__name.ilike(like))

        if i_str:
            sub_ids = (
                s.query(RecipeIngredient._RecipeIngredient__recipe_id)
                .filter(RecipeIngredient._RecipeIngredient__ingredient.ilike(f"%{i_str}%"))
                .distinct()
                .subquery()
            )
            base = base.filter(Recipe._Recipe__id.in_(sub_ids))
            count_q = count_q.filter(Recipe._Recipe__id.in_(sub_ids))

        # --- sorting ---
        sb = (sort_by or "").lower()
        dir_fn = desc if (str(sort_dir or "asc").lower() == "desc") else asc

        order_col = Recipe._Recipe__id
        then_col = func.lower(Recipe._Recipe__name)

        if sb in ("name", "title"):
            order_col = func.lower(Recipe._Recipe__name)
            then_col = Recipe._Recipe__id

        elif sb in ("id",):
            order_col = Recipe._Recipe__id
            then_col = func.lower(Recipe._Recipe__name)

        elif sb in ("rating",):
            # avoid Review→Review join ambiguity by joining via tables explicitly
            from recipe.adapters.orm import reviews_table, recipes_table
            base = base.outerjoin(
                reviews_table,
                reviews_table.c.recipe_id == recipes_table.c.id
            )
            order_col = func.coalesce(func.avg(reviews_table.c.rating), 0.0)
            then_col = func.lower(Recipe._Recipe__name)
            base = base.group_by(Recipe._Recipe__id)


        elif sb in ("author",):
            base = base.join(Recipe._Recipe__author)
            order_col = func.lower(Author._Author__name)
            then_col = func.lower(Recipe._Recipe__name)

        elif sb in ("category", "categories"):
            base = base.join(Recipe._Recipe__category)
            order_col = func.lower(Category._Category__name)
            then_col = func.lower(Recipe._Recipe__name)

        base = base.group_by(Recipe._Recipe__id).order_by(dir_fn(order_col), asc(then_col))

        total = int(count_q.scalar() or 0)
        items = base.offset((page - 1) * per_page).limit(per_page).all()
        self._bulk_populate_recipe_data(items)
        return items, total

    def _bulk_populate_recipe_data(self, recipes: List[Recipe]):
        """Load data for multiple recipes in just 3 queries instead of 3*N queries."""
        if not recipes:
            return

        recipe_ids = [r.id for r in recipes]
        session = self._session_cm.session

        # ONE query for all images
        all_images = session.query(RecipeImage).filter(
            RecipeImage._RecipeImage__recipe_id.in_(recipe_ids)
        ).order_by(RecipeImage._RecipeImage__recipe_id, RecipeImage._RecipeImage__position).all()

        # ONE query for all ingredients
        all_ingredients = session.query(RecipeIngredient).filter(
            RecipeIngredient._RecipeIngredient__recipe_id.in_(recipe_ids)
        ).order_by(RecipeIngredient._RecipeIngredient__recipe_id, RecipeIngredient._RecipeIngredient__position).all()

        # ONE query for all instructions
        all_instructions = session.query(RecipeInstruction).filter(
            RecipeInstruction._RecipeInstruction__recipe_id.in_(recipe_ids)
        ).order_by(RecipeInstruction._RecipeInstruction__recipe_id,
                   RecipeInstruction._RecipeInstruction__position).all()

        # Group by recipe_id
        images_by_recipe = {}
        for img in all_images:
            if img.recipe_id not in images_by_recipe:
                images_by_recipe[img.recipe_id] = []
            images_by_recipe[img.recipe_id].append(img.url)

        ingredients_by_recipe = {}
        quantities_by_recipe = {}
        for ing in all_ingredients:
            if ing.recipe_id not in ingredients_by_recipe:
                ingredients_by_recipe[ing.recipe_id] = []
                quantities_by_recipe[ing.recipe_id] = []
            ingredients_by_recipe[ing.recipe_id].append(ing.ingredient)
            quantities_by_recipe[ing.recipe_id].append(ing.quantity)

        instructions_by_recipe = {}
        for inst in all_instructions:
            if inst.recipe_id not in instructions_by_recipe:
                instructions_by_recipe[inst.recipe_id] = []
            instructions_by_recipe[inst.recipe_id].append(inst.step)

        # Assign to recipes
        for recipe in recipes:
            recipe._Recipe__images = images_by_recipe.get(recipe.id, [])
            recipe._Recipe__ingredients = ingredients_by_recipe.get(recipe.id, [])
            recipe._Recipe__ingredient_quantities = quantities_by_recipe.get(recipe.id, [])
            recipe._Recipe__instructions = instructions_by_recipe.get(recipe.id, [])

    def _populate_recipe_data(self, recipe: Recipe):
        """Load data for a SINGLE recipe - used by get_recipe() only."""
        if recipe is None:
            return

        # For single recipe, just use bulk method with a list of one
        self._bulk_populate_recipe_data([recipe])
    # ===========================
    # USER METHODS
    # ===========================

    def add_user(self, user: User):
        with self._session_cm as scm:
            if user.id is None:
                max_id = scm.session.query(func.max(User._User__id)).scalar()
                user.id = (max_id or 0) + 1
            scm.session.add(user)
            scm.commit()

    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return self._session_cm.session.query(User).filter(User._User__id == user_id).one()
        except NoResultFound:
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.get_user(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        try:
            return self._session_cm.session.query(User).filter(User._User__username == username).one()
        except NoResultFound:
            return None

    def next_user_id(self) -> int:
        max_id = self._session_cm.session.query(func.max(User._User__id)).scalar()
        return (max_id or 0) + 1

    # ===========================
    # REVIEW METHODS
    # ===========================

    def add_review(self, recipe_id: int, user_id: int, rating: int, comment: str):
        from datetime import datetime
        with self._session_cm as scm:
            user = scm.session.query(User).filter(User._User__id == user_id).one()
            recipe = scm.session.query(Recipe).filter(Recipe._Recipe__id == recipe_id).one()

            # --- UPSERT: try find an existing review by this user for this recipe ---
            existing = scm.session.query(Review).filter(
                Review._Review__user == user,
                Review._Review__recipe == recipe
            ).one_or_none()

            if existing:
                # Update existing review (edit)
                existing._Review__rating = rating
                existing._Review__text = comment
                existing._Review__timestamp = datetime.now()
            else:
                # Insert new review
                max_id = scm.session.query(func.max(Review._Review__id)).scalar()
                review_id = (max_id or 0) + 1
                review = Review(review_id, user, recipe, datetime.now(), rating, comment)
                scm.session.add(review)

            # --- Recompute and store the recipe's average rating ---
            avg = scm.session.query(func.avg(Review._Review__rating)).filter(
                Review._Review__recipe.has(Recipe._Recipe__id == recipe_id)
            ).scalar()
            recipe._Recipe__rating = round(float(avg), 1) if avg else None

            scm.commit()

    def reviews_for_recipe(self, recipe_id: int) -> List[Review]:
        return self._session_cm.session.query(Review).filter(
            Review._Review__recipe.has(Recipe._Recipe__id == recipe_id)
        ).order_by(desc(Review._Review__timestamp)).all()

    def average_rating(self, recipe_id: int) -> float:
        avg = self._session_cm.session.query(func.avg(Review._Review__rating)).filter(
            Review._Review__recipe.has(Recipe._Recipe__id == recipe_id)
        ).scalar()
        return float(avg) if avg else 0.0

    # ===========================
    # FAVOURITE METHODS
    # ===========================

    def add_favourite(self, user_id: int, recipe_id: int):
        with self._session_cm as scm:
            # Check if exists
            existing = scm.session.query(Favourite).filter(
                and_(
                    Favourite._Favourite__user.has(User._User__id == user_id),
                    Favourite._Favourite__recipe.has(Recipe._Recipe__id == recipe_id)
                )
            ).first()

            if not existing:
                user = scm.session.query(User).filter(User._User__id == user_id).one()
                recipe = scm.session.query(Recipe).filter(Recipe._Recipe__id == recipe_id).one()

                max_id = scm.session.query(func.max(Favourite._Favourite__id)).scalar()
                favourite_id = (max_id or 0) + 1

                favourite = Favourite(favourite_id, user, recipe)
                scm.session.add(favourite)
                scm.commit()

    def remove_favourite(self, user_id: int, recipe_id: int):
        with self._session_cm as scm:
            favourite = scm.session.query(Favourite).filter(
                and_(
                    Favourite._Favourite__user.has(User._User__id == user_id),
                    Favourite._Favourite__recipe.has(Recipe._Recipe__id == recipe_id)
                )
            ).first()

            if favourite:
                scm.session.delete(favourite)
                scm.commit()

    def favourites_for_user(self, user_id: int) -> List[Recipe]:
        favourites = self._session_cm.session.query(Favourite).filter(
            Favourite._Favourite__user.has(User._User__id == user_id)
        ).all()
        recipes = [fav.recipe for fav in favourites]
        for recipe in recipes:
            self._populate_recipe_data(recipe)
        return recipes

    # ===========================
    # UTILITY METHODS
    # ===========================

    def calculate_health_star_rating(self, recipe: Recipe) -> Optional[float]:
        """YOUR calculate_health_star_rating - copied from memory_repository."""
        nutrition = getattr(recipe, "nutrition", None)
        required = ["calories", "fat", "saturated_fat", "protein", "fiber"]
        if not nutrition or any(getattr(nutrition, k, None) is None for k in required):
            return None

        health_star = 0.0
        if nutrition.calories <= 200:
            health_star += 1
        if nutrition.fat <= 5:
            health_star += 1
        if nutrition.saturated_fat <= 2:
            health_star += 1
        if nutrition.protein >= 10:
            health_star += 1
        if nutrition.fiber >= 5:
            health_star += 1

        return max(0.0, min(5.0, health_star))

    def distinct_values(self, field: str, query: str = "", limit: int = 10) -> List[str]:
        field = (field or "").lower()
        q = (query or "").strip()
        s = self._session_cm.session

        if field in ("name", "title"):
            rows = s.query(Recipe._Recipe__name).filter(
                Recipe._Recipe__name.ilike(f"%{q}%")
            ) if q else s.query(Recipe._Recipe__name)
            return [r[0] for r in rows.distinct().limit(limit).all()]

        if field == "category":
            rows = s.query(Category._Category__name).filter(
                Category._Category__name.ilike(f"%{q}%")
            ) if q else s.query(Category._Category__name)
            return [r[0] for r in rows.distinct().limit(limit).all()]

        if field == "author":
            rows = s.query(Author._Author__name).filter(
                Author._Author__name.ilike(f"%{q}%")
            ) if q else s.query(Author._Author__name)
            return [r[0] for r in rows.distinct().limit(limit).all()]

        if field == "ingredient":
            rows = s.query(RecipeIngredient._RecipeIngredient__ingredient).filter(
                RecipeIngredient._RecipeIngredient__ingredient.ilike(f"%{q}%")
            ) if q else s.query(RecipeIngredient._RecipeIngredient__ingredient)
            return [r[0] for r in rows.distinct().limit(limit).all()]

        return []
