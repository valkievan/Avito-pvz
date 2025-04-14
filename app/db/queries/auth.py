from uuid import UUID

import bcrypt

from app.models.auth import UserCreate


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_user_query(user: UserCreate) -> tuple:
    query = """
    INSERT INTO users (email, password_hash, role)
    VALUES (%s, %s, %s)
    RETURNING id, email, role
    """
    params = (user.email, hash_password(user.password), user.role)
    return query, params


def get_user_by_email_query(email: str) -> tuple:
    query = """
    SELECT id, email, password_hash, role
    FROM users
    WHERE email = %s
    """
    params = (email,)
    return query, params


def get_user_by_id_query(user_id: UUID) -> tuple:
    query = """
    SELECT id, email, role
    FROM users
    WHERE id = %s
    """
    params = (str(user_id),)
    return query, params
