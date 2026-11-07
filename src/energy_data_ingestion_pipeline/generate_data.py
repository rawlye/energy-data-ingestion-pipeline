import random
from pathlib import Path

from openpyxl import Workbook

PLACES = [
    "Brno",
    "Praha",
    "Hodonin",
    "Morava",
    "Ostrava",
    "Karvina",
    "Pardubice",
    "HK",
    "Znojmo",
]
REGIONS = ["North", "South", "East", "West"]
STATUSES = ["planned", "under construction", "operational"]
BESS_DURATION_HOURS = [1, 2, 4]


def build_base_project(number: int, id_prefix: str, name_prefix: str) -> dict:
    project = {
        "project_id": f"{id_prefix}-{number:03d}",
        "project_name": f"{name_prefix} {random.choice(PLACES)}",
        "region": random.choice(REGIONS),
        "status": random.choice(STATUSES),
    }

    return project


def generate_solar_projects(count: int) -> list[dict]:
    solar_projects = []

    for i in range(count):
        project = build_base_project(i + 1, "SOL", "Solar Park")
        project["capacity_mwp"] = round(random.uniform(1, 50), 2)
        solar_projects.append(project)
    return solar_projects


def generate_wind_projects(count: int) -> list[dict]:
    wind_projects = []

    for i in range(count):
        project = build_base_project(i + 1, "WND", "Wind Park")
        project["capacity_mw"] = round(random.uniform(5, 150), 2)
        project["turbine_count"] = random.randint(2, 25)
        wind_projects.append(project)
    return wind_projects


def generate_bess_projects(count: int) -> list[dict]:
    bess_projects = []

    for i in range(count):
        random_power_mw = round(random.uniform(5, 100), 2)
        project = build_base_project(i + 1, "BES", "BESS")
        project["power_mw"] = random_power_mw
        project["energy_mwh"] = round(
            random_power_mw * random.choice(BESS_DURATION_HOURS), 2
        )
        bess_projects.append(project)
    return bess_projects


def write_sheet(workbook: Workbook, title: str, projects: list[dict]) -> None:
    sheet = workbook.create_sheet(title)
    headers = list(projects[0].keys())
    sheet.append(headers)
    for project in projects:
        sheet.append(list(project.values()))


if __name__ == "__main__":
    random.seed(42)
    output_dir = Path(__file__).parents[2] / "data" / "incoming"
    output_dir.mkdir(parents=True, exist_ok=True)

    solar_projects = generate_solar_projects(5)
    wind_projects = generate_wind_projects(5)
    bess_projects = generate_bess_projects(5)

    workbook = Workbook()
    workbook.remove(workbook["Sheet"])

    write_sheet(workbook, "Solar", solar_projects)
    write_sheet(workbook, "Wind", wind_projects)
    write_sheet(workbook, "BESS", bess_projects)

    workbook.save(output_dir / "projects.xlsx")
