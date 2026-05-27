"""Inference pipeline: orchestrates model loading and demand-profile prediction."""

import csv
from pathlib import Path

from decarbai_demands.model import load_artifacts
from decarbai_demands.model_cache import ensure_city_models
from decarbai_demands.schema import InputData


def run_pipeline(input_data: InputData) -> dict[str, list[float]]:
    city_dir = ensure_city_models(input_data.country, input_data.city)
    model_base_path = city_dir / input_data.building_type

    profiles = {}
    # NOTE: Electricity and dhw is one model, so we need to merge them here
    model_demand_types = list({i if i not in ["electricity", "dhw"] else "electricity_dhw" for i in input_data.demand_type})

    for t in model_demand_types:
        model = load_artifacts(model_base_path / f"{t}.zst")
        profile = model.predict(input_data.ordered_features)
        if t == "electricity_dhw":
            # NOTE: First 8760 values are dhw, rest is electricity. ORDER MUST BE MAINTAINED
            if "dhw" in input_data.demand_type:
                profiles["dhw"] = profile[:8760].tolist()
            if "electricity" in input_data.demand_type:
                profiles["electricity"] = (profile[8760:17520] + profile[17520:]).tolist()
        else:
            profiles[t] = profile.tolist()

    return profiles


def export_profiles_to_csv(profiles: dict[str, list[float]], filepath: Path) -> None:
    with filepath.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(profiles.keys())
        writer.writerows(zip(*profiles.values(), strict=True))


if __name__ == "__main__":
    input_data = InputData(
        country="ch",
        city="bern",
        building_type="mfh",
        demand_type=["heating", "cooling", "electricity", "dhw"],
        length=11.0,
        width=14.0,
        floor_height=3.5,
        number_of_floors=4,
        construction_year=2014,
        north_angle=90.0,
        nwwr=0.75,
        ewwr=0.15,
        swwr=0.3,
        wwwr=0.3,
        u_ground=0.226751734,
        u_wall=0.152911692,
        u_roof=0.175874125,
        u_window=1.176,
    )
    profiles = run_pipeline(input_data)
    export_profiles_to_csv(profiles, Path("test.csv"))
