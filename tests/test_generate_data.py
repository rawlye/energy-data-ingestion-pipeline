from datetime import date

from energy_data_ingestion_pipeline.generate_data import is_producing


def test_not_producing_before_commissioning() -> None:
    project = {"commissioning_date": date(2026, 3, 15)}
    assert is_producing(project, date(2026, 3, 1)) is False


def test_producing_after_commissioning() -> None:
    project = {"commissioning_date": date(2026, 3, 15)}
    assert is_producing(project, date(2026, 4, 1)) is True


def test_producing_from_the_commissioning_day() -> None:
    project = {"commissioning_date": date(2026, 4, 1)}
    assert is_producing(project, date(2026, 4, 1)) is True
