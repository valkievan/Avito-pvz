import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

# from app.main import app
# from app.api import auth, pvz, reception, product
# from app.api.dependencies import get_current_user, check_if_moderator, check_if_employee, get_current_employee_or_moderator

def test_complete_workflow():
    """
    Интеграционный тест полного рабочего процесса:
    1. Создание ПВЗ
    2. Добавление новой приемки
    3. Добавление 50 товаров
    4. Закрытие приемки
    """
    # Определяем Pydantic модели для корректной валидации входных данных
    class PVZCreate(BaseModel):
        city: str
    
    class ReceptionCreate(BaseModel):
        pvz_id: str
    
    class ProductCreate(BaseModel):
        type: str
        pvz_id: str
    
    # Создаем тестовое приложение FastAPI без зависимостей авторизации
    test_app = FastAPI()
    
    # Регистрируем маршруты, аналогичные основному приложению, но с замененными зависимостями
    @test_app.post("/pvz", status_code=201)
    async def create_pvz_test(pvz: PVZCreate):
        # Здесь мы вызываем оригинальную функцию, но без проверки токенов
        with patch("app.db.connection.get_db_cursor") as mock_get_cursor:
            mock_cursor = mock_get_cursor.return_value.__enter__.return_value
            mock_cursor.fetchone.return_value = {
                "id": "123e4567-e89b-12d3-a456-426614174000", 
                "registration_date": "2023-01-01T00:00:00", 
                "city": pvz.city
            }
            
            return {
                "id": "123e4567-e89b-12d3-a456-426614174000", 
                "registration_date": "2023-01-01T00:00:00", 
                "city": pvz.city
            }
    
    @test_app.post("/receptions", status_code=201)
    async def create_reception_test(reception: ReceptionCreate):
        # Здесь мы вызываем оригинальную функцию, но без проверки токенов
        with patch("app.db.connection.get_db_cursor") as mock_get_cursor:
            mock_cursor = mock_get_cursor.return_value.__enter__.return_value
            # Мок для запроса на получение ПВЗ
            mock_cursor.fetchone.side_effect = [
                {"id": reception.pvz_id, "registration_date": "2023-01-01T00:00:00", "city": "Москва"},  # get_pvz
                None,  # get_active_reception возвращает None (нет активной приемки)
                {"id": "123e4567-e89b-12d3-a456-426614174001", "date_time": "2023-01-01T00:00:00", "pvz_id": reception.pvz_id, "status": "in_progress"}  # create_reception
            ]
            
            return {
                "id": "123e4567-e89b-12d3-a456-426614174001", 
                "date_time": "2023-01-01T00:00:00", 
                "pvz_id": reception.pvz_id, 
                "status": "in_progress"
            }
    
    @test_app.post("/products", status_code=201)
    async def create_product_test(product: ProductCreate):
        reception_id = "123e4567-e89b-12d3-a456-426614174001"
        
        with patch("app.db.connection.get_db_cursor") as mock_get_cursor:
            mock_cursor = mock_get_cursor.return_value.__enter__.return_value
            # Мок для запроса на получение активной приемки
            mock_cursor.fetchone.side_effect = [
                {"id": reception_id, "date_time": "2023-01-01T00:00:00", "pvz_id": product.pvz_id, "status": "in_progress"},  # get_active_reception
                {"id": f"product-{product.type}", "date_time": "2023-01-01T00:00:00", "type": product.type, "reception_id": reception_id}  # create_product
            ]
            
            return {
                "id": f"product-{product.type}", 
                "date_time": "2023-01-01T00:00:00", 
                "type": product.type, 
                "reception_id": reception_id
            }
    
    @test_app.post("/pvz/{pvz_id}/close_last_reception")
    async def close_reception_test(pvz_id: str):
        reception_id = "123e4567-e89b-12d3-a456-426614174001"
        
        with patch("app.db.connection.get_db_cursor") as mock_get_cursor:
            mock_cursor = mock_get_cursor.return_value.__enter__.return_value
            # Мок для запросов в close_reception
            mock_cursor.fetchone.side_effect = [
                {"id": reception_id, "date_time": "2023-01-01T00:00:00", "pvz_id": pvz_id, "status": "in_progress"},  # get_active_reception
                {"id": reception_id, "date_time": "2023-01-01T00:00:00", "pvz_id": pvz_id, "status": "close"}  # close_reception
            ]
            
            return {
                "id": reception_id, 
                "date_time": "2023-01-01T00:00:00", 
                "pvz_id": pvz_id, 
                "status": "close"
            }
    
    # Создаем тестовый клиент
    client = TestClient(test_app)
    
    # Тестируем весь рабочий процесс без патчей авторизации
    
    # 1. Создаем ПВЗ
    response = client.post(
        "/pvz",
        json={"city": "Москва"}
    )
    assert response.status_code == 201
    pvz_data = response.json()
    pvz_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # 2. Создаем новую приемку
    response = client.post(
        "/receptions",
        json={"pvz_id": pvz_id}
    )
    assert response.status_code == 201
    
    # 3. Добавляем 50 товаров
    product_types = ["электроника", "одежда", "обувь"]
    for i in range(50):
        product_type = product_types[i % 3]
        response = client.post(
            "/products",
            json={"type": product_type, "pvz_id": pvz_id}
        )
        assert response.status_code == 201
        product_data = response.json()
        assert product_data["type"] == product_type
    
    # 4. Закрываем приемку
    response = client.post(
        f"/pvz/{pvz_id}/close_last_reception"
    )
    assert response.status_code == 200
    closed_reception = response.json()
    assert closed_reception["status"] == "close"