# tests/unit/test_auth_services.py

import pytest

from recipe.adapters.memory_repository import MemoryRepository
from recipe.authentication.services import (
    add_user,
    get_user,
    authenticate_user,
    NameNotUniqueException,
    UnknownUserException,
    AuthenticationException,
)

@pytest.fixture
def repo():
    # Fresh in-memory repo per test
    return MemoryRepository()

def test_add_user_success_hashes_password_and_assigns_id(repo):
    add_user("alice", "StrongPass123", repo)
    u = repo.get_user_by_username("alice")

    assert u is not None
    assert u.username == "alice"
    # password must be hashed (i.e., not equal to plaintext)
    assert u.password != "StrongPass123"
    # id assigned
    assert isinstance(u.id, int) and u.id >= 1

def test_add_user_duplicate_raises(repo):
    add_user("alice", "StrongPass123", repo)
    with pytest.raises(NameNotUniqueException):
        add_user("alice", "AnotherPass456", repo)

def test_get_user_success_returns_dict(repo):
    add_user("bob", "ValidPass123", repo)
    user_dict = get_user("bob", repo)

    assert isinstance(user_dict, dict)
    assert user_dict["username"] == "bob"
    # returns hashed password field (string), not plaintext
    assert isinstance(user_dict["password"], str)
    assert user_dict["password"] != "ValidPass123"

def test_get_user_unknown_raises(repo):
    with pytest.raises(UnknownUserException):
        get_user("nope", repo)

def test_authenticate_user_success_returns_user(repo):
    add_user("carol", "SecretPass123", repo)
    user = authenticate_user("carol", "SecretPass123", repo)

    # services.authenticate_user returns the User object
    assert user is not None
    assert user.username == "carol"

def test_authenticate_user_wrong_password_raises(repo):
    add_user("dave", "RightPass123", repo)
    with pytest.raises(AuthenticationException):
        authenticate_user("dave", "WrongPass999", repo)

def test_authenticate_user_unknown_user_raises(repo):
    # In services.authenticate_user, unknown user also triggers AuthenticationException
    with pytest.raises(AuthenticationException):
        authenticate_user("ghost", "anything", repo)

def test_repo_user_indexing_by_username_and_id(repo):
    add_user("eve", "Pass12345A", repo)
    u_by_username = repo.get_user_by_username("eve")
    u_by_id = repo.get_user(u_by_username.id)

    assert u_by_username is not None
    assert u_by_id is not None
    assert u_by_username is u_by_id

pytest.raises(ValueError)