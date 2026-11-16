from energy_data_ingestion_pipeline.clean import clean_records


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
