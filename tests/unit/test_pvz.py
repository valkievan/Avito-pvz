import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, timezone
from app.models.pvz import PVZCreate, PVZ
from app.services.pvz import create_pvz, get_pvz, get_pvzs_with_pagination_and_filtering

@pytest.mark.asyncio
async def test_create_pvz():
    """Тестирует создание нового ПВЗ."""
    # Подготовка данных
    pvz_data = PVZCreate(city="Москва")
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": pvz_id,
        "city": "Москва",
        "registration_date": datetime.now(timezone.utc)
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.pvz.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await create_pvz(pvz_data)
    
    # Проверка результатов
    assert isinstance(result, PVZ)
    assert result.id == pvz_id
    assert result.city == "Москва"

@pytest.mark.asyncio
async def test_create_pvz_invalid_city():
    """Тестирует создание ПВЗ с неверным городом."""
    # Подготовка данных
    # Вместо создания модели с неверным городом, будем патчить валидацию
    with patch("app.models.pvz.PVZBase.model_validate", return_value=PVZCreate(city="Москва")):
        # Создаем объект с неверным городом напрямую для передачи в функцию
        pvz_data = MagicMock()
        pvz_data.city = "Новосибирск"
        
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await create_pvz(pvz_data)
    
    assert exc_info.value.status_code == 400
    assert "City must be one of" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_pvz():
    """Тестирует получение ПВЗ по ID."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": pvz_id,
        "city": "Москва",
        "registration_date": datetime.now(timezone.utc)
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.pvz.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await get_pvz(pvz_id)
    
    # Проверка результатов
    assert isinstance(result, PVZ)
    assert result.id == pvz_id
    assert result.city == "Москва"

@pytest.mark.asyncio
async def test_get_pvz_not_found():
    """Тестирует получение несуществующего ПВЗ."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # ПВЗ не найден
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.pvz.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await get_pvz(pvz_id)
    
    assert exc_info.value.status_code == 404
    assert "PVZ not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_pvzs_with_pagination_and_filtering():
    """Тестирует получение списка ПВЗ с пагинацией и фильтрацией."""
    # Подготовка данных
    pvz1_id = uuid.uuid4()
    pvz2_id = uuid.uuid4()
    reception1_id = uuid.uuid4()
    reception2_id = uuid.uuid4()
    
    # Мокируем get_db_cursor для разных запросов
    db_cursor_mock = MagicMock()
    
    # Мок для первого вызова - получение общего количества
    db_cursor_mock.fetchone.return_value = {"total": 2}
    
    # Мок для второго вызова - получение списка ПВЗ
    db_cursor_mock.fetchall.side_effect = [
        # Первый вызов fetchall - список ПВЗ
        [
            {
                "id": pvz1_id,
                "city": "Москва",
                "registration_date": datetime.now(timezone.utc)
            },
            {
                "id": pvz2_id,
                "city": "Санкт-Петербург",
                "registration_date": datetime.now(timezone.utc)
            }
        ],
        # Второй вызов fetchall - детали для первого ПВЗ
        [
            {
                "pvz_id": pvz1_id,
                "registration_date": datetime.now(timezone.utc),
                "city": "Москва",
                "reception_id": reception1_id,
                "date_time": datetime.now(timezone.utc),
                "status": "close",
                "product_id": None,
                "product_date_time": None,
                "type": None
            }
        ],
        # Третий вызов fetchall - детали для второго ПВЗ
        [
            {
                "pvz_id": pvz2_id,
                "registration_date": datetime.now(timezone.utc),
                "city": "Санкт-Петербург",
                "reception_id": reception2_id,
                "date_time": datetime.now(timezone.utc),
                "status": "in_progress",
                "product_id": None,
                "product_date_time": None,
                "type": None
            }
        ]
    ]
    
    # Создаем мок для контекстного менеджера
    mock_context = MagicMock()
    mock_context.__enter__.return_value = db_cursor_mock
    
    # Патчим все необходимые функции
    with patch("app.services.pvz.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await get_pvzs_with_pagination_and_filtering(page=1, limit=10)
    
    # Проверка результатов
    assert result["total"] == 2
    assert result["page"] == 1
    assert result["limit"] == 10
    assert len(result["items"]) == 2
    assert result["items"][0]["pvz"]["id"] == pvz1_id
    assert result["items"][0]["pvz"]["city"] == "Москва"
    assert result["items"][1]["pvz"]["id"] == pvz2_id
    assert result["items"][1]["pvz"]["city"] == "Санкт-Петербург"

@pytest.mark.asyncio
async def test_get_pvzs_with_date_filtering():
    """Тестирует получение списка ПВЗ с фильтрацией по дате."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 1, 31, tzinfo=timezone.utc)
    
    # Мокируем get_db_cursor для разных запросов
    db_cursor_mock = MagicMock()
    
    # Мок для первого вызова - получение общего количества с фильтром по дате
    db_cursor_mock.fetchone.return_value = {"total": 1}
    
    # Мок для второго вызова - получение списка ПВЗ с фильтром по дате
    db_cursor_mock.fetchall.side_effect = [
        # Первый вызов fetchall - список ПВЗ
        [
            {
                "id": pvz_id,
                "city": "Москва",
                "registration_date": datetime(2023, 1, 15, tzinfo=timezone.utc)
            }
        ],
        # Второй вызов fetchall - детали для ПВЗ
        [
            {
                "pvz_id": pvz_id,
                "registration_date": datetime(2023, 1, 15, tzinfo=timezone.utc),
                "city": "Москва",
                "reception_id": reception_id,
                "date_time": datetime(2023, 1, 15, tzinfo=timezone.utc),
                "status": "close",
                "product_id": None,
                "product_date_time": None,
                "type": None
            }
        ]
    ]
    
    # Создаем мок для контекстного менеджера
    mock_context = MagicMock()
    mock_context.__enter__.return_value = db_cursor_mock
    
    # Патчим все необходимые функции
    with patch("app.services.pvz.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции с фильтрацией по дате
        result = await get_pvzs_with_pagination_and_filtering(
            page=1, limit=10, start_date=start_date, end_date=end_date
        )
    
    # Проверка результатов
    assert result["total"] == 1
    assert len(result["items"]) == 1
    assert result["items"][0]["pvz"]["id"] == pvz_id
    assert result["items"][0]["pvz"]["city"] == "Москва"