CREATE SCHEMA l0;

CREATE TABLE l0.raw_projects (
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
    loaded_at TIMESTAMPTZ DEFAULT now()
);
