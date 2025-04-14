import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from datetime import datetime, timezone
from app.models.reception import ReceptionCreate, Reception
from app.services.reception import create_reception, get_reception, get_active_reception, close_reception

@pytest.mark.asyncio
async def test_create_reception():
    """Тестирует создание новой приемки."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    reception_data = ReceptionCreate(pvz_id=pvz_id)
    
    # Создаем мок для get_pvz (проверка существования ПВЗ)
    with patch("app.services.reception.get_pvz") as mock_get_pvz:
        mock_get_pvz.return_value = MagicMock()  # Не важно что возвращает, главное не вызывать ошибку
        
        # Создаем мок для cursor
        mock_cursor = MagicMock()
        
        # Мок для проверки активной приемки
        mock_cursor.fetchone.side_effect = [
            None,  # Нет активной приемки
            {
                "id": reception_id,
                "date_time": datetime.now(timezone.utc),
                "pvz_id": pvz_id,
                "status": "in_progress"
            }
        ]
        
        # Создаем мок для контекстного менеджера get_db_cursor
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        
        # Патчим get_db_cursor
        with patch("app.services.reception.get_db_cursor", return_value=mock_context):
            # Вызов тестируемой функции
            result = await create_reception(reception_data)
    
    # Проверка результатов
    assert isinstance(result, Reception)
    assert result.id == reception_id
    assert result.pvz_id == pvz_id
    assert result.status == "in_progress"

@pytest.mark.asyncio
async def test_create_reception_with_active_reception():
    """Тестирует создание приемки, когда уже есть активная приемка."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    reception_data = ReceptionCreate(pvz_id=pvz_id)
    
    # Создаем мок для get_pvz (проверка существования ПВЗ)
    with patch("app.services.reception.get_pvz") as mock_get_pvz:
        mock_get_pvz.return_value = MagicMock()  # Не важно что возвращает, главное не вызывать ошибку
        
        # Создаем мок для cursor
        mock_cursor = MagicMock()
        
        # Мок для проверки активной приемки - возвращает существующую активную приемку
        mock_cursor.fetchone.return_value = {
            "id": reception_id,
            "date_time": datetime.now(timezone.utc),
            "pvz_id": pvz_id,
            "status": "in_progress"
        }
        
        # Создаем мок для контекстного менеджера get_db_cursor
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        
        # Патчим get_db_cursor
        with patch("app.services.reception.get_db_cursor", return_value=mock_context):
            # Проверка исключения
            with pytest.raises(HTTPException) as exc_info:
                await create_reception(reception_data)
    
    assert exc_info.value.status_code == 400
    assert "already an active reception" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_reception():
    """Тестирует получение приемки по ID."""
    # Подготовка данных
    reception_id = uuid.uuid4()
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": reception_id,
        "date_time": datetime.now(timezone.utc),
        "pvz_id": pvz_id,
        "status": "in_progress"
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await get_reception(reception_id)
    
    # Проверка результатов
    assert isinstance(result, Reception)
    assert result.id == reception_id
    assert result.pvz_id == pvz_id
    assert result.status == "in_progress"

@pytest.mark.asyncio
async def test_get_reception_not_found():
    """Тестирует получение несуществующей приемки."""
    # Подготовка данных
    reception_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # Приемка не найдена
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await get_reception(reception_id)
    
    assert exc_info.value.status_code == 404
    assert "Reception not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_active_reception():
    """Тестирует получение активной приемки для ПВЗ."""
    # Подготовка данных
    reception_id = uuid.uuid4()
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": reception_id,
        "date_time": datetime.now(timezone.utc),
        "pvz_id": pvz_id,
        "status": "in_progress"
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await get_active_reception(pvz_id)
    
    # Проверка результатов
    assert isinstance(result, Reception)
    assert result.id == reception_id
    assert result.pvz_id == pvz_id
    assert result.status == "in_progress"

@pytest.mark.asyncio
async def test_get_active_reception_not_found():
    """Тестирует получение активной приемки, когда ее нет."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # Активная приемка не найдена
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await get_active_reception(pvz_id)
    
    assert exc_info.value.status_code == 400
    assert "No active reception found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_close_reception():
    """Тестирует закрытие активной приемки."""
    # Подготовка данных
    reception_id = uuid.uuid4()
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    
    # Мок для получения активной приемки и ее закрытия
    mock_cursor.fetchone.side_effect = [
        {
            "id": reception_id,
            "date_time": datetime.now(timezone.utc),
            "pvz_id": pvz_id,
            "status": "in_progress"
        },
        {
            "id": reception_id,
            "date_time": datetime.now(timezone.utc),
            "pvz_id": pvz_id,
            "status": "close"
        }
    ]
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await close_reception(pvz_id)
    
    # Проверка результатов
    assert isinstance(result, Reception)
    assert result.id == reception_id
    assert result.pvz_id == pvz_id
    assert result.status == "close"

@pytest.mark.asyncio
async def test_close_reception_no_active_reception():
    """Тестирует закрытие приемки, когда нет активной приемки."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None  # Нет активной приемки
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await close_reception(pvz_id)
    
    assert exc_info.value.status_code == 400
    assert "No active reception found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_close_reception_failure():
    """Тестирует ситуацию, когда не удалось закрыть приемку."""
    # Подготовка данных
    reception_id = uuid.uuid4()
    pvz_id = uuid.uuid4()
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    
    # Мок для получения активной приемки и неудачного закрытия
    mock_cursor.fetchone.side_effect = [
        {
            "id": reception_id,
            "date_time": datetime.now(timezone.utc),
            "pvz_id": pvz_id,
            "status": "in_progress"
        },
        None  # Не удалось закрыть приемку
    ]
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.reception.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await close_reception(pvz_id)
    
    assert exc_info.value.status_code == 400
    assert "Failed to close reception" in exc_info.value.detail