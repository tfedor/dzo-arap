from PIL import Image, ImageTk, ImageDraw, ImageColor, ImagePath
import math
import tkinter as tk
import numpy as np


class Point():
    """ Embedding lattice point with defined position, neighbourhood and search area """

    w = 1

    def __init__(self, x, y, w=1):
        self.pos = [x, y]
        self.linked = []
        self.w = w

    @property
    def weight(self):
        return self.w

    @weight.setter
    def weight(self, value):
        self.w = value

    @property
    def x(self):
        return self.pos[0]

    @x.setter
    def x(self, value):
        self.pos[0] = value

    @property
    def y(self):
        return self.pos[1]

    @y.setter
    def y(self, value):
        self.pos[1] = value

    @property
    def coor(self):
        return self.pos[0], self.pos[1]

    def copy(self):
        return Point(self.x, self.y, self.weight)

    def sub(self, point):
        self.x -= point.x
        self.y -= point.y
        return self

    def rotate(self, rotation):
        x = rotation[0][0] * self.x + rotation[1][0] * self.y
        y = rotation[0][1] * self.x + rotation[1][1] * self.y
        self.x = x
        self.y = y
        return self

    def translate(self, translation):
        self.x += translation.x
        self.y += translation.y
        return self

    def link(self, other):
        self.linked.append(other)

    def average_linked(self):
        x = 0
        y = 0
        for point in self.linked:
            x += point.x
            y += point.y

        x /= len(self.linked)
        y /= len(self.linked)

        self.x = x
        self.y = y


class Box():

    def __init__(self, b_tl, b_tr, b_br, b_bl):
        self.boundary = [b_tl, b_tr, b_br, b_bl]
        self.box = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary[0].link(self.box[0])
        self.boundary[1].link(self.box[1])
        self.boundary[2].link(self.box[2])
        self.boundary[3].link(self.box[3])

    def draw(self, canvas, color="red"):

        # canvas.create_line(self.box[0].coor, self.box[1].coor, fill="blue")
        # canvas.create_line(self.box[1].coor, self.box[2].coor, fill="blue")
        # canvas.create_line(self.box[2].coor, self.box[3].coor, fill="blue")
        # canvas.create_line(self.box[3].coor, self.box[0].coor, fill="blue")

        canvas.create_line(self.boundary[0].coor, self.boundary[1].coor, fill=color)
        canvas.create_line(self.boundary[1].coor, self.boundary[2].coor, fill=color)
        canvas.create_line(self.boundary[2].coor, self.boundary[3].coor, fill=color)
        canvas.create_line(self.boundary[3].coor, self.boundary[0].coor, fill=color)

    def set_boundary(self, corner, point):
        self.boundary[corner] = point

    @property
    def centroid_box(self):
        return Point((self.box[0].x + self.box[1].x + self.box[2].x + self.box[3].x) / 4,
                     (self.box[0].y + self.box[1].y + self.box[2].y + self.box[3].y) / 4)

    @property
    def centroid_boundary(self):
        return Point((self.boundary[0].x + self.boundary[1].x + self.boundary[2].x + self.boundary[3].x) / 4,
                     (self.boundary[0].y + self.boundary[1].y + self.boundary[2].y + self.boundary[3].y) / 4)

    def fit(self):

        p_c = self.centroid_box
        q_c = self.centroid_boundary

        rotation = [[0, 0], [0, 0]]
        mi_1 = 0
        mi_2 = 0
        for i in range(0, 4):
            p_roof = self.box[i].copy().sub(p_c)
            q_roof = self.boundary[i].copy().sub(q_c)

            rotation[0][0] += self.boundary[i].weight * (p_roof.x * q_roof.x + p_roof.y * q_roof.y)
            rotation[0][1] += self.boundary[i].weight * (p_roof.x * q_roof.y - p_roof.y * q_roof.x)
            rotation[1][0] += self.boundary[i].weight * (p_roof.y * q_roof.x - p_roof.x * q_roof.y)
            rotation[1][1] += self.boundary[i].weight * (p_roof.y * q_roof.y + p_roof.x * q_roof.x)

            mi_1 += self.boundary[i].weight * (q_roof.x * p_roof.x + q_roof.y * p_roof.y)
            mi_2 += self.boundary[i].weight * (q_roof.x * p_roof.y - q_roof.y * p_roof.x)

        mi = math.sqrt(mi_1**2 + mi_2**2)

        rotation[0][0] /= mi
        rotation[0][1] /= mi
        rotation[1][0] /= mi
        rotation[1][1] /= mi

        for i, point in enumerate(self.box):
            self.box[i].sub(p_c).rotate(rotation).translate(q_c)











class Homography:

    def __init__(self, source, target):

        A = []
        B = []
        for i, s in enumerate(source):
            t = target[i]
            A.append([s.x, s.y, 1, 0, 0, 0, -s.x*t.x, -s.y*t.x])
            A.append([0, 0, 0, s.x, s.y, 1, -s.x*t.y, -s.y*t.y])

            B.append(t.x)
            B.append(t.y)

        h = np.linalg.solve(np.array(A), np.array(B))

        self.fwdH = np.array([[h[0], h[1], h[2]], [h[3], h[4], h[5]], [h[6], h[7], 1]])
        self.H = np.linalg.inv(self.fwdH)

        lines = Line()
        lines.add(target[0].x, target[0].y, target[1].x, target[1].y)
        lines.add(target[1].x, target[1].y, target[2].x, target[2].y)
        lines.add(target[2].x, target[2].y, target[3].x, target[3].y)
        lines.add(target[3].x, target[3].y, target[0].x, target[0].y)
        self.borders = lines.stack


    def project(self, imdata):

        data = [(0,0,0)]*(600*500)
        for y, r in self.borders.items():
            for x in range(r[0], r[1]):
                res = np.dot(self.H, [x, y, 1])

                xn = round((res[0]/res[2]))
                yn = round((res[1]/res[2]))

                # bilinear

                idx = int(yn)*600 + int(xn)
                if idx < 0 or idx > len(imdata)-1:
                    # data.append((0, 0, 0))
                    pass
                else:
                    data[y*600+x] = imdata[idx]
                    # data.append(imdata[idx])

        return data


class Line:
    """
    Bresenham's line
    http://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    """

    def __init__(self):
        self.stack = dict()
        self.res = []

    def add(self, x0, y0, x1, y1):

        self.res = []

        dx = abs(x1-x0)
        dy = abs(y1-y0)

        if dx > dy:
            for x, y in self.points(x0, y0, x1, y1):
                self.res.append((x, y))

                if y not in self.stack:
                    self.stack[y] = (x, x)
                else:
                    self.stack[y] = (min(self.stack[y][0], x), max(self.stack[y][1], x))
        else:
            for y, x in self.points(y0, x0, y1, x1):
                self.res.append((x, y))

                if y not in self.stack:
                    self.stack[y] = (x, x)
                else:
                    self.stack[y] = (min(self.stack[y][0], x), max(self.stack[y][1], x))


    def points(self, x0, y0, x1, y1):

        dx = abs(x1-x0)
        dy = abs(y1-y0)

        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0

        if y1 < y0:
            x0, y0, x1, y1 = x0, -y0, x1, -y1

        D = 2*dy - dx

        yield abs(x0), abs(y0)

        y = y0
        for x in range(x0+1, x1):
            D += 2*dy
            if D > 0:
                y += 1
                D -= 2*dx

            yield abs(x), abs(y)

    # def paint(self, imdata, color):
    #     for x, y in self.res:
    #         imdata[y*600+x] = color


srcCounter = 0
srcPoints = [Point(0, 0), Point(600, 0), Point(600, 500), Point(0, 500)]
tgtCounter = 0
tgtPoints = [Point(0, 0), Point(0, 0), Point(0, 0), Point(0, 0)]

def set_src_point(e):
    global srcCounter
    srcPoints[srcCounter] = Point(e.x, e.y)
    srcCounter = (srcCounter + 1) % 4

    if srcCounter == 0:
        b = Box(srcPoints[0], srcPoints[1], srcPoints[2], srcPoints[3])
        b.draw(canvas, color="red")


def set_tgt_point(e):
    global tgtCounter
    tgtPoints[tgtCounter] = Point(e.x, e.y)
    tgtCounter = (tgtCounter + 1) % 4

    if tgtCounter == 0:
        b = Box(tgtPoints[0], tgtPoints[1], tgtPoints[2], tgtPoints[3])
        b.draw(canvas, color="blue")


def compute_homography(e):
    h = Homography(srcPoints, tgtPoints)

    im.putdata(h.project(imdata))
    canvas.delete("all")

    cont.ref = ImageTk.PhotoImage(im)
    canvas.create_image((300, 250), image=cont.ref)

    print("DONE")


class Container:
    ref = None




cont = Container()

# load and open images
window = tk.Tk()

im = Image.open("assets/taz.jpg")

canvas = tk.Canvas(window, width=600, height=500)
canvas.bind("<Button-1>", set_src_point)
canvas.bind("<Button-3>", set_tgt_point)
canvas.bind("<Button-2>", compute_homography)
canvas.pack()

imdata = list(im.getdata())

# Line(300, 250, 400, 300).paint(imdata, (255, 0, 0))
# Line(300, 250, 400, 200).paint(imdata, (0, 255, 0))
# Line(300, 250, 200, 300).paint(imdata, (255, 0, 0))
# Line(300, 250, 200, 200).paint(imdata, (0, 255, 0))
#
# Line(300, 250, 350, 150).paint(imdata, (255, 0, 0))
# Line(300, 250, 350, 350).paint(imdata, (0, 255, 0))
# Line(300, 250, 250, 150).paint(imdata, (255, 0, 0))
# Line(300, 250, 250, 350).paint(imdata, (0, 255, 0))

im.putdata(imdata)


bitmap = ImageTk.PhotoImage(im)

canvas.create_image((300, 250), image=bitmap)


# pack
frame = tk.Frame(window)
frame.pack()

#

# window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
