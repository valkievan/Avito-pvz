-- Создаем расширение для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('employee', 'moderator')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица ПВЗ (Пунктов выдачи заказов)
CREATE TABLE IF NOT EXISTS pvz (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    city VARCHAR(50) NOT NULL CHECK (city IN ('Москва', 'Санкт-Петербург', 'Казань'))
);

-- Таблица приемок
CREATE TABLE IF NOT EXISTS receptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    pvz_id UUID NOT NULL REFERENCES pvz(id),
    status VARCHAR(20) NOT NULL CHECK (status IN ('in_progress', 'close')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблица товаров
CREATE TABLE IF NOT EXISTS products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(50) NOT NULL CHECK (type IN ('электроника', 'одежда', 'обувь')),
    reception_id UUID NOT NULL REFERENCES receptions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    sequence_number INTEGER NOT NULL -- Для реализации LIFO
);

-- Индексы для ускорения запросов
CREATE INDEX IF NOT EXISTS idx_receptions_pvz_id ON receptions(pvz_id);
CREATE INDEX IF NOT EXISTS idx_receptions_status ON receptions(status);
CREATE INDEX IF NOT EXISTS idx_products_reception_id ON products(reception_id);
CREATE INDEX IF NOT EXISTS idx_products_sequence_number ON products(sequence_number);