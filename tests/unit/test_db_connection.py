import pytest
from unittest.mock import patch, MagicMock
import psycopg2
from contextlib import contextmanager

from app.db.connection import get_db_connection, get_db_cursor

def test_get_db_connection():
    """Тестирует создание соединения с базой данных."""
    # Мокируем функцию psycopg2.connect
    with patch("psycopg2.connect") as mock_connect:
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection
        
        # Вызов тестируемой функции
        result = get_db_connection()
    
    # Проверка результатов
    assert result == mock_connection
    mock_connect.assert_called_once()

def test_get_db_connection_error():
    """Тестирует обработку ошибки при соединении с базой данных."""
    # Мокируем функцию psycopg2.connect, которая вызывает исключение
    with patch("psycopg2.connect", side_effect=Exception("Connection error")):
        # Проверка исключения
        with pytest.raises(Exception) as exc_info:
            get_db_connection()
    
    assert "Connection error" in str(exc_info.value)

def test_get_db_cursor():
    """Тестирует получение курсора базы данных."""
    # Создаем мок для курсора
    mock_cursor = MagicMock()
    
    # Создаем контекстный менеджер, который возвращает мок курсора
    @contextmanager
    def mock_cursor_context():
        yield mock_cursor
    
    # Создаем мок для соединения с базой данных
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor_context()
    
    # Мокируем функцию get_db_connection
    with patch("app.db.connection.get_db_connection", return_value=mock_connection):
        # Используем контекстный менеджер get_db_cursor
        with get_db_cursor() as cursor:
            # Выполняем тестовую операцию
            cursor.execute("SELECT 1")
    
    # Проверка вызовов методов
    mock_cursor.execute.assert_called_once_with("SELECT 1")
    mock_connection.commit.assert_called_once()
    mock_connection.close.assert_called_once()

def test_get_db_cursor_with_exception():
    """Тестирует обработку исключения в контекстном менеджере get_db_cursor."""
    # Создаем мок для курсора, который вызывает исключение
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Query error")
    
    # Создаем контекстный менеджер, который возвращает мок курсора
    @contextmanager
    def mock_cursor_context():
        yield mock_cursor
    
    # Создаем мок для соединения с базой данных
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor_context()
    
    # Мокируем функцию get_db_connection
    with patch("app.db.connection.get_db_connection", return_value=mock_connection):
        # Проверка обработки исключения в контекстном менеджере
        with pytest.raises(Exception) as exc_info:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT 1")
    
    # Проверка, что была вызвана операция rollback
    mock_connection.rollback.assert_called_once()
    mock_connection.close.assert_called_once()
    
    assert "Query error" in str(exc_info.value)