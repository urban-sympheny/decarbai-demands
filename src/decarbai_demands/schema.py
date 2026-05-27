"""Pydantic input schema and computed building-geometry properties.

MODEL FEATURE SPECIFICATIONS
----------------------------
The ``ordered_features`` property below defines the exact order of features
required by the inference model. DO NOT CHANGE the sequence or naming —
the model weights are mapped to this specific input vector structure.

Feature mapping:
    1-4.   WWR: North, East, South, West
    5.     Age: Construction year
    6.     Orientation: North Angle
    7.     Floors: Number of Floors
    8-11.  U-Values: Ground, Wall, Roof, Window
    12-14. Geometry: Footprint [m²], Total Height [m], Volume [m³]
    15-16. Metrics: Relative Compactness [-], Characteristic Length [m]
    17.    Average: Window-to-Wall Ratio [-]
"""

from typing import Literal

import numpy as np
from pydantic import BaseModel


BuildingType = Literal["mfh", "sfh", "office"]
DemandType = Literal["heating", "cooling", "electricity", "dhw"]


class InputData(BaseModel):
    country: str
    city: str
    building_type: BuildingType
    demand_type: list[DemandType]
    length: float
    width: float
    floor_height: float
    number_of_floors: int
    construction_year: int
    north_angle: float
    nwwr: float
    ewwr: float
    swwr: float
    wwwr: float
    u_ground: float
    u_wall: float
    u_roof: float
    u_window: float

    @property
    def average_wwr(self) -> float:
        return (self.nwwr + self.ewwr + self.swwr + self.wwwr) / 4

    @property
    def footprint(self) -> float:
        return self.length * self.width

    @property
    def total_height(self) -> float:
        return self.floor_height * self.number_of_floors

    @property
    def volume(self) -> float:
        return self.footprint * self.total_height

    @property
    def surface_area(self) -> float:
        return 2 * ((self.width * self.length) + (self.width * self.total_height) + (self.length * self.total_height))

    @property
    def relative_compactness(self) -> float:
        # Relative compactness (RC) = (6 * volume^(2/3)) / surface_area
        return float((6 * (self.volume ** (2 / 3))) / self.surface_area)

    @property
    def characteristic_length(self) -> float:
        # Characteristic length (CL) = volume / surface area
        return self.volume / self.surface_area

    @property
    def ordered_features(self) -> np.ndarray:
        # NOTE: The order must stay the same!
        return np.array(
            [
                self.nwwr,
                self.ewwr,
                self.swwr,
                self.wwwr,
                self.construction_year,
                self.north_angle,
                self.number_of_floors,
                self.u_ground,
                self.u_wall,
                self.u_roof,
                self.u_window,
                self.footprint,
                self.total_height,
                self.volume,
                self.relative_compactness,
                self.characteristic_length,
                self.average_wwr,
            ]
        )
