from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PointScore:
    points_earned: int
    total_points: int

    def __post_init__(self):
        if self.points_earned < 0:
            raise ValueError("Points earned cannot be negative")
        if self.total_points <= 0:
            raise ValueError("Total points must be greater than zero")

    @property
    def percentage(self) -> float:
        return (self.points_earned / self.total_points) * 100.0
