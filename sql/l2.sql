CREATE SCHEMA l2;

CREATE TABLE l2.dim_project (
    project_key INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    project_id TEXT NOT NULL, -- business key from the source
    project_name TEXT NOT NULL,
    project_type TEXT NOT NULL,
    region TEXT,
    status TEXT NOT NULL,
    commissioning_date DATE NOT NULL,
    capacity_mwp NUMERIC(12, 2),
    capacity_mw NUMERIC(12, 2),
    turbine_count INTEGER,
    power_mw NUMERIC(12, 2),
    energy_mwh NUMERIC(12, 2),
    installed_capacity_mw NUMERIC(12, 2) NOT NULL
);

CREATE TABLE l2.dim_date (
    date_key INTEGER PRIMARY KEY,
    month_start DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    hours_in_month INTEGER NOT NULL
);

WITH months AS (
    SELECT generate_series(DATE '2020-01-01', DATE '2035-12-01', INTERVAL '1 month')::date
        AS month_start
)
SELECT
    EXTRACT(YEAR FROM month_start) * 100 + EXTRACT(MONTH FROM month_start)::int AS date_key,
    month_start,
    EXTRACT(YEAR FROM month_start)::int AS year,
    CASE WHEN EXTRACT(MONTH FROM month_start) IN (1, 2, 3)
            THEN 1
        WHEN EXTRACT(MONTH FROM month_start) IN (4, 5, 6)
            THEN 2
        WHEN EXTRACT(MONTH FROM month_start) IN (7, 8, 9)
            THEN 3
        WHEN EXTRACT(MONTH FROM month_start) IN (10, 11, 12)
            THEN 4 END AS quarter,
    EXTRACT(MONTH FROM month_start) AS month,
    TO_CHAR(month_start, 'FMMonth') AS month_name,
    ((month_start + INTERVAL '1 month')::date - month_start) * 24 AS hours_in_month
FROM months;
