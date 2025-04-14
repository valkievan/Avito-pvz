import pytest
from unittest.mock import patch, MagicMock
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Создание цикла событий для асинхронных тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_db_cursor():
    """Мокает курсор базы данных для unit-тестов."""
    mock_cursor = MagicMock()
    return mock_cursor
