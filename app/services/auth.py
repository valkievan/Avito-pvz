from datetime import timedelta

from fastapi import HTTPException, status

from app.config import settings
from app.db.connection import get_db_cursor
from app.db.queries.auth import create_user_query, get_user_by_email_query, verify_password
from app.models.auth import Token, User, UserCreate, UserInDB
from app.utils.auth import create_jwt_token


async def register_user(user: UserCreate) -> User:
    with get_db_cursor() as cursor:
        query, params = get_user_by_email_query(user.email)
        cursor.execute(query, params)
        existing_user = cursor.fetchone()

        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        query, params = create_user_query(user)
        cursor.execute(query, params)
        new_user = cursor.fetchone()

        return User(id=new_user["id"], email=new_user["email"], role=new_user["role"])


async def authenticate_user(email: str, password: str) -> UserInDB:
    with get_db_cursor() as cursor:
        query, params = get_user_by_email_query(email)
        cursor.execute(query, params)
        user_data = cursor.fetchone()

        if not user_data:
            return None

        if not verify_password(password, user_data["password_hash"]):
            return None

        return UserInDB(
            id=user_data["id"],
            email=user_data["email"],
            role=user_data["role"],
            password_hash=user_data["password_hash"],
        )


async def create_access_token(user_id: str, role: str) -> Token:
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": str(user_id), "role": role}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token)


async def create_dummy_token(role: str) -> Token:
    if role not in ["employee", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be employee or moderator"
        )

    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(
        data={"sub": "00000000-0000-0000-0000-000000000000", "role": role}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token)
