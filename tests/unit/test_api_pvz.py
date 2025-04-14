import pytest
from unittest.mock import patch, AsyncMock
import uuid
from datetime import datetime, timezone

from app.api.pvz import (
    create_pvz_endpoint, 
    get_pvzs_endpoint, 
    close_reception_endpoint, 
    delete_last_product_endpoint
)
from app.models.pvz import PVZCreate, PVZ

@pytest.mark.asyncio
async def test_create_pvz_endpoint():
    """Тестирует API endpoint для создания ПВЗ."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    pvz_data = PVZCreate(city="Москва")
    
    expected_pvz = PVZ(
        id=pvz_id,
        city="Москва",
        registration_date=datetime.now(timezone.utc)
    )
    
    # Мокируем сервисную функцию
    with patch("app.api.pvz.create_pvz", new_callable=AsyncMock) as mock_create_pvz:
        mock_create_pvz.return_value = expected_pvz
        
        # Вызов тестируемой функции
        result = await create_pvz_endpoint(pvz=pvz_data, current_user={"role": "moderator"})
    
    # Проверка результатов
    assert result == expected_pvz
    mock_create_pvz.assert_called_once_with(pvz_data)

@pytest.mark.asyncio
async def test_get_pvzs_endpoint():
    """Тестирует API endpoint для получения списка ПВЗ."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    expected_result = {
        "total": 1,
        "page": 1,
        "limit": 10,
        "items": [
            {
                "pvz": {
                    "id": pvz_id,
                    "city": "Москва",
                    "registration_date": datetime.now(timezone.utc)
                },
                "receptions": []
            }
        ]
    }
    
    # Мокируем сервисную функцию
    with patch("app.api.pvz.get_pvzs_with_pagination_and_filtering", new_callable=AsyncMock) as mock_get_pvzs:
        mock_get_pvzs.return_value = expected_result
        
        # Вызов тестируемой функции
        result = await get_pvzs_endpoint(
            page=1, 
            limit=10, 
            start_date=None, 
            end_date=None, 
            current_user={"role": "employee"}
        )
    
    # Проверка результатов
    assert result == expected_result
    mock_get_pvzs.assert_called_once_with(1, 10, None, None)

@pytest.mark.asyncio
async def test_close_reception_endpoint():
    """Тестирует API endpoint для закрытия приемки."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    
    expected_reception = {
        "id": reception_id,
        "date_time": datetime.now(timezone.utc),
        "pvz_id": pvz_id,
        "status": "close"
    }
    
    # Мокируем сервисную функцию
    with patch("app.api.pvz.close_reception", new_callable=AsyncMock) as mock_close_reception:
        mock_close_reception.return_value = expected_reception
        
        # Вызов тестируемой функции
        result = await close_reception_endpoint(
            pvz_id=pvz_id, 
            current_user={"role": "employee"}
        )
    
    # Проверка результатов
    assert result == expected_reception
    mock_close_reception.assert_called_once_with(pvz_id)

@pytest.mark.asyncio
async def test_delete_last_product_endpoint():
    """Тестирует API endpoint для удаления последнего товара."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    
    # Мокируем сервисную функцию
    with patch("app.api.pvz.delete_last_product", new_callable=AsyncMock) as mock_delete_last_product:
        # Вызов тестируемой функции
        result = await delete_last_product_endpoint(
            pvz_id=pvz_id, 
            current_user={"role": "employee"}
        )
    
    # Проверка результатов
    assert result == {"message": "Product successfully deleted"}
    mock_delete_last_product.assert_called_once_with(pvz_id)