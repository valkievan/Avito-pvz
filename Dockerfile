FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
COPY reqs.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r reqs.txt

# Копирование кода приложения
COPY . .

# Установка переменных окружения
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Выполнение миграций и запуск приложения
CMD ["sh", "-c", "python -m app.db.migrations.run_migrations && python -m app.main"]