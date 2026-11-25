from typing import LiteralString

from psycopg import Connection, sql

INSERT_L0_RAW_PROJECT = """
    INSERT INTO l0.raw_projects (
        project_id, project_name, project_type, region, status, commissioning_date,
        capacity_mwp, capacity_mw, turbine_count, power_mw, energy_mwh, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

INSERT_L0_PRODUCTION_PLAN = """
    INSERT INTO l0.raw_production_plan (
        project_id, month, planned_energy_mwh, forecast_version, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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

INSERT_L1_PLANS = """
    INSERT INTO l1.plans (
        project_id, month, planned_energy_mwh, forecast_version, source_file,
        source_sheet, source_row
    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

INSERT_L1_QUARANTINE_PLANS = """
    INSERT INTO l1.quarantine_plans (
        project_id, month, planned_energy_mwh, forecast_version, source_file,
        source_sheet, source_row, reject_reason
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
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


def record_to_row(
    record: dict, columns: list[str], as_text: bool, with_reason: bool
) -> tuple:
    values = []
    for column in columns:
        row_value = record.get(column)
        if as_text:
            row_value = to_text(row_value)
        values.append(row_value)
    values.append(record["source_file"])
    values.append(record["source_sheet"])
    values.append(record["source_row"])
    if with_reason:
        values.append("; ".join(record["reject_reason"]))
    return tuple(values)


def load_to_layer(
    conn: Connection,
    records: list[dict],
    insert_statement: LiteralString,
    schema_name: str,
    table_name: str,
    as_text: bool,
    with_reason: bool,
    columns: list[str],
) -> int:
    rows = []
    for record in records:
        rows.append(record_to_row(record, columns, as_text, with_reason))
    with conn.cursor() as cur:
        cur.execute(
            sql.SQL("TRUNCATE {};").format(sql.Identifier(schema_name, table_name))
        )
        cur.executemany(insert_statement, rows)
    return len(rows)
