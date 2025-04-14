import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import uuid

from app.api.dependencies import (
    get_current_user, 
    get_current_employee_or_moderator, 
    check_if_moderator, 
    check_if_employee
)

@pytest.mark.asyncio
async def test_get_current_user():
    """Тестирует получение текущего пользователя по токену."""
    # Подготовка данных
    test_token = "test_jwt_token"
    user_id = str(uuid.uuid4())
    payload = {"sub": user_id, "role": "employee"}
    
    # Патчим decode_jwt_token
    with patch("app.api.dependencies.decode_jwt_token", return_value=payload):
        # Вызов тестируемой функции
        result = await get_current_user(test_token)
    
    # Проверка результатов
    assert result["user_id"] == user_id
    assert result["role"] == "employee"

@pytest.mark.asyncio
async def test_get_current_employee_or_moderator_with_employee():
    """Тестирует проверку роли сотрудника или модератора - для сотрудника."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "employee"}
    
    # Вызов тестируемой функции
    result = await get_current_employee_or_moderator(current_user)
    
    # Проверка результатов
    assert result == current_user

@pytest.mark.asyncio
async def test_get_current_employee_or_moderator_with_moderator():
    """Тестирует проверку роли сотрудника или модератора - для модератора."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "moderator"}
    
    # Вызов тестируемой функции
    result = await get_current_employee_or_moderator(current_user)
    
    # Проверка результатов
    assert result == current_user

@pytest.mark.asyncio
async def test_get_current_employee_or_moderator_invalid_role():
    """Тестирует проверку роли сотрудника или модератора - с неверной ролью."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "invalid_role"}
    
    # Проверка исключения
    with pytest.raises(HTTPException) as exc_info:
        await get_current_employee_or_moderator(current_user)
    
    assert exc_info.value.status_code == 403
    assert "Insufficient permissions" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_current_moderator_valid():
    """Тестирует проверку роли модератора - для модератора."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "moderator"}
    
    # Вызов тестируемой функции
    result = await check_if_moderator(current_user)
    
    # Проверка результатов
    assert result == current_user

@pytest.mark.asyncio
async def test_get_current_moderator_invalid_role():
    """Тестирует проверку роли модератора - с неверной ролью."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "employee"}
    
    # Проверка исключения
    with pytest.raises(HTTPException) as exc_info:
        await check_if_moderator(current_user)
    
    assert exc_info.value.status_code == 403
    assert "Only moderators can perform this action" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_current_employee_valid():
    """Тестирует проверку роли сотрудника - для сотрудника."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "employee"}
    
    # Вызов тестируемой функции
    result = await check_if_employee(current_user)
    
    # Проверка результатов
    assert result == current_user

@pytest.mark.asyncio
async def test_get_current_employee_invalid_role():
    """Тестирует проверку роли сотрудника - с неверной ролью."""
    # Подготовка данных
    current_user = {"user_id": str(uuid.uuid4()), "role": "moderator"}
    
    # Проверка исключения
    with pytest.raises(HTTPException) as exc_info:
        await check_if_employee(current_user)
    
    assert exc_info.value.status_code == 403
    assert "Only employees can perform this action" in exc_info.value.detail