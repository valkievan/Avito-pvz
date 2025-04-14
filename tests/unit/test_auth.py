import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.models.auth import UserCreate, User, UserInDB
from app.services.auth import register_user, authenticate_user, create_access_token, create_dummy_token
import bcrypt

@pytest.mark.asyncio
async def test_register_user():
    """Тестирует регистрацию пользователя."""
    # Подготовка данных
    user_data = UserCreate(email="test@example.com", password="password123", role="employee")
    user_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [None, {"id": user_id, "email": "test@example.com", "role": "employee"}]
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor перед вызовом тестируемой функции
    with patch("app.services.auth.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await register_user(user_data)
    
    # Проверка результатов
    assert isinstance(result, User)
    assert result.email == "test@example.com"
    assert result.role == "employee"

@pytest.mark.asyncio
async def test_register_user_existing_email():
    """Тестирует попытку регистрации с существующим email."""
    # Подготовка данных
    user_data = UserCreate(email="existing@example.com", password="password123", role="employee")
    existing_user_id = uuid.uuid4()
    
    # Создаем мок для cursor, который всегда возвращает пользователя (email существует)
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {"id": existing_user_id, "email": "existing@example.com", "role": "employee"}
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor перед вызовом тестируемой функции
    with patch("app.services.auth.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await register_user(user_data)
    
    assert exc_info.value.status_code == 400
    assert "Email already registered" in exc_info.value.detail

@pytest.mark.asyncio
async def test_authenticate_user():
    """Тестирует аутентификацию пользователя."""
    # Подготовка данных
    email = "test@example.com"
    password = "password123"
    user_id = uuid.UUID("63bde4ec-1382-4733-aab9-a75f7d9da567")  # Фиксированный UUID для соответствия возвращаемому
    
    # Создаем правильный хеш bcrypt для тестов
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": user_id, 
        "email": email, 
        "role": "employee", 
        "password_hash": hashed_password
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor (функцию verify_password не патчим, она будет работать с корректным хешем)
    with patch("app.services.auth.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await authenticate_user(email, password)
    
    # Проверка результатов
    assert result is not None
    assert isinstance(result, UserInDB)
    assert result.email == email
    assert result.role == "employee"
    assert result.id == user_id

@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials():
    """Тестирует аутентификацию с неверными учетными данными."""
    # Подготовка данных
    email = "test@example.com"
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    user_id = uuid.uuid4()
    
    # Создаем правильный хеш bcrypt для тестов (хешируем correct_password)
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(correct_password.encode('utf-8'), salt).decode('utf-8')
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": user_id, 
        "email": email, 
        "role": "employee", 
        "password_hash": hashed_password
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor (но не патчим verify_password - мы используем wrong_password, поэтому проверка не пройдет)
    with patch("app.services.auth.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции с неверным паролем
        result = await authenticate_user(email, wrong_password)
    
    # Проверка результатов
    assert result is None

@pytest.mark.asyncio
async def test_dummy_login_valid_role():
    """Тестирует создание тестового токена для валидной роли."""
    # Патчим функцию create_jwt_token в модуле app.services.auth, а не в app.utils.auth
    with patch("app.services.auth.create_jwt_token", return_value="test_token"):
        # Вызов тестируемой функции
        result = await create_dummy_token("employee")
        
        # Проверка результатов
        assert result is not None
        assert result.access_token == "test_token"
        assert result.token_type == "bearer"

@pytest.mark.asyncio
async def test_dummy_login_invalid_role():
    """Тестирует создание тестового токена для невалидной роли."""
    # Проверка исключения
    with pytest.raises(HTTPException) as exc_info:
        await create_dummy_token("invalid_role")
    
    assert exc_info.value.status_code == 400
    assert "Role must be employee or moderator" in exc_info.value.detail