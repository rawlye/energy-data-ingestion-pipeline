import psycopg

INSERT_L2_DIM_PROJECT = """
INSERT INTO l2.dim_project (
    project_id,
    project_name,
    project_type,
    region,
    status,
    commissioning_date,
    capacity_mwp,
    capacity_mw,
    turbine_count,
    power_mw,
    energy_mwh,
    installed_capacity_mw
)

SELECT
    project_id,
    project_name,
    project_type,
    region,
    status,
    commissioning_date,
    capacity_mwp,
    capacity_mw,
    turbine_count,
    power_mw,
    energy_mwh,
    CASE
        WHEN project_type = 'Solar'
            THEN capacity_mwp
        WHEN project_type in ('Wind', 'Hydro')
            THEN capacity_mw
        WHEN project_type = 'BESS'
            THEN power_mw END AS installed_capacity_mw
FROM l1.projects
ORDER BY project_id;
"""

INSERT_L2_DIM_DATE = """
INSERT INTO l2.dim_date (
    date_key,
    month_start,
    year,
    quarter,
    month,
    month_name,
    hours_in_month
)

WITH months AS (
    SELECT generate_series(DATE '2020-01-01', DATE '2035-12-01',
    INTERVAL '1 month')::date
        AS month_start
)
SELECT
    (EXTRACT(YEAR FROM month_start) * 100 + EXTRACT(MONTH FROM month_start))::int
    AS date_key,
    month_start,
    (EXTRACT(YEAR FROM month_start))::int AS year,
    CASE WHEN EXTRACT(MONTH FROM month_start) IN (1, 2, 3)
            THEN 1
        WHEN EXTRACT(MONTH FROM month_start) IN (4, 5, 6)
            THEN 2
        WHEN EXTRACT(MONTH FROM month_start) IN (7, 8, 9)
            THEN 3
        WHEN EXTRACT(MONTH FROM month_start) IN (10, 11, 12)
            THEN 4 END AS quarter,
    (EXTRACT(MONTH FROM month_start))::int AS month,
    TO_CHAR(month_start, 'FMMonth') AS month_name,
    ((month_start + INTERVAL '1 month')::date - month_start) * 24 AS hours_in_month
FROM months;
"""


def build_dim_project(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE l2.dim_project RESTART IDENTITY;")
        cur.execute(INSERT_L2_DIM_PROJECT)
        return cur.rowcount


def build_dim_date(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE l2.dim_date;")
        cur.execute(INSERT_L2_DIM_DATE)
        return cur.rowcount
