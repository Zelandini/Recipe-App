# recipe/authentication/services.py
from werkzeug.security import generate_password_hash, check_password_hash

from recipe.adapters.repository import AbstractRepository
from recipe.domainmodel.user import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(user_name: str, password: str, repo: AbstractRepository):
    """
    Add a new user to the repository.

    Args:
        user_name: The user's chosen username
        password: The user's password (will be hashed)
        repo: The repository instance

    Raises:
        NameNotUniqueException: If the username is already taken
    """
    # Check that the given user name is available.
    user = repo.get_user(user_name)
    if user is not None:
        raise NameNotUniqueException

    # Encrypt password so that the database doesn't store passwords 'in the clear'.
    password_hash = generate_password_hash(password)

    # Create and store the new User, with password encrypted.
    user = User(user_name, password_hash)
    repo.add_user(user)


def get_user(user_name: str, repo: AbstractRepository):
    """
    Get user information by username.

    Args:
        user_name: The username to look up
        repo: The repository instance

    Returns:
        dict: User information dictionary

    Raises:
        UnknownUserException: If the user doesn't exist
    """
    user = repo.get_user(user_name)
    if user is None:
        raise UnknownUserException

    return user_to_dict(user)


def authenticate_user(user_name: str, password: str, repo: AbstractRepository):
    """
    Authenticate a user with username and password.

    Args:
        user_name: The username
        password: The password to verify
        repo: The repository instance

    Returns:
        User: The authenticated user object

    Raises:
        UnknownUserException: If the user doesn't exist
        AuthenticationException: If the password is incorrect
    """
    authenticated = False

    user = repo.get_user(user_name)
    if user is not None:
        authenticated = check_password_hash(user.password, password)

    if not authenticated:
        raise AuthenticationException

    # Return the user object for session storage
    return user


# ===================================================
# Functions to convert model entities to dictionaries
# ===================================================

def user_to_dict(user: User):
    """
    Convert a User object to a dictionary representation.

    Args:
        user: The User object to convert

    Returns:
        dict: User information as dictionary
    """
    user_dict = {
        'user_name': user.username,
        'password': user.password  # This is the hashed password
    }
    return user_dict
