from PIL import Image, ImageTk, ImageDraw, ImageColor
import math
import tkinter as tk

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

    def sub(self, point):
        return Point(self.x-point.x, self.y-point.y)

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


class Box():

    def __init__(self, x, y, offset):
        self.boundary = [Point(x-offset, y-offset), Point(x+offset, y-offset),
                         Point(x+offset, y+offset), Point(x-offset, y+offset)]

        self.box = [Point(x-offset, y-offset), Point(x+offset, y-offset),
                    Point(x+offset, y+offset), Point(x-offset, y+offset)]

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
            p_roof = self.box[i].sub(p_c)
            q_roof = self.boundary[i].sub(q_c)

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
            self.box[i] = self.box[i].sub(p_c).rotate(rotation).translate(q_c)


class Grid:

    iter = 0

    def __init__(self):

        self.grid = [
            [0, 0],
            [-1, 0]
        ]

        x = 250
        y = 250
        offset = 10
        width = 2*offset

        self.boxes = []

        b = 0
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                if cell >= 0:
                    pos_x = x + c*width
                    pos_y = y + r*width
                    print(pos_x, pos_y)
                    self.boxes.append(Box(pos_x, pos_y, offset))
                    self.grid[r][c] = b
                    b += 1

        # self.boxes = [Box(250, 250, 10), Box(270, 250, 10), Box(270, 270, 10)]
        self.vert = [
            [(0, 0)], [(0, 1), (1, 0)], [(1, 1)],
            [(0, 3)], [(0, 2), (1, 3), (2, 0)], [(1, 2), (2, 1)],
            [(2, 3)], [(2, 2)]
        ]  # point: [(box, corner)]

    def draw(self, canvas):
        for box in self.boxes:
            box.draw(canvas)

    def update(self, point):

        vertex = self.vert[self.iter]

        if vertex is not None:
            for corner in vertex:
                self.boxes[corner[0]].set_boundary(corner[1], point)

        self.iter = (self.iter + 1) % len(self.vert)

        if self.iter == 0:
            for box in self.boxes:
                box.fit()


def create_point(e):

    canvas.delete("all")
    grid.update(Point(e.x, e.y))
    grid.draw(canvas)


# load and open images
window = tk.Tk()

i_box = 0
i_corner = 0

canvas = tk.Canvas(window, width=500, height=500)
canvas.pack()
canvas.bind("<Button-1>", create_point)

grid = Grid()
grid.draw(canvas)

# pack
frame = tk.Frame(window)
frame.pack()

#

# window.protocol("WM_DELETE_WINDOW", windowClose)
window.mainloop()
