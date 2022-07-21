from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union, Tuple
import matplotlib.pyplot as plt
import numpy as np


@dataclass
class Point:
    x: float
    y: float
    label: str = ""
    point_type: str = "regular_vertex"
    sorted_XIdx: int = -1
    sorted_YIdx: int = -1
    angle: float = 0
    eps = 10 ** -5  # 10 ** -5
    digits_round_numb = 6  # 5

    def round_coords(self):
        rounded_x = round(self.x, self.digits_round_numb)
        # if abs(self.x - rounded_x) < self.eps:
        #     self.x = rounded_x
        self.x = rounded_x

        rounded_y = round(self.y, self.digits_round_numb)
        # if abs(self.y - rounded_y) < self.eps:
        #     self.y = rounded_y
        self.y = rounded_y

    def toList(self):
        return np.array([self.x, self.y])

    def draw(self, color: str = "blue", mode: str = "") -> None:
        # print("noIdx" in mode)
        if not("noIdx" in mode):
            plt.annotate(self.label, [self.x, self.y])
        if not("noAngle" in mode):
            plt.annotate(str(self.angle) + "°", [self.x, self.y - 20])
        # plt.annotate(self.point_type, [self.x, self.y - 40])
        if not("noPoint" in mode):
            plt.plot(self.x, self.y, "*", color=color)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(tuple([self.x, self.y]))
