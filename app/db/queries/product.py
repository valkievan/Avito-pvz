from uuid import UUID


def create_product_query(product_type: str, reception_id: UUID) -> tuple:
    query = """
    INSERT INTO products (type, reception_id, sequence_number)
    VALUES (%s, %s, (
        SELECT COALESCE(MAX(sequence_number), 0) + 1
        FROM products
        WHERE reception_id = %s
    ))
    RETURNING id, date_time, type, reception_id
    """
    params = (product_type, str(reception_id), str(reception_id))
    return query, params


def get_product_query(product_id: UUID) -> tuple:
    query = """
    SELECT id, date_time, type, reception_id
    FROM products
    WHERE id = %s
    """
    params = (str(product_id),)
    return query, params


def get_products_for_reception_query(reception_id: UUID) -> tuple:
    query = """
    SELECT id, date_time, type, reception_id, sequence_number
    FROM products
    WHERE reception_id = %s
    ORDER BY sequence_number ASC
    """
    params = (str(reception_id),)
    return query, params


def get_last_product_in_reception_query(reception_id: UUID) -> tuple:
    query = """
    SELECT id, date_time, type, reception_id, sequence_number
    FROM products
    WHERE reception_id = %s
    ORDER BY sequence_number DESC
    LIMIT 1
    """
    params = (str(reception_id),)
    return query, params


def delete_product_query(product_id: UUID) -> tuple:
    query = """
    DELETE FROM products
    WHERE id = %s
    RETURNING id
    """
    params = (str(product_id),)
    return query, params
