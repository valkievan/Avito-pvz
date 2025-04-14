import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.models.product import ProductCreate, Product
from app.services.product import create_product, get_product, get_products_for_reception, delete_last_product

@pytest.mark.asyncio
async def test_create_product():
    """Тестирует создание нового товара."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    product_id = uuid.uuid4()
    product_type = "электроника"
    
    product_data = ProductCreate(type=product_type, pvz_id=pvz_id)
    
    # Создаем мок для вызова get_active_reception
    with patch("app.services.product.get_active_reception") as mock_get_active_reception:
        # Создаем мок результата get_active_reception
        mock_reception = MagicMock()
        mock_reception.id = reception_id
        mock_get_active_reception.return_value = mock_reception
        
        # Создаем мок для cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": product_id,
            "date_time": "2023-01-01T00:00:00",
            "type": product_type,
            "reception_id": reception_id
        }
        
        # Создаем мок для контекстного менеджера get_db_cursor
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        
        # Патчим get_db_cursor
        with patch("app.services.product.get_db_cursor", return_value=mock_context):
            # Вызов тестируемой функции
            result = await create_product(product_data)
    
    # Проверка результатов
    assert isinstance(result, Product)
    assert result.id == product_id
    assert result.type == product_type
    assert result.reception_id == reception_id

@pytest.mark.asyncio
async def test_create_product_invalid_type():
    """Тестирует создание товара с неверным типом."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    
    # Вместо создания модели с неверным типом, будем патчить проверку типа
    with patch("app.models.product.ProductBase.model_validate", return_value=ProductCreate(type="электроника", pvz_id=pvz_id)):
        # Создаем объект с неверным типом напрямую для передачи в функцию
        product_data = MagicMock()
        product_data.type = "неверный_тип"
        product_data.pvz_id = pvz_id
        
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await create_product(product_data)
    
    assert exc_info.value.status_code == 400
    assert "Product type must be one of" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_product():
    """Тестирует получение товара по ID."""
    # Подготовка данных
    product_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    product_type = "электроника"
    
    # Создаем мок для cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": product_id,
        "date_time": "2023-01-01T00:00:00",
        "type": product_type,
        "reception_id": reception_id
    }
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.product.get_db_cursor", return_value=mock_context):
        # Вызов тестируемой функции
        result = await get_product(product_id)
    
    # Проверка результатов
    assert isinstance(result, Product)
    assert result.id == product_id
    assert result.type == product_type
    assert result.reception_id == reception_id

@pytest.mark.asyncio
async def test_get_product_not_found():
    """Тестирует получение несуществующего товара."""
    # Подготовка данных
    product_id = uuid.uuid4()
    
    # Создаем мок для cursor, который возвращает None (товар не найден)
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    
    # Создаем мок для контекстного менеджера get_db_cursor
    mock_context = MagicMock()
    mock_context.__enter__.return_value = mock_cursor
    
    # Патчим get_db_cursor
    with patch("app.services.product.get_db_cursor", return_value=mock_context):
        # Проверка исключения
        with pytest.raises(HTTPException) as exc_info:
            await get_product(product_id)
    
    assert exc_info.value.status_code == 404
    assert "Product not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_get_products_for_reception():
    """Тестирует получение списка товаров для приемки."""
    # Подготовка данных
    reception_id = uuid.uuid4()
    product1_id = uuid.uuid4()
    product2_id = uuid.uuid4()
    
    # Создаем мок для get_reception (проверка существования приемки)
    with patch("app.services.product.get_reception") as mock_get_reception:
        mock_get_reception.return_value = MagicMock()  # Не важно что возвращает, главное не вызывать ошибку
        
        # Создаем мок для cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            {
                "id": product1_id,
                "date_time": "2023-01-01T00:00:00",
                "type": "электроника",
                "reception_id": reception_id,
                "sequence_number": 1
            },
            {
                "id": product2_id,
                "date_time": "2023-01-01T00:00:00",
                "type": "одежда",
                "reception_id": reception_id,
                "sequence_number": 2
            }
        ]
        
        # Создаем мок для контекстного менеджера get_db_cursor
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        
        # Патчим get_db_cursor
        with patch("app.services.product.get_db_cursor", return_value=mock_context):
            # Вызов тестируемой функции
            results = await get_products_for_reception(reception_id)
    
    # Проверка результатов
    assert len(results) == 2
    assert all(isinstance(result, Product) for result in results)
    assert results[0].id == product1_id
    assert results[0].type == "электроника"
    assert results[1].id == product2_id
    assert results[1].type == "одежда"

@pytest.mark.asyncio
async def test_delete_last_product():
    """Тестирует удаление последнего добавленного товара."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    product_id = uuid.uuid4()
    
    # Создаем мок для вызова get_active_reception
    with patch("app.services.product.get_active_reception") as mock_get_active_reception:
        # Создаем мок результата get_active_reception
        mock_reception = MagicMock()
        mock_reception.id = reception_id
        mock_get_active_reception.return_value = mock_reception
        
        # Создаем мок для cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [
            # Ответ для get_last_product_in_reception_query
            {
                "id": product_id,
                "date_time": "2023-01-01T00:00:00",
                "type": "электроника",
                "reception_id": reception_id,
                "sequence_number": 1
            },
            # Ответ для delete_product_query
            {
                "id": product_id
            }
        ]
        
        # Создаем мок для контекстного менеджера get_db_cursor
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        
        # Патчим get_db_cursor
        with patch("app.services.product.get_db_cursor", return_value=mock_context):
            # Вызов тестируемой функции
            await delete_last_product(pvz_id)
    
    # Проверка выполнения SQL-запросов
    assert mock_cursor.execute.call_count == 2  # Два SQL запроса: получение последнего товара и его удаление

@pytest.mark.asyncio
async def test_delete_last_product_no_products():
    """Тестирует удаление последнего товара, когда товаров нет."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    
    # Создаем мок для вызова get_active_reception
    with patch("app.services.product.get_active_reception") as mock_get_active_reception:
        # Создаем мок результата get_active_reception
        mock_reception = MagicMock()
        mock_reception.id = reception_id
        mock_get_active_reception.return_value = mock_reception
        
        # Создаем мок для cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # Нет товаров
        
        # Создаем мок для контекстного менеджера get_db_cursor
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_cursor
        
        # Патчим get_db_cursor
        with patch("app.services.product.get_db_cursor", return_value=mock_context):
            # Проверка исключения
            with pytest.raises(HTTPException) as exc_info:
                await delete_last_product(pvz_id)
    
    assert exc_info.value.status_code == 400
    assert "No products found in the active reception" in exc_info.value.detail