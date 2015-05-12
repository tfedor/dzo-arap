import numpy as np
from PIL import Image, ImageTk


class ImageHelper:

    HANDLE_RADIUS = 5

    def __init__(self, path):
        self._im_obj = Image.open(path)
        self._tk_obj = ImageTk.PhotoImage(self._im_obj)  # need to keep reference for image to load

        self._size = self._im_obj.size
        self.pos = (self.width/2, self.height/2)

        self._data = np.array(self._im_obj)
        self._changed = False

        # store original data of the image after load
        self._orig = np.array(self._im_obj)
        self._mask = None
        self._compute_mask()

        self._handles = set()

        self._canvas = None

    def setCanvas(self, canvas):
        self._canvas = canvas

    def _update(self):
        self._im_obj = Image.fromarray(self._data)  # putdata(self._data)
        self._tk_obj = ImageTk.PhotoImage(self._im_obj)  # need to keep reference for image to load

    def _is_foreground(self, px, lower, upper):
        return (px[0] < lower[0] or px[0] > upper[0]
             or px[1] < lower[1] or px[1] > upper[1]
             or px[2] < lower[2] or px[2] > upper[2])

    def _compute_mask(self):
        self._mask = np.full((self.height, self.width), True, dtype=np.bool)

        tolerance = 10
        empty = self._orig[0][0]

        # bounds
        lower = (min(255, empty[0] - tolerance), min(255, empty[1] - tolerance), min(255, empty[2] - tolerance))
        upper = (max(255, empty[0] + tolerance), max(255, empty[1] + tolerance), max(255, empty[2] + tolerance))

        queue = [(0, 0)]

        closed = {}
        for y in range(0, self.height):
            closed[y] = set()

        while len(queue) != 0:

            x, y = queue.pop()

            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                continue

            if x in closed[y]:
                continue

            closed[y].add(x)

            masked = self._is_foreground(self._orig[y][x], lower, upper)
            if not masked:
                self._mask[y][x] = False

                queue.append((x-1, y))
                queue.append((x+1, y))
                queue.append((x, y-1))
                queue.append((x, y+1))

    @property
    def cdata(self):
        return self._data.ctypes

    @property
    def corig(self):
        return self._orig.ctypes

    @property
    def cmask(self):
        return self._mask.ctypes

    def px(self, x, y, value):
        if 0 <= x < self.width and 0 <= y < self.height:
            self._changed = True
            self._data[y][x] = value

    def px_orig(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._orig[y][x]
        return 0, 0, 0

    def draw(self):
        #if not self._changed:
        #    return False

        self._canvas.delete("IMAGE")

        self._update()

        self._canvas.create_image(self.pos, image=self._tk_obj, tag="IMAGE")
        for h in self._handles:
            self._canvas.tag_raise(h)

        return True

    def select_handle(self, x, y):
        overlap = self._canvas.find_overlapping(x, y, x, y)
        for obj_id in overlap:
            if obj_id in self._handles:
                return obj_id

        return -1

    def create_handle(self, x, y):
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)

        overlap = self._canvas.find_overlapping(bbox[0], bbox[1], bbox[2], bbox[3])
        for obj_id in overlap:
            if obj_id in self._handles:
                return -1

        handle_id = self._canvas.create_oval(bbox, fill="blue", outline="blue", tag="HANDLE")
        self._handles.add(handle_id)
        return handle_id

    def move_handle(self, handle_id, x, y):
        bbox = (x-self.HANDLE_RADIUS, y-self.HANDLE_RADIUS, x+self.HANDLE_RADIUS, y+self.HANDLE_RADIUS)
        self._canvas.coords(handle_id, bbox)

    def remove_handle(self, handle_id):
        self._canvas.delete(handle_id)
        self._handles.remove(handle_id)

    @property
    def width(self):
        return self._size[0]

    @property
    def height(self):
        return self._size[1]

    @property
    def canvas(self):
        return self._canvas

    @property
    def orig(self):
        return self._orig
