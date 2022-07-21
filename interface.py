import numpy as np
from matplotlib import pyplot as plt


class PolygonBuilder:
    def __init__(self, line):
        self.line = line
        self.points = []
        self.xs = []
        self.ys = []
        self.cid = line.figure.canvas.mpl_connect('button_press_event', self.on_click)

    def on_click(self, event):
        if event.inaxes != self.line.axes: return
        if event.button == 1:
            point = (np.round(event.xdata, 2), np.round(event.ydata, 2))
            self.points.append(point)
            self.xs.append(point[0])
            self.ys.append(point[1])

            self.line.set_data(self.xs, self.ys)
        # elif event.button == 3:
        #     self.line.figure.canvas.mpl_disconnect(self.cid)
        #     try:
        #         plt.close(self.line.figure)
        #     except _tkinter.TclError:
        #         pass

        self.line.figure.canvas.draw()

    def getPoints(self):
        return self.points.copy()


def getPoints():
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.set_title('   Left click to choose points, \n \
                    Close this program window to plot triangulation')
    ax.axis([0, 1000, 0, 1000])
    line, = ax.plot([], [], marker="o", ms=10)  # empty line

    polygonBuilder = PolygonBuilder(line)
    plt.show()
    return polygonBuilder.getPoints()[:-1]



