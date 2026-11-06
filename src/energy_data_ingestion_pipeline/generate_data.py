import random

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


def generate_solar_projects(count: int) -> list[dict]:
    projects = []

    for i in range(count):
        project = {
            "project_id": f"SOL-{i + 1:03d}",
            "project_name": f"Solar Park {random.choice(PLACES)}",
            "region": random.choice(REGIONS),
            "status": random.choice(STATUSES),
            "capacity_mwp": round(random.uniform(1, 50), 1),
        }
        projects.append(project)
    return projects


if __name__ == "__main__":
    random.seed(42)
    result = generate_solar_projects(5)
    print(result)
