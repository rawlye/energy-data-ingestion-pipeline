import psycopg

INSERT_RAW_PROJECT = """
    INSERT INTO l0.raw_projects (
        project_id, project_name, project_type, region, status, commissioning_date,
        capacity_mwp, capacity_mw, turbine_count, power_mw, energy_mwh, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

INSERT_L1_PROJECT = """
    INSERT INTO l1.projects (
        project_id, project_name, project_type, region, status, commissioning_date,
        capacity_mwp, capacity_mw, turbine_count, power_mw, energy_mwh, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

INSERT_L1_QUARANTINE = """
    INSERT INTO l1.quarantine_projects (
        project_id, project_name, project_type, region, status, commissioning_date,
        capacity_mwp, capacity_mw, turbine_count, power_mw, energy_mwh, source_file,
        source_sheet, source_row, reject_reason
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

INSERT_L0_PRODUCTION_PLAN = """
    INSERT INTO l0.raw_production_plan (
        project_id, month, planned_energy_mwh, forecast_version, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

DATA_COLUMNS = [
    "project_id",
    "project_name",
    "project_type",
    "region",
    "status",
    "commissioning_date",
    "capacity_mwp",
    "capacity_mw",
    "turbine_count",
    "power_mw",
    "energy_mwh",
]

PLAN_COLUMNS = [
    "project_id",
    "month",
    "planned_energy_mwh",
    "forecast_version",
]


def to_text(value) -> str | None:
    if value is None:
        return None
    return str(value)


def record_to_row(record: dict) -> tuple:
    values = []
    for column in DATA_COLUMNS:
        values.append(to_text(record.get(column)))
    values.append(record["source_file"])
    values.append(record["source_sheet"])
    values.append(record["source_row"])
    return tuple(values)


def record_to_l1_row(record: dict) -> tuple:
    values = []
    for column in DATA_COLUMNS:
        values.append(record.get(column))
    values.append(record["source_file"])
    values.append(record["source_sheet"])
    values.append(record["source_row"])
    return tuple(values)


def record_to_l0_plan_row(record: dict) -> tuple:
    values = []
    for column in PLAN_COLUMNS:
        values.append(to_text(record.get(column)))
    values.append(record["source_file"])
    values.append(record["source_sheet"])
    values.append(record["source_row"])
    return tuple(values)


def record_to_l1_quarantine(record: dict) -> tuple:
    values = []
    for column in DATA_COLUMNS:
        values.append(to_text(record.get(column)))
    values.append(record["source_file"])
    values.append(record["source_sheet"])
    values.append(record["source_row"])
    values.append("; ".join(record["reject_reason"]))
    return tuple(values)


def load_raw_projects(conn: psycopg.Connection, records: list[dict]) -> int:
    rows = []
    for record in records:
        rows.append(record_to_row(record))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE l0.raw_projects")
        cur.executemany(INSERT_RAW_PROJECT, rows)
    return len(rows)


def load_l1_projects(conn: psycopg.Connection, records: list[dict]) -> int:
    rows = []
    for record in records:
        rows.append(record_to_l1_row(record))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE l1.projects")
        cur.executemany(INSERT_L1_PROJECT, rows)
    return len(rows)


def load_l1_quarantine(conn: psycopg.Connection, records: list[dict]) -> int:
    rows = []
    for record in records:
        rows.append(record_to_l1_quarantine(record))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE l1.quarantine_projects")
        cur.executemany(INSERT_L1_QUARANTINE, rows)
    return len(rows)


def load_l0_production_plan(conn: psycopg.Connection, records: list[dict]) -> int:
    rows = []
    for record in records:
        rows.append(record_to_l0_plan_row(record))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE l0.raw_production_plan")
        cur.executemany(INSERT_L0_PRODUCTION_PLAN, rows)
    return len(rows)
