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
    loaded_at TIMESTAMPTZ DEFAULT now();
