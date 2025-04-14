import pytest
from unittest.mock import patch, AsyncMock
import uuid
from datetime import datetime, timezone

from app.api.reception import create_reception_endpoint
from app.models.reception import ReceptionCreate, Reception

@pytest.mark.asyncio
async def test_create_reception_endpoint():
    """Тестирует API endpoint для создания приемки."""
    # Подготовка данных
    pvz_id = uuid.uuid4()
    reception_id = uuid.uuid4()
    reception_data = ReceptionCreate(pvz_id=pvz_id)
    
    expected_reception = Reception(
        id=reception_id,
        pvz_id=pvz_id,
        date_time=datetime.now(timezone.utc),
        status="in_progress"
    )
    
    # Мокируем сервисную функцию
    with patch("app.api.reception.create_reception", new_callable=AsyncMock) as mock_create_reception:
        mock_create_reception.return_value = expected_reception
        
        # Вызов тестируемой функции
        result = await create_reception_endpoint(reception=reception_data, current_user={"role": "employee"})
    
    # Проверка результатов
    assert result == expected_reception
    mock_create_reception.assert_called_once_with(reception_data)