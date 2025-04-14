import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import settings

logger = logging.getLogger(__name__)


def get_db_connection():
    try:
        return psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname=settings.POSTGRES_DB,
            cursor_factory=RealDictCursor,
        )
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise


@contextmanager
def get_db_cursor():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        conn.close()
