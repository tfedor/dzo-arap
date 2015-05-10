import numpy as np
from PIL import Image, ImageTk

class ImageHelper:

    HANDLE_RADIUS = 5

    def __init__(self, canvas, pos, path):
        self.__canvas = canvas
        self.pos = pos

        self.__im_obj = Image.open(path)
        self.__tk_obj = ImageTk.PhotoImage(self.__im_obj)  # need to keep reference for image to load

        self.__size = self.__im_obj.size

        self._data = np.array(self.__im_obj)
        self._changed = False

        # store original data of the image after load
        self._orig = np.array(self.__im_obj)

        self._handles = set()

    def _update(self):
        self.__im_obj = Image.fromarray(self._data)  # putdata(self._data)
        self.__tk_obj = ImageTk.PhotoImage(self.__im_obj)  # need to keep reference for image to load

    @property
    def cdata(self):
        return self._data.ctypes

    @property
    def corig(self):
        return self._orig.ctypes

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

        self.__canvas.delete("IMAGE")

        self._update()

        self.__canvas.create_image(self.pos, image=self.__tk_obj, tag="IMAGE")
        for h in self._handles:
            self.__canvas.tag_raise(h)

        return True

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
        return self._orig
