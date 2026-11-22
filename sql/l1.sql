CREATE SCHEMA l1;

CREATE TABLE l1.projects (
    project_id TEXT PRIMARY KEY,
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
    source_file TEXT,
    source_sheet TEXT,
    source_row INTEGER,
    loaded_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE l1.quarantine_projects (
    project_id TEXT,
    project_name TEXT,
    project_type TEXT,
    region TEXT,
    status TEXT,
    commissioning_date TEXT,
    capacity_mwp TEXT,
    capacity_mw TEXT,
    turbine_count TEXT,
    power_mw TEXT,
    energy_mwh TEXT,
    source_file TEXT,
    source_sheet TEXT,
    source_row INTEGER,
    reject_reason TEXT NOT NULL, -- all data can be null, only reject_reason cannot
    quarantined_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE l1.plans (
    project_id TEXT,
    month DATE,
    planned_energy_mwh NUMERIC NOT NULL,
    forecast_version INTEGER,
    source_file TEXT,
    source_sheet TEXT,
    source_row INTEGER,
    loaded_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (project_id, month, forecast_version)
);

CREATE TABLE l1.quarantine_plans (
    project_id TEXT,
    month TEXT,
    planned_energy_mwh TEXT,
    forecast_version TEXT,
    source_file TEXT,
    source_sheet TEXT,
    source_row INTEGER,
    reject_reason TEXT NOT NULL, -- all data can be null, only reject_reason cannot
    quarantined_at TIMESTAMPTZ DEFAULT now()
);
