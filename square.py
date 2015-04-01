from PIL import Image, ImageTk, ImageDraw, ImageColor
import math
import tkinter as tk
import time

SEARCH_SIZE = 48
SEARCH_OFFSET = SEARCH_SIZE/2


class ImageWidget():

    def __init__(self, parent):

        self.image = None
        self.data = []

        self.image = tk.Canvas(self.label, width=500, height=500)
        #self.label.image = canvas
        self.label.pack()

    def bind(self, event, callback):
        self.label.bind(event, callback)

    def update(self, image):
        self.image = image
        self.data = list(self.image.getdata())

    def redraw(self):
        photo = ImageTk.PhotoImage(self.image)
        self.label.configure(image=photo)
        self.label.image = photo

    def clear_overlay(self):
        self.image.putdata(self.data)

    def px(self, x, y):
        return self.data[y * self.image.size[0] + x]

    def draw_box(self, x, y, offset, color):

        draw = ImageDraw.Draw(self.image)
        draw.rectangle([(x-offset, y-offset),
                        (x+offset, y+offset)], outline=color)

    def draw_line(self, start, end, color=(255, 0, 255), width=1):
        draw = ImageDraw.Draw(self.image)
        draw.line([start, end], fill=color, width=width)


class Point():
    """ Embedding lattice point with defined position, neighbourhood and search area """

    def __init__(self, x, y):
        self.pos = [x, y]
        self.linked = []

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
        return Point(self.x, self.y)

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

        for point in self.linked:
            point.x = x
            point.y = y


class Box():

    def __init__(self, b_tl, b_tr, b_br, b_bl):
        self.boundary = [b_tl, b_tr, b_br, b_bl]
        self.box = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary[0].link(self.box[0])
        self.boundary[1].link(self.box[1])
        self.boundary[2].link(self.box[2])
        self.boundary[3].link(self.box[3])

    def draw(self, canvas):

        canvas.create_line(self.box[0].coor, self.box[1].coor, fill="blue")
        canvas.create_line(self.box[1].coor, self.box[2].coor, fill="blue")
        canvas.create_line(self.box[2].coor, self.box[3].coor, fill="blue")
        canvas.create_line(self.box[3].coor, self.box[0].coor, fill="blue")

        canvas.create_line(self.boundary[0].coor, self.boundary[1].coor, fill="red")
        canvas.create_line(self.boundary[1].coor, self.boundary[2].coor, fill="red")
        canvas.create_line(self.boundary[2].coor, self.boundary[3].coor, fill="red")
        canvas.create_line(self.boundary[3].coor, self.boundary[0].coor, fill="red")

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

            rotation[0][0] += (p_roof.x * q_roof.x + p_roof.y * q_roof.y)
            rotation[0][1] += (p_roof.x * q_roof.y - p_roof.y * q_roof.x)
            rotation[1][0] += (p_roof.y * q_roof.x - p_roof.x * q_roof.y)
            rotation[1][1] += (p_roof.y * q_roof.y + p_roof.x * q_roof.x)

            mi_1 += q_roof.x * p_roof.x + q_roof.y * p_roof.y
            mi_2 += q_roof.x * p_roof.y - q_roof.y * p_roof.x

        mi = math.sqrt(mi_1**2 + mi_2**2)

        rotation[0][0] /= mi
        rotation[0][1] /= mi
        rotation[1][0] /= mi
        rotation[1][1] /= mi

        for i, point in enumerate(self.box):
            self.box[i].sub(p_c).rotate(rotation).translate(q_c)


class Grid:

    iter = 0
    id = None

    def __init__(self, canvas):

        self.canvas = canvas

        self.points = [
            Point(240, 240), Point(260, 240), Point(280, 240), Point(300, 240), Point(320, 240),
            Point(240, 260), Point(260, 260), Point(280, 260), Point(300, 260), Point(320, 260),
            Point(240, 280), Point(260, 280), Point(280, 280), Point(300, 280), Point(320, 280),
        ]

        self.boxes = [
            Box(self.points[0], self.points[1], self.points[6], self.points[5]),
            Box(self.points[1], self.points[2], self.points[7], self.points[6]),
            Box(self.points[2], self.points[3], self.points[8], self.points[7]),
            Box(self.points[3], self.points[4], self.points[9], self.points[8]),

            Box(self.points[5], self.points[6], self.points[11], self.points[10]),
            Box(self.points[6], self.points[7], self.points[12], self.points[11]),
            Box(self.points[7], self.points[8], self.points[13], self.points[12]),
            Box(self.points[8], self.points[9], self.points[14], self.points[13])
        ]

    def draw(self):
        for box in self.boxes:
            box.draw(self.canvas)

    def regularize(self):
        for box in self.boxes:
            box.fit()

        for vertex in self.points:
            vertex.average_linked()

        self.canvas.delete("all")
        self.draw()

        self.id = self.canvas.after(200, lambda: self.regularize())

    def stop_regularize(self):
        if self.id is not None:
            self.canvas.after_cancel(self.id)
            self.id = None

    def update(self, point):

        vertex = self.points[self.iter]

        if vertex is not None:
            vertex.x = point.x
            vertex.y = point.y

        self.iter = (self.iter + 1) % len(self.points)

        if self.iter == 0:
            self.regularize()

        self.draw()


def create_point(e):

    grid.stop_regularize()

    canvas.delete("all")
    grid.update(Point(e.x, e.y))


# load and open images
window = tk.Tk()

reg_callback = None

canvas = tk.Canvas(window, width=500, height=500)
canvas.pack()
canvas.bind("<Button-1>", create_point)

grid = Grid(canvas)
grid.draw()

# pack
frame = tk.Frame(window)
frame.pack()

#

# window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
