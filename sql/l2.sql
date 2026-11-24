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

CREATE TABLE l2.fact_production_plan (
    project_key INTEGER NOT NULL REFERENCES l2.dim_project (project_key),
    date_key INTEGER NOT NULL REFERENCES l2.dim_date (date_key),
    forecast_version INT NOT NULL,
    planned_energy_mwh NUMERIC(12, 2) NOT NULL,
    PRIMARY KEY (project_key, date_key, forecast_version)
);
