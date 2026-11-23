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


def build_dim_project(conn: psycopg.Connection) -> int:
    with conn.cursor() as cur:
        cur.execute("TRUNCATE l2.dim_project RESTART IDENTITY;")
        cur.execute(INSERT_L2_DIM_PROJECT)
        return cur.rowcount
