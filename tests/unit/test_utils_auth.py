import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone

from app.utils.auth import create_jwt_token, decode_jwt_token
from app.config import settings

def test_create_jwt_token():
    """Тестирует создание JWT токена."""
    # Подготовка данных
    data = {"sub": "test_user_id", "role": "employee"}
    expires_delta = timedelta(minutes=30)
    
    # Мокируем функцию jwt.encode
    with patch("jwt.encode", return_value="test_encoded_token") as mock_encode:
        # Вызов тестируемой функции
        result = create_jwt_token(data, expires_delta)
    
    # Проверка результатов
    assert result == "test_encoded_token"
    
    # Проверяем, что jwt.encode вызвана с правильными параметрами
    # jwt.encode в версии pyjwt 2.x принимает аргументы по-другому
    mock_encode.assert_called_once()
    args, kwargs = mock_encode.call_args
    assert len(args) >= 2
    assert args[1] == settings.JWT_SECRET_KEY  # Проверка секретного ключа
    assert kwargs.get('algorithm') == settings.JWT_ALGORITHM  # Проверка алгоритма

def test_create_jwt_token_default_expiry():
    """Тестирует создание JWT токена с дефолтным временем истечения."""
    # Подготовка данных
    data = {"sub": "test_user_id", "role": "employee"}
    
    # Мокируем функцию jwt.encode
    with patch("jwt.encode", return_value="test_encoded_token") as mock_encode:
        # Вызов тестируемой функции
        result = create_jwt_token(data)
    
    # Проверка результатов
    assert result == "test_encoded_token"
    
    # Проверяем, что в данных для токена добавлено поле exp
    payload = mock_encode.call_args[0][0]
    assert "exp" in payload

def test_decode_jwt_token_valid():
    """Тестирует декодирование валидного JWT токена."""
    # Подготовка данных
    token = "test_token"
    payload = {"sub": "test_user_id", "role": "employee"}
    
    # Мокируем функцию jwt.decode
    with patch("jwt.decode", return_value=payload) as mock_decode:
        # Вызов тестируемой функции
        result = decode_jwt_token(token)
    
    # Проверка результатов
    assert result == payload
    mock_decode.assert_called_once_with(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

def test_decode_jwt_token_invalid():
    """Тестирует декодирование невалидного JWT токена."""
    # Подготовка данных
    token = "invalid_token"
    
    # Мокируем функцию jwt.decode, которая вызывает исключение
    with patch("jwt.decode", side_effect=jwt.PyJWTError("Token is invalid")):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            decode_jwt_token(token)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail