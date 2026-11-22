from datetime import date, datetime

from energy_data_ingestion_pipeline.load import (
    record_to_l0_row,
    record_to_l1_plan_quarantine_row,
    to_text,
)


def test_to_text_converts_to_str() -> None:
    datum = date(2020, 2, 2)

    assert to_text(7) == "7"
    assert to_text(datum) == "2020-02-02"
    assert to_text(None) is None


def test_record_to_row_keeps_column_order() -> None:
    record = {
        "project_id": "SOL-001",
        "status": "operational",
        "capacity_mwp": 13,
        "source_file": "projects.xlsx",
        "source_sheet": "Solar",
        "source_row": 2,
    }

    expected = (
        "SOL-001",  # 1 project_id
        None,  # 2 project_name (missing -> None)
        None,  # 3 project_type
        None,  # 4 region
        "operational",  # 5 status
        None,  # 6 commisioning_date
        "13",  # 7 capacity_mwp - gets converted to string
        None,  # 8 capacity_mw
        None,  # 9 turbine_count
        None,  # 10 power_mw
        None,  # 11 energy_mwh
        "projects.xlsx",  # 12 source_file
        "Solar",  # 13 source_sheet
        2,  # 14 source_row - stays as integer
    )

    assert record_to_l0_row(record) == expected


def test_record_to_l1_plan_quarantine_row_keeps_column_order() -> None:
    record = {
        "project_id": "WND-003",
        "month": datetime(2026, 3, 1, 0, 0),
        "planned_energy_mwh": -50.5,
        "forecast_version": 1,
        "source_file": "production_plan_2026_03.xlsx",
        "source_sheet": "Plan",
        "source_row": 4,
        "reject_reason": [
            "planned_energy_mwh is negative number: -50.5",
            "project_id belongs to a rejected project",
        ],
    }

    expected = (
        "WND-003",
        "2026-03-01 00:00:00",
        "-50.5",
        "1",
        "production_plan_2026_03.xlsx",
        "Plan",
        4,
        (
            "planned_energy_mwh is negative number: -50.5; "
            "project_id belongs to a rejected project"
        ),
    )

    assert record_to_l1_plan_quarantine_row(record) == expected
