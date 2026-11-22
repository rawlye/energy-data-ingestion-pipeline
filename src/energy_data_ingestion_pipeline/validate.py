from datetime import date

from energy_data_ingestion_pipeline.schema import (
    ALLOWED_STATUSES,
    CAPACITY_FIELDS,
)


def check_project_id_present(record: dict) -> str | None:
    value = record.get("project_id")
    if value is None or value == "":
        return "project_id is missing"
    return None


def check_status_allowed(record: dict) -> str | None:
    status = record.get("status")
    if status not in ALLOWED_STATUSES:
        return f"status {status} is not allowed"
    return None


def check_project_type(record: dict) -> str | None:
    project_type = record.get("project_type")
    if project_type is None:
        return "project_type is missing"
    elif project_type not in CAPACITY_FIELDS:
        return f"project_type is invalid: {project_type}"
    else:
        return None


def check_capacity_positive(record: dict) -> str | None:
    if record.get("project_type") not in CAPACITY_FIELDS:
        return None

    correct_capacity = CAPACITY_FIELDS[record["project_type"]]
    capacity_value = record.get(correct_capacity)

    if capacity_value is None:
        return f"{correct_capacity} is missing"
    elif not isinstance(capacity_value, (int, float)):
        return f"{correct_capacity} is not a number"
    elif capacity_value <= 0:
        return f"{correct_capacity} must be > 0, got {capacity_value}"
    else:
        return None


def check_cod_valid(record: dict) -> str | None:
    cod = record.get("commissioning_date")

    if cod is None:
        return "commissioning_date is missing"
    elif not isinstance(cod, date):
        return f"commissioning_date is not a date: {cod}"
    elif not 2000 <= cod.year <= 2050:
        return f"commissioning_date outside the sanity year range 2000-2050: {cod.year}"
    else:
        return None


def check_plan_month_valid(record: dict) -> str | None:
    month = record.get("month")

    if month is None or month == "":
        return "month is missing"
    elif not isinstance(month, date):
        return f"month is not a date: {month}"
    elif month.day != 1:
        return f"month is not the 1st day of the month: {month}"
    else:
        return None


def check_planned_energy_mwh(record: dict) -> str | None:
    planned_energy = record.get("planned_energy_mwh")

    if planned_energy is None or planned_energy == "":
        return "planned_energy_mwh is missing"
    elif not isinstance(planned_energy, (int, float)):
        return f"planned_energy_mwh is not a number: {planned_energy}"
    elif planned_energy < 0:
        return f"planned_energy_mwh is negative number: {planned_energy}"
    else:
        return None


def check_forecast_version(record: dict) -> str | None:
    forecast_version = record.get("forecast_version")

    if forecast_version is None or forecast_version == "":
        return "forecast_version is missing"
    elif not isinstance(forecast_version, int):
        return f"forecast_version is invalid format: {forecast_version}"
    elif forecast_version < 1:
        return f"forecast_version can't be negative or 0: {forecast_version}"
    else:
        return None


PROJECT_RULES = [
    check_project_id_present,
    check_status_allowed,
    check_project_type,
    check_capacity_positive,
    check_cod_valid,
]

PLAN_RULES = [
    check_project_id_present,
    check_plan_month_valid,
    check_planned_energy_mwh,
    check_forecast_version,
]


def validate_record(record: dict, rules: list) -> list[str]:
    errors_list = []

    for rule in rules:
        validation_result = rule(record)
        if validation_result is not None:
            errors_list.append(validation_result)
    return errors_list


def validate_records(records: list[dict], rules: list) -> tuple[list[dict], list[dict]]:
    valid_rows = []
    invalid_rows = []

    for record in records:
        validation_result = validate_record(record, rules)

        if validation_result != []:
            rejected_record = record.copy()
            rejected_record["reject_reason"] = validation_result
            invalid_rows.append(rejected_record)
        else:
            valid_rows.append(record)
    return valid_rows, invalid_rows


def check_plans_against_projects(
    plans: list[dict],
    valid_projects: list[dict],
    rejected_projects: list[dict],
) -> tuple[list[dict], list[dict]]:

    valid_ids = set()
    rejected_projects_ids = set()

    kept_plans = []
    set_aside_plans = []

    for project in valid_projects:
        valid_ids.add(project["project_id"])

    for rejected_project in rejected_projects:
        rejected_projects_ids.add(rejected_project["project_id"])

    for plan in plans:
        if plan["project_id"] in valid_ids:
            kept_plans.append(plan)
        elif plan["project_id"] in rejected_projects_ids:
            rejected_plan = plan.copy()
            rejected_plan["reject_reason"] = [
                f"project_id is in rejected project rows: {rejected_plan['project_id']}"
            ]
            set_aside_plans.append(rejected_plan)
        else:
            non_exist_plan = plan.copy()
            non_exist_plan["reject_reason"] = [
                (
                    "project_id doesn't exist "
                    f"in project rows: {non_exist_plan['project_id']}"
                )
            ]
            set_aside_plans.append(non_exist_plan)

    return kept_plans, set_aside_plans


if __name__ == "__main__":
    validation_rows = [
        {"project_id": "SOL-001", "status": "operational"},
        {"project_id": "", "status": "Operational"},
        {"project_id": "SOL-001", "status": "Operational"},
        {"project_type": "Solar", "capacity_mwp": 12.5},
        {"project_type": "Wind", "capacity_mw": -5},
        {"project_type": "Solar"},
    ]

    valid_rows, invalid_rows = validate_records(validation_rows, PROJECT_RULES)

    print(invalid_rows[0])
