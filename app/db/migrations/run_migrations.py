import logging
import os

import psycopg2

from app.config import settings

logger = logging.getLogger(__name__)


def run_migrations():
    logger.info("Starting database migrations")
    conn = None
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
        )

        with conn.cursor() as cursor:
            migration_path = os.path.join(os.path.dirname(__file__), "init_db.sql")
            with open(migration_path) as f:
                migration_sql = f.read()
                cursor.execute(migration_sql)

        conn.commit()
        logger.info("Database migrations completed successfully")
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database migration failed: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
