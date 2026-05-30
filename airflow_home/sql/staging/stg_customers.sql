CREATE TABLE IF NOT EXISTS stg_customers (
    customer_id TEXT PRIMARY KEY,
    name TEXT,
    email TEXT,
    country TEXT,
    created_at TIMESTAMP
);

INSERT INTO stg_customers (customer_id, name, email, country, created_at)
SELECT
    customer_id,
    INITCAP(name) AS name,
    LOWER(email) AS email,
    COALESCE(country, 'Nigeria') AS country,
    CAST(created_at AS TIMESTAMP) AS created_at
FROM src_customers
ON CONFLICT (customer_id) DO UPDATE
    SET name = EXCLUDED.name,
        email = EXCLUDED.email,
        country = EXCLUDED.country,
        created_at = EXCLUDED.created_at;
