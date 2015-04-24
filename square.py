import datetime
import math
import pprint
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import time
import asyncio


class Line:
    """
    Bresenham's line
    http://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    """

    def __init__(self):
        self.stack = dict()
        self.res = []

    def addp(self, p1, p2):
        self.add(p1.x, p1.y, p2.x, p2.y)

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

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)


class Box():

    def __init__(self, b_tl, b_tr, b_br, b_bl):
        # initial position of a box, used for modifying image
        self.__initial = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary = [b_tl, b_tr, b_br, b_bl]

        #
        self._rigid = [b_tl.copy(), b_tr.copy(), b_br.copy(), b_bl.copy()]

        self.boundary[0].link(self._rigid[0])
        self.boundary[1].link(self._rigid[1])
        self.boundary[2].link(self._rigid[2])
        self.boundary[3].link(self._rigid[3])

        lines = Line()
        lines.addp(b_tl, b_tr)
        lines.addp(b_tr, b_br)
        lines.addp(b_br, b_bl)
        lines.addp(b_bl, b_tl)
        self.__rasterized = lines.stack

    def has_point(self, x, y):
        if y in self.__rasterized:
            left, right = self.__rasterized[y]
            return left <= x <= right
        return False

    def draw(self, canvas):

        # canvas.create_line(self.box[0].coor, self.box[1].coor, fill="blue")
        # canvas.create_line(self.box[1].coor, self.box[2].coor, fill="blue")
        # canvas.create_line(self.box[2].coor, self.box[3].coor, fill="blue")
        # canvas.create_line(self.box[3].coor, self.box[0].coor, fill="blue")

        canvas.create_line(self.boundary[0].coor, self.boundary[1].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[1].coor, self.boundary[2].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[2].coor, self.boundary[3].coor, fill="red", tag="GRID")
        canvas.create_line(self.boundary[3].coor, self.boundary[0].coor, fill="red", tag="GRID")

    def set_boundary(self, corner, point):
        self.boundary[corner] = point

    def get_closest_boundary(self, x, y):
        min_ = -1
        closest = None
        for b in self.boundary:
            dist = abs(b.x - x) + abs(b.y - y)
            if min_ == -1 or dist < min_:
                min_ = dist
                closest = b
        return closest

    @property
    def centroid_box(self):
        return Point((self._rigid[0].x + self._rigid[1].x + self._rigid[2].x + self._rigid[3].x) / 4,
                     (self._rigid[0].y + self._rigid[1].y + self._rigid[2].y + self._rigid[3].y) / 4)

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
            p_roof = self._rigid[i].copy().sub(p_c)
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

        for i, point in enumerate(self._rigid):
            self._rigid[i].sub(p_c).rotate(rotation).translate(q_c)


class Grid:

    iter = 0
    id = None

    def __init__(self, image):

        BOX_SIZE = 16

        self.__image = image
        self.__points = {}
        self.__boxes = []

        imdata = self.__image.orig
        bg = imdata[0, 0]

        # find borders of image
        top = self.__border(bg, imdata)
        btm = self.__image.height - self.__border(bg, imdata[::-1])
        lft = self.__border(bg, imdata.T)
        rgt = self.__image.width - self.__border(bg, imdata.T[::-1])

        width = rgt-lft
        height = btm-top

        box_count = (int(math.ceil(width/BOX_SIZE)), int(math.ceil(height/BOX_SIZE)))
        box_x = lft - int((box_count[0] * BOX_SIZE - width) / 2)
        box_y = top - int((box_count[1] * BOX_SIZE - height) / 2)

        for y in range(box_y, btm, BOX_SIZE):
            for x in range(box_x, rgt, BOX_SIZE):
                if -1 != self.__border(bg, imdata[y:y+BOX_SIZE:1, x:x+BOX_SIZE:1]):
                    self.__boxes.append(
                        Box(
                            self.__add_point(x, y),
                            self.__add_point(x+BOX_SIZE, y),
                            self.__add_point(x+BOX_SIZE, y+BOX_SIZE),
                            self.__add_point(x, y+BOX_SIZE)
                        )
                    )

        self._controls = {}

    def __border(self, empty, data):
        """
        :param empty: rgb tuple which represents empty space
        :param data: image data to go through
        :return: row number in which the first non-empty pixel was found, -1 if all pixels are empty
        """
        nonempty = 0
        stop = False
        for row in data:
            i = 0
            for rgb in row:
                if rgb != empty:
                    stop = True
                    break
                i += 1
            if stop:
                break
            nonempty += 1

        if not stop:
            return -1
        return nonempty

    def __add_point(self, x, y):
        if y in self.__points:
            if x not in self.__points[y]:
                self.__points[y][x] = Point(x, y)
        else:
            self.__points[y] = {}
            self.__points[y][x] = Point(x, y)

        return self.__points[y][x]

    def create_control_point(self, handle_id, x, y):
        for box in self.__boxes:
            if box.has_point(x, y):

                control = box.get_closest_boundary(x, y)
                control.weight = 1000000

                # controls[handle_id] = (point, target_pos, handle offset)
                self._controls[handle_id] = [control, (control.x, control.y), (control.x - x, control.y - y)]

                return True

        return False

    def remove_control_point(self, handle_id):
        if handle_id in self._controls:
            self._controls[handle_id][0].weight = 1
            del self._controls[handle_id]

    def set_control_target(self, handle_id, x, y):
        dx, dy = self._controls[handle_id][2]
        self._controls[handle_id][1] = (x+dx, y+dy)

    def draw(self):
        self.__image.canvas.delete("GRID")

        for box in self.__boxes:
            box.draw(self.__image.canvas)

    def regularize(self):
        for handle_id in self._controls:
            control = self._controls[handle_id]
            control[0].x = control[1][0]
            control[0].y = control[1][1]

        for box in self.__boxes:
            box.fit()

        for y in self.__points:
            for x in self.__points[y]:
                self.__points[y][x].average_linked()


class ImageHelper:

    HANDLE_RADIUS = 5

    def __init__(self, canvas, pos, path):
        self.__canvas = canvas
        self.pos = pos

        self.__im_obj = Image.open(path)
        self.__tk_obj = ImageTk.PhotoImage(self.__im_obj)  # need to keep reference for image to load

        self.__size = self.__im_obj.size
        self.__orig = self.get_data()  # store original data of the image after load

        self._handles = set()

    def get_data(self):
        """ return current image data ((r, g, b) tuples) as numpy's 2-dimensional array """
        data = self.__im_obj.getdata()
        return np.array(data, dtype='u1,u1,u1').reshape((self.height, self.width))

    def draw(self):
        self.__canvas.delete("IMAGE")
        self.__canvas.create_image(self.pos, image=self.__tk_obj, tag="IMAGE")
        for h in self._handles:
            self.__canvas.tag_raise(h)

    def select_handle(self, x, y):
        overlap = self.__canvas.find_overlapping(x, y, x, y)
        for obj_id in overlap:
            if obj_id in self._handles:
                return obj_id

        return -1

    def create_handle(self, x, y):
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)

        overlap = self.__canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3])
        for obj_id in overlap:
            if obj_id in self._handles:
                return -1

        handle_id = self.__canvas.create_oval(bbox, fill="blue", outline="blue", tag="HANDLE")
        self._handles.add(handle_id)
        return handle_id

    def move_handle(self, handle_id, x, y):
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)
        self.__canvas.coords(handle_id, bbox)

    def remove_handle(self, handle_id):
        self.__canvas.delete(handle_id)
        self._handles.remove(handle_id)

    @property
    def width(self):
        return self.__size[0]

    @property
    def height(self):
        return self.__size[1]

    @property
    def canvas(self):
        return self.__canvas

    @property
    def orig(self):
        return self.__orig


class Application:

    def __init__(self, width, height):
        self.window = tk.Tk()

        self.width = width
        self.height = height

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        self.image = None
        self.grid = None

        self._active_handle = -1

        self._loop = None

    def load_image(self, path):

        self.image = ImageHelper(self.canvas, (self.width/2, self.height/2), path)
        self.image.draw()

    def bind(self, event, fn):
        self.canvas.bind(event, fn)

    def run(self):
        self.grid = Grid(self.image)
        self.grid.draw()

        self._loop = self.window.after(1, self.run_once)

        self.window.mainloop()

    def run_once(self):
        self.grid.regularize()
        self.grid.draw()

        self._loop = self.window.after(1, self.run_once)



    def select_handle(self, e):
        handle_id = self.image.select_handle(e.x, e.y)

        if handle_id == -1:
            handle_id = self.image.create_handle(e.x, e.y)
            if handle_id != -1:
                if not self.grid.create_control_point(handle_id, e.x, e.y):
                    self.image.remove_handle(e.x, e.y)
                    return False
            else:
                return False

        self._active_handle = handle_id
        return True

    def deselect_handle(self, e):
        self._active_handle = -1

    def remove_handle(self, e):
        handle_id = self.image.select_handle(e.x, e.y)
        if handle_id != -1:
            self.grid.remove_control_point(handle_id)
            self.image.remove_handle(handle_id)

    def move_handle(self, e):
        if self._active_handle != -1:
            self.image.move_handle(self._active_handle, e.x, e.y)
            self.grid.set_control_target(self._active_handle, e.x, e.y)


app = Application(600, 500)
app.load_image("assets/taz.jpg")

app.bind("<Button-1>", app.select_handle)
app.bind("<ButtonRelease-1>", app.deselect_handle)
app.bind("<Button-3>", app.remove_handle)
app.bind("<B1-Motion>", app.move_handle)
app.bind("<Button-2>", app.run_once)

app.run()

