from fastapi import APIRouter, HTTPException, status

from app.models.auth import DummyLoginRequest, LoginRequest, Token, User, UserCreate
from app.services.auth import (
    authenticate_user,
    create_access_token,
    create_dummy_token,
    register_user,
)

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED, summary="Регистрация")
async def register(user: UserCreate):
    return await register_user(user)


@router.post("/login", response_model=Token, summary="Вход")
async def login(login_data: LoginRequest):
    user = await authenticate_user(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await create_access_token(user.id, user.role)


@router.post("/dummyLogin", response_model=Token, summary="Тестовый токен")
async def dummy_login(login_data: DummyLoginRequest):
    return await create_dummy_token(login_data.role)
