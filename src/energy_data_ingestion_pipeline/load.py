import psycopg

INSERT_RAW_PROJECT = """
    INSERT INTO l0.raw_projects (
        project_id, project_name, project_type, region, status, commissioning_date,
        capacity_mwp, capacity_mw, turbine_count, power_mw, energy_mwh, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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


def load_raw_projects(conn: psycopg.Connection, records: list[dict]) -> int:
    rows = []
    for record in records:
        rows.append(record_to_row(record))

    with conn.cursor() as cur:
        cur.execute("TRUNCATE l0.raw_projects")
        cur.executemany(INSERT_RAW_PROJECT, rows)
    return len(rows)
