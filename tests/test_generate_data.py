from datetime import date

from energy_data_ingestion_pipeline.generate_data import (
    hours_in_month,
    inject_defects,
    is_producing,
)


def test_not_producing_before_commissioning() -> None:
    project = {"commissioning_date": date(2026, 3, 15)}
    assert is_producing(project, date(2026, 3, 1)) is False


def test_producing_after_commissioning() -> None:
    project = {"commissioning_date": date(2026, 3, 15)}
    assert is_producing(project, date(2026, 4, 1)) is True


def test_producing_from_the_commissioning_day() -> None:
    project = {"commissioning_date": date(2026, 4, 1)}
    assert is_producing(project, date(2026, 4, 1)) is True


def test_hours_in_month_2026_feb() -> None:
    assert hours_in_month(date(2026, 2, 1)) == 672


def test_hours_in_month_march_2026() -> None:
    assert hours_in_month(date(2026, 3, 1)) == 744


def test_hours_in_month_feb_2028() -> None:
    assert hours_in_month(date(2028, 2, 1)) == 696


def test_defect_projects_gets_wrong_status() -> None:
    records = [
        {"project_id": "SOL-002", "status": "operational"},
    ]

    modified_records = inject_defects(records)

    assert modified_records[0]["status"] == "Operational"
    assert records[0]["status"] == "operational"
