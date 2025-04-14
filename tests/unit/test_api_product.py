import pytest
from unittest.mock import patch, AsyncMock
import uuid

from app.api.product import create_product_endpoint
from app.models.product import ProductCreate, Product

@pytest.mark.asyncio
async def test_create_product_endpoint():
    """Тестирует API endpoint для создания товара."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    product_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    product_data = ProductCreate(type="электроника", pvz_id=pvz_id)
    
    expected_product = Product(
        id=product_id,
        type="электроника",
        date_time="2023-01-01T00:00:00",
        reception_id=reception_id
    )
    
    # Мокируем сервисную функцию
    with patch("app.api.product.create_product", new_callable=AsyncMock) as mock_create_product:
        mock_create_product.return_value = expected_product
        
        # Вызов тестируемой функции
        result = await create_product_endpoint(product=product_data, current_user={"role": "employee"})
    
    # Проверка результатов
    assert result == expected_product
    mock_create_product.assert_called_once_with(product_data)