import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
import uuid

from app.api.auth import register, login, dummy_login
from app.models.auth import UserCreate, Token, LoginRequest, DummyLoginRequest

@pytest.mark.asyncio
async def test_register():
    """Тестирует регистрацию пользователя через API."""
    # Подготовка данных
    user_data = UserCreate(email="test@example.com", password="password123", role="employee")
    user_id = uuid.uuid4()
    expected_user = {"id": user_id, "email": "test@example.com", "role": "employee"}
    
    # Мокируем сервисную функцию
    with patch("app.api.auth.register_user", new_callable=AsyncMock) as mock_register_user:
        mock_register_user.return_value = expected_user
        
        # Вызов тестируемой функции
        result = await register(user_data)
    
    # Проверка результатов
    assert result == expected_user
    mock_register_user.assert_called_once_with(user_data)

@pytest.mark.asyncio
async def test_login_successful():
    """Тестирует успешную авторизацию через API."""
    # Подготовка данных
    login_data = LoginRequest(email="test@example.com", password="password123")
    expected_token = Token(access_token="test_token", token_type="bearer")
    
    # Мокируем сервисные функции
    with patch("app.api.auth.authenticate_user", new_callable=AsyncMock) as mock_authenticate_user, \
         patch("app.api.auth.create_access_token", new_callable=AsyncMock) as mock_create_access_token:
        
        # Настраиваем моки
        mock_authenticate_user.return_value = MagicMock(id=uuid.uuid4(), role="employee")
        mock_create_access_token.return_value = expected_token
        
        # Вызов тестируемой функции
        result = await login(login_data)
    
    # Проверка результатов
    assert result == expected_token
    mock_authenticate_user.assert_called_once_with(login_data.email, login_data.password)
    mock_create_access_token.assert_called_once()

@pytest.mark.asyncio
async def test_login_failed():
    """Тестирует неудачную авторизацию через API."""
    # Подготовка данных
    login_data = LoginRequest(email="test@example.com", password="wrong_password")
    
    # Мокируем сервисную функцию, которая возвращает None при неудачной аутентификации
    with patch("app.api.auth.authenticate_user", new_callable=AsyncMock) as mock_authenticate_user:
        mock_authenticate_user.return_value = None
        
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await login(login_data)
    
    assert exc_info.value.status_code == 401
    assert "Incorrect email or password" in exc_info.value.detail

@pytest.mark.asyncio
async def test_dummy_login():
    """Тестирует получение тестового токена."""
    # Подготовка данных
    login_data = DummyLoginRequest(role="employee")
    expected_token = Token(access_token="test_token", token_type="bearer")
    
    # Мокируем сервисную функцию
    with patch("app.api.auth.create_dummy_token", new_callable=AsyncMock) as mock_create_dummy_token:
        mock_create_dummy_token.return_value = expected_token
        
        # Вызов тестируемой функции
        result = await dummy_login(login_data)
    
    # Проверка результатов
    assert result == expected_token
    mock_create_dummy_token.assert_called_once_with(login_data.role)