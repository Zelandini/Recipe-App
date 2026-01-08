from werkzeug.security import generate_password_hash, check_password_hash
from dataclasses import dataclass
from sqlalchemy.exc import IntegrityError

from recipe.adapters.repository import AbstractRepository
from recipe.domainmodel.user import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass



def add_user(username: str, password: str, repo: AbstractRepository):
    """
    Add a new user to the repository, hashing their password.

    Raises:
        NameNotUniqueException: If the username already exists
    """
    # Check for duplicate username before DB commit
    existing = repo.get_user_by_username(username)
    if existing is not None:
        raise NameNotUniqueException

    # Encrypt password so that the database doesn't store it in clear text
    password_hash = generate_password_hash(password)
    user = User(username, password_hash)

    # Add to repository with DB integrity safety
    try:
        repo.add_user(user)
    except IntegrityError:
        # In case of race condition with unique constraint
        raise NameNotUniqueException


def get_user(username: str, repo: AbstractRepository):
    """
    Retrieve a user by username.

    Raises:
        UnknownUserException: If user not found
    """
    user = repo.get_user_by_username(username)
    if user is None:
        raise UnknownUserException
    return user_to_dict(user)


def authenticate_user(username: str, password: str, repo: AbstractRepository):
    """
    Authenticate user credentials using password hashing.

    Raises:
        UnknownUserException: If username not found
        AuthenticationException: If password mismatch
    """
    user = repo.get_user_by_username(username)
    if user is None:
        raise AuthenticationException

    # Verify hashed password
    if not check_password_hash(user.password, password):
        raise AuthenticationException

    # Return full user model for session tracking
    return user


# ===============================
# Helper Conversion
# ===============================
def user_to_dict(user: User):
    """Convert a User object to a dictionary representation."""
    return {
        "id": getattr(user, "id", None),
        "username": user.username,
        "password": user.password,  # hashed password for completeness
    }