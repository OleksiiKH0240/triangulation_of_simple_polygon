import math
import random


# https://ru.stackoverflow.com/questions/1380366/python-%D0%B3%D0%B5%D0%BD%D0%B5%D1%80%D0%B0%D1%82%D0%BE%D1%80-%D0%BC%D0%BD%D0%BE%D0%B3%D0%BE%D1%83%D0%B3%D0%BE%D0%BB%D1%8C%D0%BD%D0%B8%D0%BA%D0%BE%D0%B2-%D0%BF%D0%BE%D0%BB%D0%B8%D0%B3%D0%BE%D0%BD%D0%BE%D0%B2-%D0%BE%D1%81%D1%82%D1%80%D0%BE%D0%B2%D0%BE%D0%B2

def generatePolygon(ctrX, ctrY, aveRadius, irregularity, spikeyness, numVerts):
    '''

    :param ctrX: coordinate x of the "centre" of the polygon
    :param ctrY: coordinate y of the "centre" of the polygon
    :param aveRadius: in px, the average radius of this polygon, this roughly controls how large the polygon is,
    really only useful for order of magnitude.
    :param irregularity: [0,1] indicating how much variance there is in the angular spacing of vertices.
    [0,1] will map to [0, 2pi/numberOfVerts]
    :param spikeyness: [0,1] indicating how much variance there is in each vertex from the circle of radius aveRadius.
    [0,1] will map to [0, aveRadius]
    :param numVerts: self-explanatory
    :return: a list of vertices, in CCW order.
    '''
    irregularity = clip(irregularity, 0, 1) * 2 * math.pi / numVerts
    spikeyness = clip(spikeyness, 0, 1) * aveRadius

    # generate n angle steps
    angleSteps = []
    lower = (2 * math.pi / numVerts) - irregularity
    upper = (2 * math.pi / numVerts) + irregularity
    sum = 0
    for i in range(numVerts):
        tmp = random.uniform(lower, upper)
        angleSteps.append(tmp)
        sum = sum + tmp

    # normalize the steps so that point 0 and point n+1 are the same
    k = sum / (2 * math.pi)
    for i in range(numVerts):
        angleSteps[i] = angleSteps[i] / k

    # now generate the points
    points = []
    angle = random.uniform(0, 2 * math.pi)
    for i in range(numVerts):
        r_i = clip(random.gauss(aveRadius, spikeyness), 0, 2 * aveRadius)
        x = ctrX + r_i * math.cos(angle)
        y = ctrY + r_i * math.sin(angle)
        points.append((int(x), int(y)))

        angle = angle + angleSteps[i]

    return points


def clip(x, min, max):
    if min > max:
        return x
    elif x < min:
        return min
    elif x > max:
        return max
    else:
        return x


if __name__ == "__main__":
    print(generatePolygon(ctrX=500, ctrY=500, aveRadius=100, irregularity=0.5, spikeyness=0.5, numVerts=20))
