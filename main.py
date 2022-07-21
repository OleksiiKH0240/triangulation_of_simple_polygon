from __future__ import annotations

from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np

from dataClasses.Point import Point
from dataClasses.Segment import Segment
from generate_pol1.generate_pol import generatePolygon
from interface import getPoints


def recognize_points(points: List[Point]) -> None:
    # points types: start_vertex, split_vertex, end_vertex, merge_vertex, regular_vertex
    n = len(points)
    for idx in range(len(points)):
        pt1_idx = idx
        pt0_idx = (pt1_idx - 1) % n
        pt2_idx = (pt1_idx + 1) % n
        vec1 = np.array([points[pt0_idx].x - points[pt1_idx].x, points[pt0_idx].y - points[pt1_idx].y])
        vec2 = np.array([points[pt2_idx].x - points[pt1_idx].x, points[pt2_idx].y - points[pt1_idx].y])
        pointAngle = np.round(calculate_angle(vec1, vec2), 2)
        points[pt1_idx].angle = pointAngle

        if points[pt1_idx].y > points[pt0_idx].y and points[pt1_idx].y > points[pt2_idx].y \
                and points[pt1_idx].angle < 180.0:
            points[pt1_idx].point_type = "start_vertex"
        elif points[pt1_idx].y > points[pt0_idx].y and points[pt1_idx].y > points[pt2_idx].y \
                and points[pt1_idx].angle > 180.0:
            points[pt1_idx].point_type = "split_vertex"
        elif points[pt1_idx].y < points[pt0_idx].y and points[pt1_idx].y < points[pt2_idx].y \
                and points[pt1_idx].angle < 180.0:
            points[pt1_idx].point_type = "end_vertex"
        elif points[pt1_idx].y < points[pt0_idx].y and points[pt1_idx].y < points[pt2_idx].y \
                and points[pt1_idx].angle > 180.0:
            points[pt1_idx].point_type = "merge_vertex"


def benchmark(func):
    import time
    def _benchmark(*args, **kw):
        t = time.time()
        res = func(*args, **kw)
        print('time elapsed:', time.time() - t)
        return res

    return _benchmark


def calculate_angle(vec1, vec2, direction: bool = True):
    """ Calculate angle between two points against direct of clock arrow
            A
                    C
              B
        angle(AB, AC) < 180
        angle(AC, AB) > 180
    """
    # ang_a = np.arctan2(*vec1[::-1])
    # ang_b = np.arctan2(*vec2[::-1])
    if direction is True:
        # clockwise direction
        return ((np.arctan2(vec2[1], vec2[0]) - np.arctan2(vec1[1], vec1[0])) % (2 * np.pi)) * 180 / np.pi
    # else:
    #     # counter-clockwise direction
    #     return ((np.arctan2(vec1[1], vec1[0]) - np.arctan2(vec2[1], vec2[0])) % (2 * np.pi)) * 180 / np.pi
    # return np.rad2deg((ang_b - ang_a) % (2 * np.pi))


@benchmark
def triangulate(points: List[Point], ptsX_sorted: List[Point], ptsY_sorted: List[Point],
                segments: List[Segment], drawMode: bool = False, mode: str = "simple"):
    vertices2del = points.copy()
    edges2del = set(segments.copy())
    externalEdges = set()
    idx = 0
    n = len(vertices2del)
    while True:
        if n == 3:
            break
        prevVertexIdx = (idx - 1) % n
        currVertexIdx = idx
        nextVertexIdx = (idx + 1) % n

        prevVertex = vertices2del[prevVertexIdx]
        currVertex = vertices2del[currVertexIdx]
        nextVertex = vertices2del[nextVertexIdx]
        if isEar(currVertex, prevVertex, nextVertex, edges2del, externalEdges, ptsX_sorted, ptsY_sorted, mode=mode,
                 drawMode=drawMode):
            # drawing
            if drawMode is True:
                draw(edges2del, vertices2del)
                currVertex.draw(color="red", mode="noAngle")
                plt.show()
            #

            cutSegment = Segment(prevVertex, nextVertex)
            segments.append(cutSegment)
            edges2del.add(cutSegment)

            # prevVertexIdx = prevVertexIdx % n
            doublePrevVertex = vertices2del[(prevVertexIdx - 1) % n]
            doubleNextVertex = vertices2del[(nextVertexIdx + 1) % n]

            #
            # update angles
            prevVertexAngle = round(
                calculate_angle(doublePrevVertex.toList() - prevVertex.toList(),
                                nextVertex.toList() - prevVertex.toList()), 2)
            vertices2del[prevVertexIdx].angle = prevVertexAngle

            nextVertexAngle = round(
                calculate_angle(prevVertex.toList() - nextVertex.toList(),
                                doubleNextVertex.toList() - nextVertex.toList()), 2)
            vertices2del[nextVertexIdx].angle = nextVertexAngle
            #
            #

            vertices2del.pop(currVertexIdx)
            n = len(vertices2del)

            sortedXIdx = bsearch_leftmost(ptsX_sorted, currVertex.x, mode="Xcoord")
            ptsX_sorted.pop(sortedXIdx)

            sortedYIdx = bsearch_leftmost(ptsY_sorted, currVertex.y, mode="Ycoord")
            ptsY_sorted.pop(sortedYIdx)

            edges2del.remove(Segment(prevVertex, currVertex))
            edges2del.remove(Segment(currVertex, nextVertex))
            idx -= 1



            # drawing
            if drawMode is True:
                draw(edges2del, vertices2del)
                plt.show()
            #

        idx += 1

        if idx == n:
            idx = 0


def isEar(point: Point, prev_point: Point, next_point: Point, edges: List[Segment], externalEdges: List[Segment],
          ptsX_sorted: List[Point], ptsY_sorted: List[Point], mode: str = "simple", drawMode: bool = False):
    if point.angle > 180.0:
        externalEdge = Segment(prev_point, next_point)
        externalEdges.add(externalEdge)
        return False
    seg = Segment(prev_point, next_point)
    state = seg in externalEdges

    if state: return False
    if "modified" in mode:
        region = getRegion([point, prev_point, next_point])
        rest_points = search_in_region(ptsX_sorted, ptsY_sorted, region)

        for pt in rest_points:
            if isInsideTriangle(point, prev_point, next_point, pt):
                # drawing
                if drawMode:
                    plt.plot(
                        [region[0][0], region[1][0], region[1][0], region[0][0], region[0][0]],
                        [region[0][1], region[0][1], region[1][1], region[1][1], region[0][1]])
                    for pt in rest_points:
                        plt.plot(pt.x, pt.y, "*", "yellow")
                    draw(edges)
                    point.draw(color="red", mode="NoAngle")
                    plt.show()
                #
                return False
        return True
    elif mode == "simple":
        for e in edges:
            if seg.intersect(e) is not None:
                return False
        return True


def draw(segments: List[Segment] = [], points: List[Point] = [], mode: str = "") -> None:
    # mode = "noAngle, noIdx, noPoint"
    for seg in segments:
        seg.draw()

    for pt in points:
        pt.draw(mode=mode)


# O(log(n)) complexity
def bsearch_leftmost(array, x, mode: str = "") -> int:
    """ Бінарний пошук для відшукання найпершого входження заданого числа
    :param mode: key for comparing.
    mode belong ['Xcoord' ,'Ycoord', '']
    :param array: Відсортований за неспаданням масив цілих чисел
    :param x:     Шукане число
    :return:      Номер шуканого елемента у масиві

    """
    left = 0  # ліва границя пошуку
    right = len(array)  # права границя пошуку
    while left < right:
        m = left + (right - left) // 2  # Середина
        condition = (mode == "" and array[m] < x) or \
                    (mode == "Xcoord" and array[m].x < x) or (mode == "Ycoord" and array[m].y < x)
        if condition:
            left = m + 1
        else:
            right = m

    return left


# O(log(n)) complexity
def bsearch_rightmost(array, x, mode: str) -> int:
    """ Бінарний пошук для відшукання останнього входження заданого числа
    :param mode: key for comparing.
    mode belong ['Xcoord' ,'Ycoord', '']
    :param array: Відсортований за неспаданням масив цілих чисел
    :param x:     Шукане число
    :return:      Номер шуканого елемента у масиві
    """
    left = 0  # ліва границя пошуку
    right = len(array)  # права границя пошуку
    while left < right:
        m = left + (right - left) // 2  # Середина
        condition = (mode == "" and array[m] < x) or \
                    (mode == "Xcoord" and array[m].x < x) or (mode == "Ycoord" and array[m].y < x)
        if condition:
            left = m + 1
        else:
            right = m

    return left - 1


# method analog of regions tree(J. V. Bentley, M.I. Shamos 1977)
def search_in_region(ptsX_sorted: List[Point], ptsY_sorted: List[Point],
                     region: List[Tuple[float, float], Tuple[float, float]]) -> List[Point]:
    # region = [(min_x, max_y), (max_x, min_y)]
    (min_x, max_y), (max_x, min_y) = region

    # Complexity{
    min_x_ptIdx = bsearch_leftmost(ptsX_sorted, min_x, mode="Xcoord")
    max_x_ptIdx = bsearch_rightmost(ptsX_sorted, max_x, mode="Xcoord")

    min_y_ptIdx = bsearch_leftmost(ptsY_sorted, min_y, mode="Ycoord")
    max_y_ptIdx = bsearch_rightmost(ptsY_sorted, max_y, mode="Ycoord")
    # } = O(log2(n))

    # filter with min, max y
    pts = ptsX_sorted[min_x_ptIdx: max_x_ptIdx + 1]
    pt: Point
    pts = [pt for pt in pts if min_y_ptIdx <= pt.sorted_YIdx <= max_y_ptIdx]

    return pts


# Barycentric coordinates on triangles
# https://mathworld.wolfram.com/TriangleInterior.html
def isInsideTriangle(pt0: Point, pt1: Point, pt2: Point, pt2detect: Point) -> bool:
    v0 = np.array([pt0.x, pt0.y], dtype=float)
    v1 = np.array([pt1.x - pt0.x, pt1.y - pt0.y], dtype=float)
    v2 = np.array([pt2.x - pt0.x, pt2.y - pt0.y], dtype=float)
    v = np.array([pt2detect.x, pt2detect.y], dtype=float)

    a = (np.cross(v, v2) - np.cross(v0, v2)) / np.cross(v1, v2)
    b = -(np.cross(v, v1) - np.cross(v0, v1)) / np.cross(v1, v2)

    return a > 0 and b > 0 and (a + b) < 1


def getRegion(pts: List[Point]) -> List[Tuple[float], Tuple[float]]:
    '''

    :param pts:
    :return: [(minX, maxY), (maxX, minY)]
    '''
    pt: Point
    minX = min(pts, key=lambda pt: pt.x).x
    maxX = max(pts, key=lambda pt: pt.x).x
    minY = min(pts, key=lambda pt: pt.y).y
    maxY = max(pts, key=lambda pt: pt.y).y
    return [(minX, maxY), (maxX, minY)]


def main(points: List[Tuple[float, float]], drawMode=False, mode: str = "simple"):
    # mode belongs ["simple", "modified"]
    min_x = min(points, key=lambda x: x[0])[0]
    max_x = max(points, key=lambda x: x[0])[0]
    min_y = min(points, key=lambda x: x[1])[1]
    max_y = max(points, key=lambda x: x[1])[1]

    points = [Point(*coords, str(idx)) for idx, coords in enumerate(points)]

    # quick sort complexity = O(n*log(n))
    ptsX_sorted = sorted(points.copy(), key=lambda pt: pt.x)
    ptsY_sorted = sorted(points.copy(), key=lambda pt: pt.y)
    #
    for idx, pt in enumerate(ptsX_sorted):
        pt: Point
        pt.sorted_XIdx = idx

    for idx, pt in enumerate(ptsY_sorted):
        pt: Point
        pt.sorted_YIdx = idx

    recognize_points(points)

    segmentsNumber = len(points)
    segments = [Segment(points[i % segmentsNumber], points[(i + 1) % segmentsNumber])
                # points[i % (segmentsNumber - 1)].label + "_" + points[(i + 1) % (segmentsNumber - 1)].label)
                for i in range(len(points))]

    draw(segments, points)
    plt.axis([min_x - 50, max_x + 50, min_y - 50, max_y + 50])
    plt.show()

    draw(segments, points, mode="noAngle, noIdx, noPoint")
    plt.show()

    triangulate(points, ptsX_sorted, ptsY_sorted, segments, drawMode=drawMode, mode=mode)

    # draw(segments, points, mode="noAngle")
    draw(segments, points, mode="noAngle, noIdx, noPoint")
    plt.axis([min_x - 50, max_x + 50, min_y - 50, max_y + 50])
    plt.show()


if __name__ == "__main__":
    mode = input("choose mode of program execution:"
                 "\n'1' - use program test data"
                 "\n'2' - input data manually using mouse"
                 "\n'3' - use random data"
                 "\n:")
    points: List = None
    if mode == "1":
        points = [(230, 544), (373, 690), (645, 700), (758, 333), (630, 151), (320, 60), (120, 240), (220, 369),
             (273, 180), (500, 186), (360, 300), (400, 440), (545, 246), (670, 344), (578, 529), (365, 503)]
        
        main(points, mode="modified", drawMode=False)
    # points = ((30, 50), (35, 47), (40, 50), (37, 43), (35, 35), (33, 43))

    # points = [(324.39, 653.14), (423.44, 586.48), (519.65, 636.0), (553.61, 437.9), (622.94, 418.86),
    #            (613.04, 316.0),
    #            (498.43, 357.9), (501.26, 197.9), (392.31, 272.19), (324.39, 194.1), (243.74, 289.33),
    #            (253.65, 481.71),
    #            (311.66, 397.9), (335.71, 525.52), (240.91, 597.9)]
    elif mode == "2":
        points = getPoints()
        main(points, mode="modified", drawMode=False)
    elif mode == "3":
        n = int(input("input number of simple polygon vertices, you want to randomize: "))
        yn = input("do you want to compare modified algorithm with basic ears cutting algorithm?{y/n}:")
        try:
            points = generatePolygon(ctrX=500, ctrY=500, aveRadius=n ** 2, irregularity=0.9, spikeyness=0.25,
                                     numVerts=n)[::-1]
            print("modified mode")
            main(points, mode="modified", drawMode=False)
        except Exception as e:
            print(e)
        if yn == "y":
            try:
                points = generatePolygon(ctrX=500, ctrY=500, aveRadius=n * 2, irregularity=0.9, spikeyness=0.25,
                                         numVerts=n)[::-1]
                print("simple mode:")
                main(points, mode="simple", drawMode=False)
            except Exception as e:
                print(e)

    #
    # for idx, n in enumerate([100] * 1):
    #     print(idx)
    #     try:
    #         points = generatePolygon(ctrX=500, ctrY=500, aveRadius=n ** 2, irregularity=0.7, spikeyness=0.3,
    #                                  numVerts=n)[::-1]
    #         main(points)
    #     except Exception as e:
    #         print(e)

    n = 80

    # try:
    #     points = generatePolygon(ctrX=500, ctrY=500, aveRadius=n * 2, irregularity=0.9, spikeyness=0.25,
    #                              numVerts=n)[::-1]
    #     print("simple mode:")
    #     main(points, mode="simple", drawMode=False)
    # except Exception as e:
    #     print(e)

    # try:
    #     # points = generatePolygon(ctrX=500, ctrY=500, aveRadius=n ** 2, irregularity=0.9, spikeyness=0.25,
    #     #                          numVerts=n)[::-1]
    #     print("modified mode")
    #     main(points, mode="modified", drawMode=True)
    # except Exception as e:
    #     print(e)
