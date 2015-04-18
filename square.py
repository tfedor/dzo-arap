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

    def draw(self, canvas):

        # canvas.create_line(self.box[0].coor, self.box[1].coor, fill="blue")
        # canvas.create_line(self.box[1].coor, self.box[2].coor, fill="blue")
        # canvas.create_line(self.box[2].coor, self.box[3].coor, fill="blue")
        # canvas.create_line(self.box[3].coor, self.box[0].coor, fill="blue")

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


class Grid:

    iter = 0
    id = None

    def __init__(self, canvas):

        self.canvas = canvas

        self.points = [
            Point(180, 240), Point(200, 240), Point(220, 240),  Point(240, 240), Point(260, 240), Point(280, 240), Point(300, 240), Point(320, 240), Point(340, 240),
            Point(180, 260), Point(200, 260), Point(220, 260),  Point(240, 260), Point(260, 260), Point(280, 260), Point(300, 260), Point(320, 260), Point(340, 260),
            Point(180, 280), Point(200, 280), Point(220, 280),  Point(240, 280), Point(260, 280), Point(280, 280), Point(300, 280), Point(320, 280), Point(340, 280),
            Point(180, 300), Point(200, 300), Point(220, 300),  Point(240, 300), Point(260, 300), Point(280, 300), Point(300, 300), Point(320, 300), Point(340, 300),
        ]

        # self.handle = self.points[4]
        self.handle = self.points[13]
        self.handle.weight = 1000
        self.handle_target = self.handle.copy()

        for p in self.points:
            p.weight = self.handle.weight - (abs(self.handle.x - p.x) + abs(self.handle.y - p.y)*10)

        self.boxes = [
            Box(self.points[0], self.points[1], self.points[10], self.points[9]),
            Box(self.points[1], self.points[2], self.points[11], self.points[10]),
            Box(self.points[2], self.points[3], self.points[12], self.points[11]),
            Box(self.points[3], self.points[4], self.points[13], self.points[12]),
            Box(self.points[4], self.points[5], self.points[14], self.points[13]),
            Box(self.points[5], self.points[6], self.points[15], self.points[14]),
            Box(self.points[6], self.points[7], self.points[16], self.points[15]),
            Box(self.points[7], self.points[8], self.points[17], self.points[16]),

            Box(self.points[9], self.points[10], self.points[19], self.points[18]),
            Box(self.points[10], self.points[11], self.points[20], self.points[19]),
            Box(self.points[11], self.points[12], self.points[21], self.points[20]),
            Box(self.points[12], self.points[13], self.points[22], self.points[21]),
            Box(self.points[13], self.points[14], self.points[23], self.points[22]),
            Box(self.points[14], self.points[15], self.points[24], self.points[23]),
            Box(self.points[15], self.points[16], self.points[25], self.points[24]),
            Box(self.points[16], self.points[17], self.points[26], self.points[25]),

            Box(self.points[18], self.points[19], self.points[28], self.points[27]),
            Box(self.points[19], self.points[20], self.points[29], self.points[28]),
            Box(self.points[20], self.points[21], self.points[30], self.points[29]),
            Box(self.points[21], self.points[22], self.points[31], self.points[30]),
            Box(self.points[22], self.points[23], self.points[32], self.points[31]),
            Box(self.points[23], self.points[24], self.points[33], self.points[32]),
            Box(self.points[24], self.points[25], self.points[34], self.points[33]),
            Box(self.points[25], self.points[26], self.points[35], self.points[34])
        ]

    def draw(self):
        self.canvas.delete("all")
        for box in self.boxes:
            box.draw(self.canvas)

    def regularize(self):
        for box in self.boxes:
            box.fit()

        for vertex in self.points:
            vertex.average_linked()

    def set_handle_target(self, point):
        self.handle_target = point

    def run_once(self):
        if self.handle_target is not None:
            self.handle.x = self.handle_target.x
            self.handle.y = self.handle_target.y
            # self.handle_target = None

        self.regularize()
        self.draw()

    def run(self):
        self.run_once()
        self.id = self.canvas.after(1, lambda: self.run())

    def stop(self):
        if self.id is not None:
            self.canvas.after_cancel(self.id)
            self.id = None

    def update(self, point):

        self.points[2].x = point.x
        self.points[2].y = point.y

        # vertex = self.points[self.iter]
        #
        # if vertex is not None:
        #     vertex.x = point.x
        #     vertex.y = point.y
        #
        # self.iter = (self.iter + 1) % len(self.points)
        #
        # if self.iter == 0:
        #     self.regularize()

        self.draw()


def set_target(e):
    grid.stop()
    grid.set_handle_target(Point(e.x, e.y))
    grid.run()


def release_target(e):
    # grid.stop()
    pass


def create_point(e):
    grid.stop()
    grid.set_handle_target(Point(e.x, e.y))
    grid.run_once()


def run_once(e):
    grid.run_once()

# load and open images
window = tk.Tk()

reg_callback = None

canvas = tk.Canvas(window, width=500, height=500)
canvas.pack()
canvas.bind("<Button-1>", set_target)
canvas.bind("<B1-Motion>", set_target)
canvas.bind("<ButtonRelease-1>", release_target)

canvas.bind("<Button-2>", create_point)
canvas.bind("<Button-3>", run_once)

grid = Grid(canvas)
grid.draw()

# pack
frame = tk.Frame(window)
frame.pack()

#

# window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
