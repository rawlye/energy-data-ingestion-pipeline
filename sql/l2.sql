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
FROM l1.projects;
