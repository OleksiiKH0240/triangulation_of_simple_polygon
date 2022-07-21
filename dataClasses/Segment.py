from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union
import matplotlib.pyplot as plt
import numpy as np

from dataClasses.Point import Point


@dataclass
class Segment:
    a: Point
    b: Point
    label: str = ""
    helper: Point = None

    eps = 0.00999

    def draw(self, color: str = "green") -> None:
        x = [self.a.x, self.b.x]
        y = [self.a.y, self.b.y]
        plt.plot(x, y, color)

    def intersect(self, other: Segment) -> Union[Point, Segment, None]:
        equation1 = self.to_equation()
        equation2 = other.to_equation()
        matrix = np.array([equation1, equation2])
        X: np.array = matrix[:, :-1]
        B: np.array = -1 * matrix[:, -1]
        X_det = np.linalg.det(X)
        intersect_point: Point
        if X_det != 0:
            intersect_point_coords = kramer(X, B)

            intersect_point = Point(*intersect_point_coords)
            # print("before rounded", point)
            intersect_point.round_coords()
            # print("after rounded", point)
            is_in_segs = []
            for seg in [self, other]:
                is_in_segs.append(seg.is_inside(intersect_point))

                # is_in_segs.append(x_cond and y_cond)
            if all(is_in_segs):
                return intersect_point
            return None
        else:
            intersect_pts = []

            for pt in [self.a, self.b]:
                if other.is_inside(pt):
                    intersect_pts.append(pt)

            for pt in [other.a, other.b]:
                if self.is_inside(pt):
                    intersect_pts.append(pt)
            if len(intersect_pts) == 2:
                return Segment(*intersect_pts)
            elif len(intersect_pts) == 1:
                print("bullshit in Segment class, intersect method")

    def is_inside(self, point: Point) -> bool:
        is_in_seg = []
        min_x, min_y, max_x, max_y = self.min_max_coords()
        x_cond = (min_x < point.x < max_x)
        # x_cond = (min_x <= point.x <= max_x)
        if min_x == max_x:
            x_cond = (abs(point.x - min_x) < self.eps)
            # x_cond = (point.x == min_x)

        y_cond = (min_y < point.y < max_y)
        # y_cond = (min_y <= point.y <= max_y)
        if min_y == max_y:
            y_cond = (abs(point.y - min_y) < self.eps)
            # y_cond = (point.y == min_y)

        is_in_seg.append(x_cond and y_cond)

        equation = self.to_equation()
        eqResult = equation[0] * point.x + equation[1] * point.y + equation[2]
        equation_cond = (abs(eqResult) < self.eps)
        is_in_seg.append(equation_cond)

        return all(is_in_seg)

    def min_max_coords(self) -> list:
        """

        :return: [min_x, min_y, max_x, max_y]
        """
        min_x = min([self.a.x, self.b.x])
        min_y = min([self.a.y, self.b.y])
        max_x = max([self.a.x, self.b.x])
        max_y = max([self.a.y, self.b.y])
        return [min_x, min_y, max_x, max_y]

    def to_equation(self) -> np.array:
        """
        equation: Ax + By + C = 0
        :return:
        """
        x_coeff = -1 * (self.b.y - self.a.y)
        y_coeff = (self.b.x - self.a.x)
        free_coeff = x_coeff * -self.a.x + y_coeff * -self.a.y
        return np.array([x_coeff, y_coeff, free_coeff], dtype=float)

    def __eq__(self, other):
        return (self.a == other.a and self.b == other.b) or (self.a == other.b and self.b == other.a)

    def __hash__(self):
        return hash(hash(self.a) * hash(self.b))




def kramer(x_matrix: List[List], b_vector: List) -> List:
    det_0 = np.linalg.det(x_matrix)
    assert det_0 != 0
    result_vector = []
    for j in range(len(x_matrix)):
        matrix_j = x_matrix.copy()
        matrix_j[:, j] = b_vector
        x_i = np.linalg.det(matrix_j) / det_0
        result_vector.append(x_i)
    return result_vector

if __name__ == "__main__":
    pt1 = Point(230, 544)
    pt2 = Point(373, 690)
    seg1 = Segment(pt1, pt2)
    seg2 = Segment(pt2, pt1)
    print(seg1 == seg2)