from energy_data_ingestion_pipeline.clean import clean_project_record, clean_records


def test_clean_normalizes_status_and_keeps_input() -> None:
    records = [
        {"project_id": "SOL-002", "status": " Operational "},
        {"project_id": "SOL-003"},
    ]

    assert clean_records(records)[0] == {
        "project_id": "SOL-002",
        "status": "operational",
    }
    assert clean_records(records)[1] == {"project_id": "SOL-003"}
    assert records[0]["status"] == " Operational "


def test_convert_floats_leaving_unconvertable_values() -> None:
    records = [
        {"project_type": "Wind", "capacity_mw": 12.5},
        {"project_type": "Wind", "capacity_mw": "12,5"},
        {"project_type": "Wind", "capacity_mw": "n/a"},
        {"project_type": "Wind"},
    ]

    assert clean_project_record(records[0]) == {
        "project_type": "Wind",
        "capacity_mw": 12.5,
    }
    assert clean_project_record(records[1]) == {
        "project_type": "Wind",
        "capacity_mw": 12.5,
    }
    assert clean_project_record(records[2]) == {
        "project_type": "Wind",
        "capacity_mw": "n/a",
    }
    assert clean_project_record(records[3]) == {"project_type": "Wind"}
